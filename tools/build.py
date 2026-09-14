#!/usr/bin/env python3
"""Static generator for the Labs site. Dev-only: tools/ is excluded from the
deploy by .vercelignore.

    python3 tools/build.py

Writes index.html, 404.html, vercel.json (every build's short link, such as
/ridelens, is one of its redirects), sitemap.xml, robots.txt and
assets/js/labs-data.js, the ⌘K palette index.

The design system, the interaction layer and the story engine are the
portfolio's own: assets/css/site.css, assets/js/site.js and tools/stories.py come
from johnjayasankar.com, so the two sites read as one. The build refuses to
finish on an em or en dash, a link, anchor or ARIA reference that resolves
nowhere, a story whose steps do not match its phases, or a duplicate id."""

import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import data as D  # noqa: E402
import stories  # noqa: E402
import labs_stories  # noqa: E402,F401  registers AgentFit, Cartonry, KeepFloor and Pricing Hub

S = D.SITE
H = D.HOME
DOM = S['domain']
EMAIL = S['email']
BUILDS = D.BUILDS
BY = {b['slug']: b for b in BUILDS}
FEATURED = [b for b in BUILDS if b['featured']]
ALSO = [b for b in BUILDS if not b['featured']]
ROUTES = {b['route'] for b in BUILDS}
LASTMOD = '2026-09-14'
NEWTAB = '<span class="sr-only"> (opens in a new tab)</span>'
V = {}


def icon(cls, body, size=16):
    return ('<svg class="ico %s" viewBox="0 0 16 16" width="%d" height="%d" aria-hidden="true" focusable="false">%s</svg>'
            % (cls, size, size, body))


STROKE = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
ARROW = icon('ico--arrow', '<path d="M3 8h9.5M8.5 4l4 4-4 4" %s/>' % STROKE)
EXTI = icon('ico--ext', '<path d="M5 4.5h6.5V11M11.5 4.5l-7 7" %s/>' % STROKE)
CHEV = icon('ico--chev', '<path d="M4.5 6.5 8 10l3.5-3.5" %s/>' % STROKE, 12)
SEARCH = icon('ico--search', '<circle cx="7" cy="7" r="4.4" fill="none" stroke="currentColor" stroke-width="1.5"/>'
                             '<path d="m10.4 10.4 3.1 3.1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>', 15)
UP = icon('ico--up', '<path d="M8 13V3.5M4 7.5l4-4 4 4" %s/>' % STROKE)


# ----------------------------------------------------------------------------
# helpers, the same ones the portfolio's generator uses
# ----------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s), quote=True)


def mval(v):
    """A figure or heading. The arrow in '4 → 1' is drawn, and read as 'to'."""
    return esc(v).replace('→', '<i class="to" aria-hidden="true">→</i><span class="sr-only"> to </span>')


def render(tpl, **kw):
    def sub(m):
        key = m.group(1)
        if key not in kw:
            raise KeyError('missing template value: ' + key)
        return str(kw[key])
    return re.sub(r'\{\{(\w+)\}\}', sub, tpl)


def fingerprint(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return 'dev'
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:10]


def img_v(rel):
    """An asset URL stamped with its content hash, so a redeploy never serves a stale file."""
    return '/%s?v=%s' % (rel, fingerprint(rel))


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    return rel


def is_ext(href):
    return href.startswith('http')


def link(label_html, href, cls='', arrow=False):
    """Off-site links open in a new tab, and say so."""
    c = ' class="%s"' % cls if cls else ''
    if is_ext(href):
        return '<a%s href="%s" target="_blank" rel="noopener">%s%s%s</a>' % (c, esc(href), label_html, EXTI, NEWTAB)
    return '<a%s href="%s">%s%s</a>' % (c, esc(href), label_html, ARROW if arrow else '')


def btn(label, href, kind='primary', size='', arrow=None):
    cls = 'btn btn--' + kind + ((' btn--' + size) if size else '')
    if arrow is None:
        arrow = not is_ext(href) and not href.startswith('mailto:')
    return link('<span>%s</span>' % esc(label), href, cls, arrow)


def tlink(label, href, cls='tlink'):
    return link('<span>%s</span>' % esc(label), href, cls, True)


def hint(text):
    return '<p class="hint" data-kbd>%s</p>' % esc(text)


def slabel(n, text, dark=False):
    num = '<span class="slabel__n">%s</span>' % esc(n) if n else ''
    return '<p class="slabel%s">%s<span class="slabel__t">%s</span></p>' % (' slabel--dark' if dark else '', num, esc(text))


def heading(parts, hid, level='h2', cls='h2'):
    """A two-tone heading: the second clause is set in the quieter tone."""
    if isinstance(parts, (tuple, list)):
        inner = '%s <span class="tone">%s</span>' % (mval(parts[0]), mval(parts[1]))
    else:
        inner = mval(parts)
    return '<%s class="%s" id="%s">%s</%s>' % (level, cls, hid, inner, level)


NUM = re.compile(r'\d+(?:\.\d+)?')


def count_attr(v):
    """Figures with one plain number count up when they arrive."""
    s = str(v)
    if '→' in s:
        return ''
    nums = NUM.findall(s)
    if len(nums) != 1 or re.search(r'[A-Za-z]', s.split(nums[0], 1)[0]):
        return ''
    return ' data-count'


KEEP = re.compile(r'(<[^>]+>)|(?<![\w-])(\w+(?:-\w+)+)(?![\w-])')


def keep(s):
    """Hyphenated compounds such as end-to-end stay on one line in display type."""
    return KEEP.sub(lambda m: m.group(1) or '<span class="nw">%s</span>' % m.group(2), s)


def stat(v, k, cls='stat'):
    return '<li class="%s"><b class="stat__v"%s>%s</b><span class="stat__k">%s</span></li>' % (cls, count_attr(v), mval(v), esc(k))


def rd(i):
    return ' style="--rd:%d"' % i


# ----------------------------------------------------------------------------
# chrome
# ----------------------------------------------------------------------------
HEAD = """<!doctype html>
<html lang="en" data-page="{{page}}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{{title}}</title>
<meta name="description" content="{{desc}}">
<link rel="canonical" href="{{url}}">
<meta name="author" content="John Jayasankar">
<meta name="robots" content="{{robots}}">
<meta name="theme-color" content="#f8f6f1">
<meta property="og:site_name" content="John Jayasankar · Labs">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="website">
<meta property="og:title" content="{{title}}">
<meta property="og:description" content="{{ogdesc}}">
<meta property="og:url" content="{{url}}">
<meta property="og:image" content="{{ogimg}}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{{ogalt}}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{title}}">
<meta name="twitter:description" content="{{ogdesc}}">
<meta name="twitter:image" content="{{ogimg}}">
<meta name="twitter:image:alt" content="{{ogalt}}">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/inter-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/site.css?v={{v}}">
{{ld}}</head>
"""

CHROME = """<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"><i data-scrollbar></i></div>
<header class="hdr" data-hdr>
  <div class="hdr__bar">
    <a class="brand" href="/" aria-label="John Jayasankar Labs, home"><span class="orb" aria-hidden="true"></span><span class="brand__name">John Jayasankar</span><span class="brand__tag">Labs</span></a>
    <nav class="hdr__nav" aria-label="Primary">{{nav}}<span class="nav__hl" aria-hidden="true"></span></nav>
    <div class="hdr__tools">
      <button class="kbtn" type="button" data-cmdk aria-label="Search the builds and jump anywhere" aria-keyshortcuts="Meta+K Control+K">{{search}}<span class="kbtn__k"><span data-modkey>⌘</span>K</span></button>
      {{portfolio}}
      <a class="btn btn--primary btn--sm hdr__cta" href="mailto:{{email}}"><span>Email me</span></a>
      <button class="menu" type="button" aria-expanded="false" aria-controls="drawer" data-menu><span class="sr-only">Menu</span><i></i><i></i></button>
    </div>
  </div>
  <div class="drawer" id="drawer" data-drawer hidden>
    <nav class="drawer__nav" aria-label="Site menu">{{drawer}}</nav>
    <div class="drawer__tools"><a class="btn btn--primary" href="mailto:{{email}}"><span>Email me</span></a>{{dportfolio}}<button class="btn btn--ghost" type="button" data-cmdk><span>Search</span><span class="kbtn__k"><span data-modkey>⌘</span>K</span></button></div>
  </div>
</header>
"""

FOOTER = """<footer class="ftr">
  <div class="ftr__card" data-spot>
    <div class="stripes stripes--ftr" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <div class="ftr__in">
      <div class="ftr__grid">
        <div class="ftr__id">
          <a class="brand brand--light" href="/" aria-label="John Jayasankar Labs, home"><span class="orb" aria-hidden="true"></span><span class="brand__name">John Jayasankar</span><span class="brand__tag brand__tag--dark">Labs</span></a>
          <p class="ftr__role">Independent products · {{city}}</p>
          <p class="ftr__quote">{{note}}</p>
          <div class="ftr__cta"><a class="btn btn--mint" href="mailto:{{email}}"><span>Email me</span>{{arrow}}</a>{{portfolio}}</div>
        </div>
        <nav class="ftr__col" aria-label="Labs"><p class="ftr__h">Labs</p>{{labs}}</nav>
        <nav class="ftr__col" aria-label="Featured builds"><p class="ftr__h">Featured</p>{{featured}}</nav>
        <nav class="ftr__col" aria-label="Also shipped"><p class="ftr__h">Also shipped</p>{{also}}</nav>
        <nav class="ftr__col" aria-label="Elsewhere"><p class="ftr__h">Elsewhere</p>{{elsewhere}}</nav>
      </div>
      <p class="ftr__word ftr__word--labs" aria-hidden="true">Labs<span>.</span></p>
      <div class="ftr__base"><span>© {{year}} John Jayasankar</span><span class="ftr__locus" data-locus-label>{{label}}</span><span>{{city}}<span class="ftr__clock" data-clock hidden></span></span></div>
    </div>
  </div>
</footer>
"""

TOTOP = '<button class="totop" type="button" data-totop aria-label="Back to top">%s</button>\n' % UP

OVERLAYS = TOTOP + """<div class="toast" role="status" aria-live="polite" data-toast></div>
<div class="gchip" data-gchip hidden><p data-gchip-text></p><button type="button" data-gchip-close>Got it</button></div>
<div class="cmdk" data-cmdk-root hidden>
  <div class="cmdk__scrim" data-cmdk-close></div>
  <div class="cmdk__panel" role="dialog" aria-modal="true" aria-labelledby="cmdk-title">
    <p class="sr-only" id="cmdk-title">Jump to a build</p>
    <div class="cmdk__bar">
      <span class="cmdk__glyph" aria-hidden="true">""" + SEARCH + """</span>
      <input class="cmdk__input" data-cmdk-input type="text" role="combobox" aria-expanded="true" aria-controls="cmdk-list" aria-autocomplete="list" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="RideLens, Daylight, AgentFit, or type ? for keys">
      <button class="cmdk__esc" type="button" data-cmdk-close>Esc</button>
    </div>
    <ul class="cmdk__list" id="cmdk-list" role="listbox" aria-label="Results" data-cmdk-list></ul>
    <p class="cmdk__foot" aria-hidden="true"><span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>Enter</kbd> open</span><span><kbd>Esc</kbd> close</span></p>
  </div>
</div>
"""


def mega(base):
    def col(title, items):
        links = ''.join('<a class="mega__link" href="%s"><span class="mega__name">%s</span><span class="mega__m">%s · %s</span></a>'
                        % (b['route'], esc(b['name']), b['n'], esc(b['line'])) for b in items)
        return '<div class="mega__col"><p class="mega__h">%s</p>%s</div>' % (esc(title), links)
    lead = ('<div class="mega__lead"><p class="mega__h">Overview</p>'
            '<a class="mega__big" href="%s#featured"><span>All builds</span><small>%02d live · %02d featured</small></a>'
            '<a class="mega__big" href="%s#rules"><span>What they share</span><small>The rule each build keeps</small></a>'
            '<a class="mega__card" href="%s" target="_blank" rel="noopener"><img src="%s" alt="" width="640" height="400" loading="lazy" decoding="async">'
            '<span class="mega__card-t">Portfolio</span><small>Case studies for the featured builds</small>%s</a></div>') % (
        base, len(BUILDS), len(FEATURED), base, esc(S['portfolio']), img_v('assets/img/portfolio.jpg'), NEWTAB)
    return ('<div class="mega mega--labs" id="mega-builds" data-mega-panel><div class="mega__grid mega__grid--labs">%s%s%s</div></div>'
            % (lead, col('Featured', FEATURED), col('Also shipped', ALSO)))


def chrome_top(base):
    nav = ('<div class="nav__item" data-mega><a class="nav__link" href="%s#featured">Builds</a>'
           '<button class="nav__more" type="button" aria-expanded="false" aria-controls="mega-builds" data-mega-btn>'
           '<span class="sr-only">Show every build</span>%s</button>%s</div>') % (base, CHEV, mega(base))
    nav += '<a class="nav__link" href="%s#also">Also shipped</a><a class="nav__link" href="%s#rules">What they share</a>' % (base, base)
    nav += link('<span>Writing</span>', S['substack'], 'nav__link')
    items = [('Builds', base + '#featured'), ('Also shipped', base + '#also'), ('What they share', base + '#rules'),
             ('Writing', S['substack']), ('Portfolio', S['portfolio'])]
    drawer = ''.join(link('<span>%s</span>' % esc(label), href, 'drawer__link', arrow=True) for label, href in items)
    return render(CHROME, nav=nav, drawer=drawer, search=SEARCH, email=EMAIL,
                  portfolio=btn('Portfolio', S['portfolio'], 'ghost', 'sm').replace('class="btn btn--ghost btn--sm"', 'class="btn btn--ghost btn--sm hdr__resume"'),
                  dportfolio=btn('Portfolio', S['portfolio'], 'ghost'))


def footer(label, base):
    labs = ''.join('<a href="%s">%s</a>' % (base + h, esc(l)) for l, h in (('All builds', '#featured'), ('Also shipped', '#also'),
                                                                          ('What they share', '#rules')))
    featured = ''.join('<a href="%s">%s</a>' % (b['route'], esc(b['name'])) for b in FEATURED)
    also = ''.join('<a href="%s">%s</a>' % (b['route'], esc(b['name'])) for b in ALSO)
    elsewhere = (link('<span>Portfolio</span>', S['portfolio']) + link('<span>Writing</span>', S['substack'])
                 + link('<span>LinkedIn</span>', S['linkedin']) + '<a href="mailto:%s">Email</a>' % EMAIL)
    return render(FOOTER, year=S['year'], label=esc(label), note=esc(S['note']), email=EMAIL, arrow=ARROW, city=esc(S['city']),
                  portfolio=btn('Portfolio', S['portfolio'], 'night'), labs=labs, featured=featured, also=also, elsewhere=elsewhere)


def scripts():
    return ('<script src="/assets/js/labs-data.js?v=%s" defer></script>\n'
            '<script src="/assets/js/site.js?v=%s" defer></script>\n') % (V['data'], V['site'])


def ld_block(ld):
    if not ld:
        return ''
    return '<script type="application/ld+json">%s</script>\n' % json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')


def shell(page, path, title, desc, label, body, base='', robots='index, follow', ld=None):
    return ''.join([
        render(HEAD, page=page, title=esc(title), desc=esc(desc), url=esc(DOM + path), robots=robots,
               ogdesc=esc(S['og_description']), ogimg=esc(DOM + img_v(S['og_image'].lstrip('/'))), ogalt=esc(S['og_alt']),
               v=V['css'], ld=ld_block(ld)),
        '<body data-label="%s">\n' % esc(label),
        chrome_top(base),
        '<main id="main" tabindex="-1">\n', body, '</main>\n',
        footer(label, base),
        OVERLAYS,
        scripts(),
        '</body>\n</html>\n',
    ])


# ----------------------------------------------------------------------------
# the bay: a build's story with its phase controls, exactly as on the portfolio
# ----------------------------------------------------------------------------
TELE = ('<p class="tele" aria-hidden="true"><span class="tele__dot"></span><span data-bay-phase>{{i}} / {{n}}</span>'
        '<span data-bay-state>Auto</span></p>')

BAY_COMPACT = """<figure class="bay bay--compact" id="{{hid}}" data-bay aria-label="{{title}}">
{{screen}}
<div class="bay__ctl"><div class="bay__tabs" role="group" aria-label="{{title}}: phases">{{tabs}}</div>{{tele}}</div>
<figcaption class="bay__cap"><span class="bay__note" data-bay-note>{{cap0}}</span><span class="bay__foot">{{foot}}</span><span class="sr-only" aria-live="polite" data-bay-live></span></figcaption>
</figure>
"""

BAY_STEPS = """<figure class="bay bay--steps" id="{{hid}}" data-bay aria-labelledby="{{hid}}-t">
<div class="bay__main">
<div class="bay__head"><div class="bay__id"><p class="bay__t" id="{{hid}}-t">{{title}}</p><p class="bay__s">{{sub}}</p></div><p class="bay__big"><b>{{big}}</b>{{bigsub}}</p></div>
{{screen}}
<p class="bay__foot">{{foot}}</p>
</div>
<figcaption class="bay__side">
<p class="bay__side-h"><span>Phases</span><span class="bay__keys">1-{{n}} · select to hold</span></p>
<ol class="bay__steps" aria-label="{{title}}: phases">{{items}}</ol>
<p class="bay__read"><span class="bay__read-k">{{readk}}</span>{{readt}}</p>
<div class="bay__status">{{tele}}<span class="rail" aria-hidden="true">{{ticks}}<i class="rail__play" data-bay-play></i></span></div>
<span class="sr-only" aria-live="polite" data-bay-live></span>
</figcaption>
</figure>
"""

BAY_STEP = ('<li><button type="button" class="step" data-stop="{{stop}}" data-caption="{{cap}}" aria-pressed="{{pressed}}">'
            '<span class="step__n" aria-hidden="true">{{num}}</span><span class="step__body"><span class="step__l">{{label}}</span>'
            '<span class="step__t">{{txt}}</span></span><span class="step__prog" aria-hidden="true"><i data-prog></i></span></button></li>')


def bay(hid, b, variant='compact'):
    """Phases sit evenly around the story's clock, and the page is written at the
    story's resting phase, so controls, caption and picture agree before any script."""
    phases = b['phases']
    n = len(phases)
    st = stories.STORIES[b['slug']]
    assert st['n'] == n, 'story %s has %d steps for %d phases' % (b['slug'], st['n'], n)
    rest = st['rest']
    stops = [(i + .5) / n for i in range(n)]
    B = b['bay']
    screen = stories.render(b['slug'])
    tele = render(TELE, i='%02d' % (rest + 1), n='%02d' % n)
    if variant == 'steps':
        ticks = ''.join('<i class="rail__tick" style="left:%.1f%%"></i>' % (stop * 100) for stop in stops)
        items = ''.join(render(BAY_STEP, stop='%g' % stops[i], cap=esc(cap), pressed='true' if i == rest else 'false',
                               num='%02d' % (i + 1), label=esc(tab), txt=esc(cap)) for i, (tab, cap) in enumerate(phases))
        kind, _, text = st['label'].partition(': ')
        return render(BAY_STEPS, hid=hid, title=esc(B['title']), sub=esc(B['sub']), big=mval(B['big']),
                      bigsub=('<span>%s</span>' % mval(B['big_sub'])) if B['big_sub'] else '', screen=screen, foot=esc(B['foot']),
                      n=n, items=items, tele=tele, ticks=ticks,
                      readk=esc('Reading the %s interface' % kind.split(' ')[0].lower()), readt=esc(text[0].upper() + text[1:]))
    tabs = ''.join('<button type="button" class="ptab" data-stop="%g" data-caption="%s" aria-pressed="%s">'
                   '<span class="ptab__n" aria-hidden="true">%d</span><span class="ptab__l">%s</span>'
                   '<span class="ptab__prog" aria-hidden="true"><i data-prog></i></span></button>'
                   % (stops[i], esc(cap), 'true' if i == rest else 'false', i + 1, esc(tab)) for i, (tab, cap) in enumerate(phases))
    return render(BAY_COMPACT, hid=hid, title=esc(B['title']), screen=screen, tabs=tabs, tele=tele,
                  cap0=esc(phases[rest][1]), foot=esc(B['foot']))


def open_links(b, cls='tlink'):
    out = link('<span>Open %s</span>' % esc(b['name']), b['route'], cls, True)
    if b.get('case'):
        out += link('<span>Case study</span>', b['case'], 'tlink tlink--quiet')
    return out


# ----------------------------------------------------------------------------
# home
# ----------------------------------------------------------------------------
HERO_TPL = """<section class="hero" id="top" data-locus data-label="Top" aria-labelledby="hero-h">
  <div class="hero__in wrap">
    <p class="badge hero__badge"><span class="badge__dot" aria-hidden="true"></span>{{badge}}<span class="badge__clock" data-clock hidden></span></p>
    <h1 class="hero__h1" id="hero-h"><span class="hero__line">{{h1a}}</span> <span class="hero__line tone">{{h1b}}</span></h1>
    <p class="hero__lede">{{lede}}</p>
    <div class="actions hero__actions">{{actions}}</div>
    <ul class="hero__career" aria-label="The bench">{{meta}}</ul>
  </div>
  <div class="hero__stage">
    <div class="stripes" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
    <div class="wrap hero__show">{{show}}</div>
    <div class="wrap proof"><ul class="proof__grid" aria-label="The bench, in numbers">{{proof}}</ul></div>
  </div>
</section>
"""

LABFEAT_TPL = """<article class="labfeat{{rev}}" id="{{slug}}" data-locus data-label="{{name}}" data-href="{{route}}" aria-labelledby="{{slug}}-h">
  <div class="wrap labfeat__grid">
    <div class="labfeat__copy" data-reveal>
      <p class="labfeat__k"><span class="labfeat__n">{{n}}</span> / {{cat}}</p>
      <h3 class="labfeat__h" id="{{slug}}-h">{{name}}</h3>
      <p class="labfeat__tag">{{line}}</p>
      <p class="labfeat__blurb">{{blurb}}</p>
      <ul class="ticks">{{does}}</ul>
      <ul class="stats stats--row">{{stats}}</ul>
      <div class="actions">{{actions}}</div>
    </div>
    <div class="labfeat__bay" data-reveal style="--rd:1">{{bay}}</div>
  </div>
</article>
"""

LABCARD_TPL = """<article class="labcard" id="{{slug}}" data-locus data-label="{{name}}" data-href="{{route}}" aria-labelledby="{{slug}}-h" data-reveal{{rd}}>
  <a class="labcard__screen" href="{{route}}" tabindex="-1" aria-hidden="true">{{story}}</a>
  <div class="labcard__body">
    <p class="labcard__k"><span>{{n}}</span> / {{tag}}</p>
    <h3 class="labcard__h" id="{{slug}}-h"><a href="{{route}}">{{name}}</a></h3>
    <p class="labcard__tag">{{line}}</p>
    <p class="labcard__p">{{blurb}}</p>
    <ul class="labcard__stats">{{metrics}}</ul>
    <p class="labcard__phases" aria-hidden="true">{{phases}}</p>
    <p class="labcard__links">{{open}}</p>
  </div>
</article>
"""


def showcase():
    tabs, panels = [], []
    for i, (key, tab, slug) in enumerate(H['show']):
        b = BY[slug]
        sel = i == 0
        tabs.append('<button type="button" class="seg__btn show__tab" role="tab" id="show-tab-%s" aria-controls="show-%s" '
                    'aria-selected="%s" tabindex="%s" data-show-tab><span class="show__tl show__tl--long">%s</span><span class="show__ts">%s</span>'
                    '<span class="show__fill" aria-hidden="true"><i></i></span></button>'
                    % (key, key, 'true' if sel else 'false', '0' if sel else '-1', esc(tab), esc(H['show_short'][key])))
        panels.append('<div class="show__panel" role="tabpanel" id="show-%s" aria-labelledby="show-tab-%s"%s>%s<p class="show__more">%s</p></div>'
                      % (key, key, '' if sel else ' hidden', bay('bay-show-' + key, b, 'steps'), open_links(b)))
    return ('<div class="show" data-show data-reveal><div class="show__bar"><div class="seg" role="tablist" aria-label="Range, one bench" data-seg>%s'
            '<span class="seg__ind" aria-hidden="true"></span></div></div><div class="show__panels">%s</div></div>') % (
        ''.join(tabs), ''.join(panels))


def home():
    actions = btn('See the builds', '#featured', 'primary', 'lg') + btn('Portfolio', S['portfolio'], 'ghost', 'lg')
    meta = ''.join('<li>%s</li>' % esc(x) for x in H['meta'])
    proof = ''.join('<li class="proof__item"><a href="%s"><b class="proof__v"%s>%s</b><span class="proof__k">%s</span></a></li>'
                    % (h, count_attr(v), mval(v), esc(k)) for v, k, h in H['proof'])
    hero = render(HERO_TPL, badge=esc(H['badge']), h1a=keep(mval(H['h1'][0])), h1b=keep(mval(H['h1'][1])), lede=esc(H['lede']),
                  actions=actions, meta=meta, show=showcase(), proof=proof)

    F = H['featured']
    rows = []
    for i, b in enumerate(FEATURED):
        acts = btn('Open ' + b['name'], b['route'], 'primary')
        if b.get('case'):
            acts += btn('Case study', b['case'], 'ghost')
        rows.append(render(LABFEAT_TPL, rev=' labfeat--rev' if i % 2 else '', slug=b['slug'], name=esc(b['name']), route=b['route'],
                           n=b['n'], cat=esc(b['cat']), line=esc(b['line']), blurb=esc(b['blurb']),
                           does=''.join('<li>%s</li>' % esc(x) for x in b['does']),
                           stats=''.join(stat(v, k) for v, k in b['stats']), actions=acts, bay=bay('bay-' + b['slug'], b, 'compact')))
    featured = ('<section class="sect sect--feat" id="featured" data-locus data-label="Featured" aria-labelledby="featured-h">'
                '<div class="wrap"><div class="shead shead--center" data-reveal>%s%s</div></div>%s</section>\n') % (
        slabel(F['n'], F['kicker']), heading(F['h2'], 'featured-h'), ''.join(rows))

    A = H['also']
    cards = []
    for i, b in enumerate(ALSO):
        rest = stories.STORIES[b['slug']]['rest']
        phases = ' <span class="wrow__arr">→</span> '.join('<span data-phase="%d"%s>%s</span>' % (j, ' class="is-cur"' if j == rest else '', esc(p[0]))
                                                          for j, p in enumerate(b['phases']))
        metrics = ''.join('<li><b>%s</b><span>%s</span></li>' % (mval(v), esc(k)) for v, k in b['stats'])
        cards.append(render(LABCARD_TPL, slug=b['slug'], name=esc(b['name']), route=b['route'], rd=rd(i % 2), n=b['n'], tag=esc(b['tag']),
                            story=stories.render(b['slug'], attrs=' data-thumb data-autoplay'), line=esc(b['line']), blurb=esc(b['blurb']),
                            metrics=metrics, phases=phases, open=link('<span>Open %s</span>' % esc(b['name']), b['route'], 'tlink', True)))
    # the same dark band the portfolio gives Labs on its home page
    also = ('<section class="sect labsband" id="also" data-locus data-label="Also shipped" aria-labelledby="also-h"><div class="labsband__card" data-spot><div class="wrap">'
            '<div class="shead shead--center shead--dark" data-reveal>%s%s</div><div class="labgrid labgrid--2">%s</div></div></div></section>\n') % (
        slabel(A['n'], A['kicker'], dark=True), heading(A['h2'], 'also-h'), ''.join(cards))

    R = H['rules']
    rules = ''.join('<li class="rule rule--sm" data-words="%s" data-reveal%s><p class="rule__k">%s · %s</p><p class="rule__h">%s</p><p class="rule__p">%s</p></li>'
                    % (esc(' '.join([b['words']] * 3)), rd(i % 4), b['n'], esc(b['name']), esc(b['rule']), esc(b['rule_body']))
                    for i, b in enumerate(BUILDS))
    shared = ('<section class="sect" id="rules" data-locus data-label="What they share" aria-labelledby="rules-h"><div class="wrap">'
              '<div class="shead shead--center" data-reveal>%s%s</div><ul class="rules rules--eight">%s</ul></div></section>\n') % (
        slabel(R['n'], R['kicker']), heading(R['h2'], 'rules-h'), rules)

    Vt = H['visit']
    visit = ('<section class="sect sect--tight" id="portfolio" data-locus data-label="Portfolio" aria-labelledby="visit-h"><div class="wrap">'
             '<a class="visit" href="%s" target="_blank" rel="noopener" data-spot data-reveal><span class="visit__orb" aria-hidden="true"></span>'
             '<span class="visit__copy"><span class="visit__k">%s</span><h2 class="visit__h" id="visit-h">%s</h2><span class="visit__p">%s</span></span>'
             '<span class="visit__go btn btn--mint"><span>%s</span>%s</span>%s</a><div class="rows__foot">%s</div></div></section>\n') % (
        esc(S['portfolio']), esc(Vt['k']), esc(Vt['h2']), mval(Vt['lede']), esc(Vt['link']), EXTI, NEWTAB, hint(H['hint']))

    body = hero + featured + also + shared + visit
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': S['title'], 'url': DOM + '/', 'description': S['description'],
          'author': {'@type': 'Person', 'name': S['name'], 'url': S['portfolio']},
          'hasPart': [{'@type': 'CreativeWork', 'name': b['name'], 'description': b['line'], 'url': b['live']} for b in BUILDS]}
    return shell('labs', '/', S['title'], S['description'], 'Labs', body, ld=ld)


# ----------------------------------------------------------------------------
# 404
# ----------------------------------------------------------------------------
def notfound():
    N = D.NOT_FOUND
    acts = btn('Labs home', '/', 'primary') + btn('Featured builds', '/#featured', 'ghost') + btn('Portfolio', S['portfolio'], 'ghost')
    index = ''.join('<li><a class="labindex__a" href="%s"><span class="labindex__n">%s · %s</span><span class="labindex__name">%s</span>'
                    '<span class="labindex__tag">%s</span></a></li>' % (b['route'], b['n'], esc(b['tag']), esc(b['name']), esc(b['line']))
                    for b in BUILDS)
    body = ('<section class="phead phead--center phead--nf" id="top" data-locus data-label="Not found"><div class="wrap phead__in" data-reveal>%s%s'
            '<p class="phead__lede">%s</p><p class="nf__path"><span>Requested</span><code data-nf-path>/</code></p>'
            '<div class="nf__recent" data-nf-recent hidden><p class="nf__k">Recent</p><ul data-nf-list></ul></div>'
            '<div class="actions actions--center">%s</div><ul class="labindex labindex--eight" aria-label="Every build">%s</ul>%s</div></section>\n') % (
        slabel(None, N['kicker']), heading(N['h1'], 'page-title', 'h1', 'h1'), esc(N['lede']), acts, index, hint(N['hint']))
    return shell('notfound', '/404', 'Not found · ' + S['title'], S['description'], 'Not found', body, base='/', robots='noindex, follow')


# ----------------------------------------------------------------------------
# data, vercel.json, sitemap, robots
# ----------------------------------------------------------------------------
def data_js():
    data = dict(
        builds=[dict(slug=b['slug'], n=b['n'], name=b['name'], cat=b['cat'], tag=b['tag'], line=b['line'], route=b['route'],
                     live=b['live'], case=b['case'] or '') for b in BUILDS],
        links=dict(email=EMAIL, portfolio=S['portfolio'], substack=S['substack'], linkedin=S['linkedin']),
    )
    return ('/* generated by tools/build.py - do not edit */\nwindow.JJ = '
            + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')


def vercel_json():
    csp = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
           "connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'; "
           "upgrade-insecure-requests")
    cfg = {
        'cleanUrls': True,
        'trailingSlash': False,
        # each build's short link hands off to the product, as a temporary redirect
        'redirects': [{'source': b['route'], 'destination': b['live'], 'permanent': False} for b in BUILDS],
        'headers': [
            {'source': '/assets/fonts/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=31536000, immutable'}]},
            {'source': '/assets/(css|js|img)/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800, must-revalidate'}]},
            {'source': '/(.*)', 'headers': [
                {'key': 'X-Content-Type-Options', 'value': 'nosniff'},
                {'key': 'Referrer-Policy', 'value': 'strict-origin-when-cross-origin'},
                {'key': 'X-Frame-Options', 'value': 'SAMEORIGIN'},
                {'key': 'Content-Security-Policy', 'value': csp},
                {'key': 'Permissions-Policy', 'value': 'camera=(), microphone=(), geolocation=(), payment=()'},
                {'key': 'Strict-Transport-Security', 'value': 'max-age=63072000; includeSubDomains; preload'},
            ]},
        ],
    }
    return json.dumps(cfg, indent=2, ensure_ascii=False) + '\n'


def sitemap():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            '  <url><loc>%s/</loc><lastmod>%s</lastmod></url>\n</urlset>\n') % (DOM, LASTMOD)


def robots():
    return 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % DOM


# ----------------------------------------------------------------------------
# checks
# ----------------------------------------------------------------------------
def resolves(path):
    path = path.split('?')[0]
    if path in ('', '/') or path in ROUTES:
        return True
    full = os.path.join(ROOT, path.lstrip('/'))
    return os.path.isfile(full) or os.path.isfile(full + '.html')


def check(files):
    problems, pages = [], {}
    for rel in files:
        if rel.endswith('.html'):
            with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
                pages[rel] = f.read()
    home_ids = set(re.findall(r'\sid="([^"]+)"', pages.get('index.html', '')))
    for rel, text in pages.items():
        for bad in ('—', '–'):
            if bad in text:
                i = text.index(bad)
                problems.append('%s: dash %r near %r' % (rel, bad, text[max(0, i - 40):i + 40]))
        ids = re.findall(r'\sid="([^"]+)"', text)
        idset = set(ids)
        for dup in sorted({i for i in ids if ids.count(i) > 1}):
            problems.append('%s: duplicate id %s' % (rel, dup))
        for ref in re.findall(r'aria-(?:controls|labelledby)="([^"]+)"', text):
            for one in ref.split():
                if one not in idset:
                    problems.append('%s: aria reference %s has no target' % (rel, one))
        for frag in re.findall(r'href="#([^"]*)"', text):
            if frag and frag not in idset:
                problems.append('%s: anchor #%s has no target' % (rel, frag))
        for href in re.findall(r'href="(/[^"]*)"', text):
            path, _, frag = href.partition('#')
            if not resolves(path):
                problems.append('%s: link %s goes nowhere' % (rel, href))
            elif frag and path in ('', '/') and frag not in home_ids:
                problems.append('%s: link %s has no target on the home page' % (rel, href))
        for src in re.findall(r'src="(/[^"]+)"', text):
            if not resolves(src):
                problems.append('%s: asset %s is missing' % (rel, src))
    return problems


def main():
    written = [write('assets/js/labs-data.js', data_js())]
    for key, rel in (('css', 'assets/css/site.css'), ('site', 'assets/js/site.js'), ('data', 'assets/js/labs-data.js')):
        V[key] = fingerprint(rel)
    written.append(write('index.html', home()))
    written.append(write('404.html', notfound()))
    written.append(write('vercel.json', vercel_json()))
    written.append(write('sitemap.xml', sitemap()))
    written.append(write('robots.txt', robots()))
    problems = check(written)
    if problems:
        for p in problems:
            print('ERROR', p)
        sys.exit(1)
    print('built %d files, %d builds, %d redirects, checks clean' % (len(written), len(BUILDS), len(ROUTES)))


if __name__ == '__main__':
    main()
