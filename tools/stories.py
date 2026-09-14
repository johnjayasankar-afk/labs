"""Stories: every system's visual, told as a few schematic interface moments.

Each story is one light stage in the site's own palette holding a product-style
window whose state follows the bay's phases. Nothing here is a screenshot or a
production interface. Copy is lifted from the case data only; figures are the
case's own or the product's published sample data (RailDrop's sample board,
Daylight's Balanced preset), and the bay caption says which. Where a picture
would otherwise imply a fact nobody published (which ride provider is cheaper,
which clearing venue wins), the story shows the rule instead of a result.

Gridiron's story is captured real games: every figure in it is one Gridiron shows
replaying its NFL Week 1 fixtures, and the bay says so.

Mechanics
  data-step on the story root is the phase being shown. The HTML is written at
  the story's resting phase, so it is complete without script.
  data-on="spec" marks an element that belongs to some phases: "1", "1-2", "2-"
  or "0,2". It carries is-on while the step is in its spec, and its own classes
  decide what that means (s-fx fades it in and out, s-lane lifts, and so on).
  s-var elements take --v0..--v4 and expose the current one as --v."""

import html
import math


def esc(s):
    return html.escape(str(s), quote=True)


def in_spec(spec, i):
    for part in str(spec).split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            if (int(a) if a else 0) <= i <= (int(b) if b else 99):
                return True
        elif part and int(part) == i:
            return True
    return False


# ----------------------------------------------------------------------------
# icons: 16px, stroked in currentColor
# ----------------------------------------------------------------------------
_DOT = 'fill="currentColor" stroke="none"'
ICONS = dict(
    check='<path d="M3.6 8.4l2.8 2.8L12.4 5"/>',
    clock='<circle cx="8" cy="8" r="5.6"/><path d="M8 5.1v3.1l2 1.3"/>',
    person='<circle cx="8" cy="5.5" r="2.4"/><path d="M3.5 13.3c.7-2.4 2.4-3.6 4.5-3.6s3.8 1.2 4.5 3.6"/>',
    pause='<path d="M6.1 4.6v6.8M9.9 4.6v6.8"/>',
    spark='<path d="M7.6 2.4l1.35 3.25L12.2 7 8.95 8.35 7.6 11.6 6.25 8.35 3 7l3.25-1.35z"/><path d="M12.4 10.6l.5 1.2 1.2.5-1.2.5-.5 1.2-.5-1.2-1.2-.5 1.2-.5z"/>',
    sliders='<path d="M2.8 5h10.4M2.8 11h10.4"/><circle cx="6" cy="5" r="1.7" fill="#fff"/><circle cx="10.4" cy="11" r="1.7" fill="#fff"/>',
    shield='<path d="M8 2.4l4.6 1.8v3.6c0 3-2 5-4.6 5.8C5.4 12.8 3.4 10.8 3.4 7.8V4.2z"/><path d="M5.9 8l1.5 1.5 2.8-3"/>',
    train='<rect x="4" y="2.4" width="8" height="9.2" rx="2.2"/><path d="M4 7.2h8M5.6 14l1.1-2.4M10.4 14l-1.1-2.4"/><circle cx="6.3" cy="9.4" r=".6" %s/><circle cx="9.7" cy="9.4" r=".6" %s/>' % (_DOT, _DOT),
    mail='<rect x="2.4" y="3.8" width="11.2" height="8.6" rx="1.9"/><path d="M3 5.1l5 3.6 5-3.6"/>',
    network='<circle cx="8" cy="8" r="1.9"/><circle cx="3.4" cy="3.8" r="1.35"/><circle cx="12.6" cy="3.8" r="1.35"/><circle cx="3.4" cy="12.2" r="1.35"/><circle cx="12.6" cy="12.2" r="1.35"/><path d="M4.5 4.8l2 1.9M11.5 4.8l-2 1.9M4.5 11.2l2-1.9M11.5 11.2l-2-1.9"/>',
    arrow='<path d="M3 8h9.5M8.5 4l4 4-4 4"/>',
    search='<circle cx="7" cy="7" r="4.2"/><path d="M10.2 10.2l3.3 3.3"/>',
    lock='<rect x="3.4" y="7" width="9.2" height="6.6" rx="1.7"/><path d="M5.5 7V5.3a2.5 2.5 0 0 1 5 0V7"/>',
    alert='<path d="M8 2.9l5.5 9.6h-11z"/><path d="M8 6.7v2.8M8 11.2v.1"/>',
    layers='<path d="M8 2.4l5.6 2.9L8 8.2 2.4 5.3z"/><path d="M2.4 8.1L8 11l5.6-2.9M2.4 10.8L8 13.7l5.6-2.9"/>',
    columns='<rect x="2.4" y="3" width="4.6" height="10" rx="1.2"/><rect x="9" y="3" width="4.6" height="10" rx="1.2"/><path d="M4 6h1.5M4 8.5h1.5M10.6 6h1.5M10.6 8.5h1.5"/>',
    calc='<rect x="3.4" y="2.4" width="9.2" height="11.2" rx="1.9"/><path d="M5.5 5.4h5"/><circle cx="5.9" cy="8.6" r=".6" %s/><circle cx="8" cy="8.6" r=".6" %s/><circle cx="10.1" cy="8.6" r=".6" %s/><circle cx="5.9" cy="11" r=".6" %s/><circle cx="8" cy="11" r=".6" %s/><circle cx="10.1" cy="11" r=".6" %s/>' % ((_DOT,) * 6),
    car='<path d="M3.2 10V8.4l1.3-2.9a1.5 1.5 0 0 1 1.4-.9h4.2a1.5 1.5 0 0 1 1.4.9l1.3 2.9V10"/><rect x="2.4" y="8.2" width="11.2" height="3.6" rx="1.3"/><path d="M4.6 11.8v1.4M11.4 11.8v1.4"/>',
    sun='<circle cx="8" cy="8" r="2.7"/><path d="M8 1.9v1.4M8 12.7v1.4M1.9 8h1.4M12.7 8h1.4M3.7 3.7l1 1M11.3 11.3l1 1M3.7 12.3l1-1M11.3 4.7l1-1"/>',
    route='<circle cx="4" cy="12" r="1.6"/><circle cx="12" cy="4" r="1.6"/><path d="M5.4 11.3c3.2-1 .3-5 3.6-6.4l1.5-.5"/>',
    plus='<path d="M8 3.6v8.8M3.6 8h8.8"/>',
    doc='<path d="M4.4 2.4h4.8l2.4 2.4v8.8H4.4z"/><path d="M6.2 7.6h3.6M6.2 10h3.6"/>',
    refresh='<path d="M12.6 6.2A4.9 4.9 0 0 0 3.6 6M3.4 9.8a4.9 4.9 0 0 0 9 .2"/><path d="M12.8 3.3v2.9H9.9M3.2 12.7V9.8h2.9"/>',
    bell='<path d="M4.4 11V7.4a3.6 3.6 0 0 1 7.2 0V11l1 1.2H3.4z"/><path d="M6.8 13.6a1.3 1.3 0 0 0 2.4 0"/>',
    field='<rect x="2.2" y="4" width="11.6" height="8" rx="1.9"/><path d="M5.9 4v8M10.1 4v8" stroke-opacity=".45"/><ellipse cx="9" cy="8" rx="2.3" ry="1.35" %s/>' % _DOT,
)

# the pointer that presses buttons in a story
CURSOR = ('<svg class="s-cursor" viewBox="0 0 16 16" aria-hidden="true" focusable="false">'
          '<path d="M3.2 1.8l9.6 5.7-4.4.9 2.7 4.7-1.9 1.1-2.7-4.7-3.3 3.1z" fill="#fff" stroke="#0f1712" stroke-width="1.1" stroke-linejoin="round"/></svg>')


def pointer(who='', tone=''):
    tag = '<span class="s-ptr__tag%s">%s</span>' % ((' s-ptr__tag--' + tone) if tone else '', esc(who)) if who else ''
    return '<span class="s-ptr">%s%s</span>' % (CURSOR, tag)


def ico(name, cls=''):
    return ('<svg class="s-ico%s" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">%s</svg>'
            % ((' ' + cls) if cls else '', ICONS[name]))


# ----------------------------------------------------------------------------
# a builder that knows the resting step, so the static HTML is already right
# ----------------------------------------------------------------------------
class Mk:
    def __init__(self, rest):
        self.rest = rest

    def el(self, tag, cls, inner='', on=None, style=None):
        c, a = cls, ''
        if on is not None:
            a += ' data-on="%s"' % on
            if in_spec(on, self.rest):
                c += ' is-on'
        if style:
            a += ' style="%s"' % style
        return '<%s class="%s"%s>%s</%s>' % (tag, c.strip(), a, inner, tag)

    def fx(self, inner, on, cls='', tag='span', d=None):
        return self.el(tag, ('s-fx ' + cls).strip(), inner, on, ('--d:%s' % d) if d is not None else None)

    def chip(self, text, tone='', icon=None, on=None, d=None, cls=''):
        c = 's-chip' + ((' s-chip--' + tone) if tone else '') + ((' ' + cls) if cls else '')
        inner = (ico(icon) if icon else '') + '<span>%s</span>' % esc(text)
        if on is None:
            return '<span class="%s">%s</span>' % (c, inner)
        return self.fx(inner, on, c, d=d)

    def swap(self, *items, cls=''):
        return '<span class="s-swap%s">%s</span>' % ((' ' + cls) if cls else '', ''.join(i for i in items if i))

    def status(self, idle=None, wait=None, done=None, busy=None, d=None):
        """Row status: idle clock, busy spinner, held pause, done check. d staggers the settle."""
        return self.swap(self.fx(ico('clock'), idle, 's-st s-st--idle') if idle else '',
                         self.fx('<i class="s-spin"></i>', busy, 's-st s-st--busy') if busy else '',
                         self.fx(ico('pause'), wait, 's-st s-st--wait', d=d) if wait else '',
                         self.fx(ico('check'), done, 's-st s-st--done', d=d) if done else '', cls='s-swap--st')


def skel(*widths, busy=False):
    return '<span class="s-skels">%s</span>' % ''.join(
        '<i class="s-skel%s" style="--w:%gem"></i>' % (' s-busy' if busy else '', w) for w in widths)


def var(values, cls, inner='', tag='i'):
    style = ';'.join('--v%d:%g' % (i, v) for i, v in enumerate(values))
    return '<%s class="s-var %s" style="%s">%s</%s>' % (tag, cls, style, inner, tag)


def chips(*items):
    return '<span class="s-chips">%s</span>' % ''.join(items)


def press(m, label, on, delay=1.2, cls='', who='', tone=''):
    """A button a pointer glides onto and presses while its phase is showing. who
    names the person pressing it, the way a shared cursor does."""
    return m.el('span', ('s-btn s-press ' + cls).strip(), '<span>%s</span>%s' % (esc(label), pointer(who, tone)), on, '--cd:%gs' % delay)


def typed(m, text, on, delay=.3):
    """Text that types itself in each time its phase begins."""
    return m.el('span', 's-type', esc(text), on, '--n:%d;--td:%gs' % (len(text), delay)) + '<i class="s-caret"></i>'


def count(n, pre='', post='', frm=0):
    """A figure that runs from frm to n as it appears. The resting value is n, so a
    still page, a thumbnail or reduced motion always shows the real figure."""
    return ('<b class="s-count" style="--s-to:%d;--s-from:%d" data-pre="%s" data-post="%s"></b>'
            % (n, frm, esc(pre), esc(post)))


def window(icon, title, sub, right, body, foot='', cls='', floats=''):
    return ('<div class="s-win%s"><div class="s-bar"><span class="s-app">%s</span><span class="s-ttl"><b>%s</b><small>%s</small></span>%s</div>'
            '<div class="s-body">%s</div>%s%s</div>') % ((' ' + cls) if cls else '', ico(icon), esc(title), esc(sub), right, body, foot, floats)


def row(label, content, end='', m=None, sweep=None, hold=None, fd=0):
    """A window row. sweep: phases in which attention passes over the row, fd seconds
    in. hold: phases in which it rests there, waiting on a person or a fix."""
    inner = '<span class="s-k">%s</span><span class="s-cell">%s</span>%s' % (esc(label), content, end)
    if m is None or (sweep is None and hold is None):
        return '<div class="s-row">%s</div>' % inner
    if hold is not None:
        inner = m.el('i', 's-row__hold', '', hold) + inner
    if sweep is None:
        return '<div class="s-row">%s</div>' % inner
    return m.el('div', 's-row s-sweep', inner, sweep, '--fd:%gs' % fd)


def foot(label, fill, value):
    return '<div class="s-foot"><span class="s-k">%s</span><span class="s-track">%s</span>%s</div>' % (esc(label), fill, value)


def note(m, icon, tone, title, sub, on, pos, d=None):
    tile = '<span class="s-tile%s">%s</span>' % ((' s-tile--' + tone) if tone else '', ico(icon))
    return m.fx('%s<span><b>%s</b><small>%s</small></span>' % (tile, esc(title), esc(sub)), on, 's-float s-float--%s s-note' % pos, d=d)


def metric(m, value, sub, on, pos='tr', html=None):
    return m.fx('%s<small>%s</small>' % (html or '<b>%s</b>' % esc(value), esc(sub)), on, 's-float s-float--%s s-metric' % pos)


def stage(key, group, n, rest, inner, label, attrs='', outer='', hidden=False, cls=''):
    a11y = ' aria-hidden="true"' if hidden else ' role="img" aria-label="%s"' % esc(label)
    return ('<div class="story story--%s story--%s%s" data-story="%s" data-steps="%d" data-step="%d"%s%s>'
            '<div class="s-in" aria-hidden="true">%s<div class="s-frame">%s</div></div></div>') % (
        group, key, (' ' + cls) if cls else '', key, n, rest, attrs, a11y, outer, inner)


def network(n=18, r=39, cls=''):
    pts = [(50 + r * math.cos(math.radians(-90 + i * 360 / n)), 50 + r * math.sin(math.radians(-90 + i * 360 / n))) for i in range(n)]
    step = max(2, n // 4)
    pairs = sorted({tuple(sorted((i, (i + k) % n))) for i in range(n)
                    for k in ((step + 1,) if i % 2 == 0 else ()) + ((n // 2 - 1,) if i % 3 == 0 else ())})
    bi = ''.join('<line class="bi" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (pts[a] + pts[b]) for a, b in pairs)
    sp = ''.join('<line class="sp" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x, y, 50 + (x - 50) * .2, 50 + (y - 50) * .2) for x, y in pts)
    env = ''.join('<circle class="env" cx="%.1f" cy="%.1f" r="4.6"/>' % p for p in pts)
    nodes = ''.join('<circle class="n" cx="%.1f" cy="%.1f" r="2.2"/>' % p for p in pts)
    return ('<svg class="s-net%s" viewBox="0 0 100 100" aria-hidden="true" focusable="false"><g>%s</g><g>%s</g><g>%s</g><g>%s</g>'
            '<circle class="scan" cx="50" cy="50" r="23"/><circle class="hub-ring" cx="50" cy="50" r="10.5"/><circle class="hub" cx="50" cy="50" r="6.4"/></svg>') % (
        (' ' + cls) if cls else '', bi, sp, env, nodes)


# ----------------------------------------------------------------------------
# Home showcase · Agents, Gate, Market
# ----------------------------------------------------------------------------
def hero(m):
    right = m.swap(m.chip('Two production agents', 'sky', 'spark', '0'), m.chip('Human gate', 'amber', 'shield', '1'),
                   m.chip('Settled multilaterally', 'mint', 'check', '2'))
    # each agent's bar falls to its real ratio: 8 of 210 minutes, 11 of 270
    minis = ''.join('<span class="s-mini"><span>%s</span><b>%s</b><i class="s-mini__bar"><i class="s-mini__fill" style="--r:%.3f"></i></i>'
                    '<small>%s</small></span>' % (name, esc(v), r, esc(what))
                    for name, v, r, what in (('I-Port', '3.5h → 8m', 8 / 210, 'setup'), ('QT CoCo', '4.5h → 11m', 11 / 270, 'investigation')))
    agents = m.el('div', 's-lane', '<p class="s-k">Agents</p>' + minis, on='0')
    gate = m.el('div', 's-lane', '<p class="s-k">Human gate</p>%s<small class="s-lane__note">Between agent intent and irreversible action</small>' % m.swap(
        m.fx(skel(5.5, 3.5), '0', 's-stack'),
        m.fx(m.chip('Held for approval', 'amber', 'pause') + press(m, 'Approve', '1', 1.3, who='Human', tone='amber'), '1', 's-stack'),
        m.fx(m.chip('Approved', 'mint', 'check') + '<span class="s-quiet">typed actions released</span>', '2', 's-stack')), on='1')
    market = m.el('div', 's-lane s-lane--net', '<p class="s-k">Market</p>%s<span class="s-lane__foot">%s</span>' % (
        network(12, 38, 's-net--mini'),
        m.swap(m.fx('<span class="s-quiet">LCH SwapAgent</span>', '0-1'), m.fx('<b class="s-lane__big">$6.5T</b><small>eligible</small>', '2'))), on='2')

    def flow(on):
        # a typed action travels on to the next lane as that lane takes over
        return '<span class="s-flow">%s%s</span>' % (ico('arrow'), m.el('i', 's-packet', '', on))
    body = '<div class="s-lanes">%s%s%s%s%s</div>' % (agents, flow('1'), gate, flow('2'), market)
    floats = (note(m, 'spark', 'sky', 'Hours → minutes', 'expert work, now agents', '0', 'tr')
              + note(m, 'shield', 'amber', 'One control model', 'across Quantile systems', '1', 'tr')
              + metric(m, '$6.5T', 'eligible notional, same gate', '2'))
    return window('network', 'Agents and markets', 'Quantile systems · schematic', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# I-Port · Before, Gate, After
# ----------------------------------------------------------------------------
def iport(m):
    right = m.swap(m.chip('Senior engineering', '', 'person', '0'), m.chip('Agent + operator', 'sky', 'spark', '1'),
                   m.chip('Operations', 'mint', 'check', '2'))
    body = ''.join([
        row('Context', m.swap(m.fx(skel(4.2, 5.6, 3.8), '0'),
                              m.fx(chips(m.chip('Run state', 'sky', None, '1-', 0), m.chip('Configurations', 'sky', None, '1-', 1),
                                         m.chip('Client data', 'sky', None, '1-', 2)), '1-')),
            m.status(idle='0', done='1-', d=3), m=m, sweep='1', fd=.1),
        row('Actions', m.swap(m.fx(skel(6.4, 3.4), '0'),
                              m.fx(chips(m.chip('Typed', 'soft', None, '1-', 4), m.chip('Reversible', 'soft', None, '1-', 5)), '1-')),
            m.status(idle='0', busy='1', done='2', d=1), m=m, sweep='1', fd=.55),
        row('Operator', m.swap(m.fx(m.chip('Owned by senior engineering', 'soft', 'person'), '0'),
                               m.fx(chips(m.chip('Held for approval', 'amber'), press(m, 'Release', '1', 1.2, who='Operator', tone='amber')), '1'),
                               m.fx(m.chip('Released by operator', 'mint', 'check'), '2')),
            m.status(idle='0', wait='1', done='2', d=2), m=m, hold='0-1'),
        row('Quality', m.swap(m.fx(skel(3.6, 4.8), '0-1'), m.fx(m.chip('0 AI config errors in 6 months', 'mint', 'shield'), '2', d=3)),
            m.status(idle='0-1', done='2', d=4), m=m, sweep='2', fd=.7),
    ])
    # 3.5 hours is 210 minutes: the figure runs down to 8 as the cycle lands
    ft = foot('Setup', var([1, .52, .038], 's-fill'),
              m.swap(m.fx('<b class="s-val">3.5h</b>', '0'), m.fx('<b class="s-val s-val--quiet">In review</b>', '1'),
                     m.fx('<b class="s-val s-val--mint">%s</b>' % count(8, post='m', frm=210), '2'), cls='s-swap--end'))
    floats = (note(m, 'clock', '', '3.5 hours', 'per run, senior engineering', '0', 'tr')
              + note(m, 'shield', 'amber', 'HITL on', 'typed, reversible tools only', '1', 'tr')
              + metric(m, '3×', 'run volume, same headcount', '2', html=count(3, post='×')))
    return window('sliders', 'Compression-run setup', 'I-Port · schematic', right, body, ft, floats=floats)


# ----------------------------------------------------------------------------
# QT CoCo · Incident, Evidence, Diagnose
# ----------------------------------------------------------------------------
def coco(m):
    right = m.swap(m.chip('Pages engineering', 'amber', 'alert', '0'), m.chip('Gathering evidence', 'sky', 'search', '1'),
                   m.chip('Resolved in operations', 'mint', 'check', '2'))
    # while evidence arrives the packet fills; it is complete before anything resolves
    packet = ('<span class="s-packet-m"><span class="s-k">Packet</span><span class="s-track s-track--mini"><i class="s-grow"></i></span>'
              '<span class="s-quiet">assembling</span></span>')
    body = ''.join([
        row('Incident', m.swap(m.fx(chips(m.chip('Incident opened', '', 'alert'), m.chip('Paging engineering', 'amber', 'bell', cls='s-pulse s-hide-sm')), '0'),
                               m.fx(chips(m.chip('Incident opened', '', 'alert'), m.chip('Before anyone is paged', 'soft', cls='s-hide-sm')), '1-')),
            m.status(wait='0', done='1-'), m=m, hold='0'),
        row('MCP · run', m.swap(m.fx(skel(5.4, 3), '0'), m.fx(chips(m.chip('Run facts', 'sky', 'network'), skel(4.2, busy=True)), '1'),
                                m.fx(chips(m.chip('Run facts', 'sky', 'network'), m.chip('Relevant', 'soft')), '2')),
            m.status(idle='0', busy='1', done='2', d=0), m=m, sweep='1', fd=.1),
        row('MCP · ops', m.swap(m.fx(skel(4.4, 3.8), '0'), m.fx(chips(m.chip('Ops facts', 'sky', 'network'), skel(3.4, busy=True)), '1', d=2),
                                m.fx(chips(m.chip('Ops facts', 'sky', 'network'), m.chip('Relevant', 'soft'),
                                           m.chip('Noise', 'soft', cls='s-chip--struck s-hide-sm')), '2')),
            m.status(idle='0', busy='1', done='2', d=2), m=m, sweep='1', fd=.5),
        row('Knowledge', m.swap(m.fx(skel(6.8), '0'), m.fx(m.chip('Six years of production support', 'soft', 'doc'), '1-', d=4)),
            m.status(idle='0', done='1-', d=4), m=m, sweep='1', fd=.9),
        row('Decision', m.swap(m.fx(skel(4.6, 2.8), '0'), m.fx(packet, '1', d=6),
                               m.fx(chips(m.chip('Packet complete', 'mint', 'check'), '<span class="s-quiet">escalate only if incomplete</span>'), '2', d=5)),
            m.status(idle='0-1', done='2', d=6), m=m, sweep='2', fd=.55),
    ])
    # 4.5 hours is 270 minutes
    ft = foot('Time', var([1, .5, .041], 's-fill'),
              m.swap(m.fx('<b class="s-val">4.5h</b>', '0'), m.fx('<b class="s-val s-val--quiet">Triaging</b>', '1'),
                     m.fx('<b class="s-val s-val--mint">%s</b>' % count(11, post='m', frm=270), '2'), cls='s-swap--end'))
    floats = (note(m, 'person', 'amber', 'Senior engineering', 'paged by default', '0', 'tr')
              + note(m, 'network', 'sky', 'Two MCP surfaces', 'run and ops evidence', '1', 'tr')
              + metric(m, '−78%', 'escalations to engineering', '2', html=count(78, pre='−', post='%')))
    return window('alert', 'Incident triage', 'QT CoCo · schematic', right, body, ft, floats=floats)


# ----------------------------------------------------------------------------
# LCH SwapAgent · Gross, Run, Compressed, Risk envelope
# ----------------------------------------------------------------------------
def cross_currency(m):
    right = m.swap(m.chip('Bilateral only', '', None, '0'), m.chip('Run in progress', 'sky', 'spark', '1'),
                   m.chip('Compressed', 'mint', 'check', '2'), m.chip('Risk intent held', 'mint', 'shield', '3'))
    stats = ''.join([
        '<div class="s-stat"><span class="s-k">Eligible notional</span>%s</div>' % m.swap(
            m.fx('<span class="s-quiet">Network offsets unused</span>', '0-1'), m.fx('<b class="s-big">$6.5T</b>', '2-')),
        '<div class="s-stat"><span class="s-k">Network</span><span class="s-line2">18 banks · 12 pairs</span></div>',
        '<div class="s-stat"><span class="s-k">Reduction per run</span>%s</div>' % m.swap(
            m.fx('<span class="s-quiet">Pairs only</span>', '0'), m.fx(skel(5.5, busy=True), '1'),
            # the case: 34% greater reduction per run than bilateral, so bilateral draws at 1 / 1.34 of the length
            m.fx('<span class="s-redux"><span class="s-redux__r"><span class="s-redux__k">Bilateral</span><i class="s-redux__bar" style="--w:74.6%%"></i></span>'
                 '<span class="s-redux__r"><span class="s-redux__k">Multilateral</span><i class="s-redux__bar s-redux__bar--mint" style="--w:100%%"></i>'
                 '<b class="s-redux__v">%s</b></span></span>' % count(34, pre='+', post='%'), '2-', d=2)),
        '<div class="s-stat"><span class="s-k">Each book</span>%s</div>' % m.swap(
            m.fx(skel(4.6), '0-2'), m.fx(m.chip('Inside its constraints', 'mint', 'shield'), '3')),
    ])
    body = ('<div class="s-split"><div class="s-netbox">%s<p class="s-legend"><span><i class="s-lg s-lg--n"></i>Participant</span>'
            '<span><i class="s-lg s-lg--hub"></i>LCH SwapAgent</span></p></div><div class="s-stats">%s</div></div>') % (network(), stats)
    floats = (note(m, 'network', 'sky', 'SwapAgent settles', 'compatible offsets across the network', '1', 'tr')
              + m.fx(m.chip('Eligible notional is not cash saved', 'ink'), '3', 's-float s-float--bl'))
    return window('network', 'Cross-currency compression', 'LCH SwapAgent · schematic', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# Simplified Compression · Split, Diff, Lock
# ----------------------------------------------------------------------------
VAL_ROWS = [(.52, .5, .5), (.48, .9, .46), (.55, .52, .53), (.5, .12, .49), (.46, .47, .47)]


def valuation(m):
    right = m.swap(m.chip('Independent view', 'sky', 'columns', '0'), m.chip('Outside tolerance', 'amber', 'alert', '1'),
                   m.chip('Locked', 'mint', 'lock', '2'))
    head = '<div class="s-vrow s-vrow--head"><span class="s-k">Row</span><span class="s-k">Internal</span><span class="s-k">Independent</span><span class="s-k">Tolerance</span><span></span></div>'
    rows = []
    for i, (w, out, inn) in enumerate(VAL_ROWS):
        bad = out < .3 or out > .7
        # one dot per row: it appears where the independent view lands, and a row
        # outside the band fails early, then moves inside once the sources agree
        dot = var([out, out, inn], 's-dot' + (' s-dot--bad' if bad else ''))
        inner = '<span>%s</span><span>%s</span><span>%s</span><span class="s-band"><i class="s-band__ok"></i>%s</span>%s' % (
            skel(1.8 + (i % 3) * .5), '<i class="s-skel s-skel--ink" style="--w:%gem"></i>' % (2.6 + w * 2),
            m.swap(m.fx(skel(2.4 + w * 2, busy=True), '0'), m.fx('<i class="s-skel s-skel--sky" style="--w:%gem"></i>' % (2.6 + w * 2 + (.9 if bad else .1)), '1-', d=i)),
            dot, m.status(busy='0', wait='1' if bad else None, done=('2' if bad else '1-'), d=i))
        rows.append(m.el('div', 's-vrow' + (' s-vrow--bad' if bad else ''), inner, on='1' if bad else None))
    body = head + ''.join(rows)
    ft = ('<div class="s-foot s-foot--time"><span class="s-k">Check</span><span class="s-timeline"><i class="s-tl__check"></i><i class="s-tl__gap"></i>'
          '<i class="s-tl__live"></i><span class="s-tl__lab s-tl__lab--a">Independent check</span><span class="s-tl__lab s-tl__lab--g">48h</span>'
          '<span class="s-tl__lab s-tl__lab--b">Live window</span></span></div>')
    floats = (note(m, 'columns', 'sky', 'Two sources', 'before the live window', '0', 'tr')
              + note(m, 'alert', 'amber', 'Fails early', 'not mid-cycle', '1', 'tr')
              + metric(m, '−91%', 'failed-run resubmissions', '2', html=count(91, pre='−', post='%'))
              + m.fx(m.chip('$6T+ cycle notional under check', 'ink'), '2', 's-float s-float--bl'))
    return window('columns', 'Valuation check', 'Simplified Compression · schematic', right, body, ft, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# ForexClear · Book, Gates, Accept
# ----------------------------------------------------------------------------
def fx_compression(m):
    right = m.swap(m.chip('Book ready', '', 'doc', '0'), m.chip('Gating', 'amber', 'shield', '1'),
                   m.chip('Accepted for the live run', 'mint', 'check', '2'))
    sources = ''.join(m.swap(m.fx('<span class="s-src">%d</span>' % (i + 1), '0'), m.fx('<span class="s-src s-src--ok">%s</span>' % ico('check'), '1-', d=2 + i))
                      for i in range(4))
    # the gates clear in order: eligibility, margin, then the four sources
    body = ''.join([
        row('Book', chips(m.chip('FX forwards', 'soft'), m.chip('NDFs', 'soft'))),
        row('Eligibility', m.swap(m.fx(skel(5.2), '0'), m.fx(m.chip('Eligible', 'soft', 'check'), '1-')), m.status(idle='0', done='1-', d=0), m=m, sweep='1', fd=.05),
        row('Margin', m.swap(m.fx(skel(6.6), '0'), m.fx(m.chip('ForexClear IM, inside the optimizer', 'sky', 'calc'), '1-', d=1)), m.status(idle='0', done='1-', d=2), m=m, sweep='1', fd=.3),
        row('Sources', '<span class="s-srcs">%s<span class="s-quiet">four must agree</span></span>' % sources, m.status(idle='0', done='1-', d=6), m=m, sweep='1', fd=.6),
        row('Proposals', m.swap(m.fx(skel(4, 3.2), '0'), m.fx(chips(m.chip('Cut before live', 'amber', 'alert'), m.chip('Kept', 'soft', 'check')), '1', d=7),
                                m.fx(m.chip('Accepted', 'mint', 'check'), '2')), m.status(idle='0', wait='1', done='2', d=7), m=m, hold='1', sweep='2', fd=.5),
    ])
    ft = foot('Acceptance', var([.001, .5, 1], 's-fill s-fill--mint'),
              m.swap(m.fx('<b class="s-val s-val--quiet">Not run</b>', '0'), m.fx('<b class="s-val s-val--quiet">Gating</b>', '1'),
                     m.fx('<b class="s-val s-val--mint">%s</b>' % count(100, post='%'), '2'), cls='s-swap--end'))
    floats = (note(m, 'alert', 'amber', 'Good math still fails', 'if margin or data disagree', '0', 'tr')
              + note(m, 'shield', 'amber', 'Gates before live', 'margin and four sources', '1', 'tr')
              + metric(m, '40+', 'live runs, 100% acceptance', '2', html=count(40, post='+'))
              + m.fx(m.chip('−94% live-run failures', 'ink'), '2', 's-float s-float--bl'))
    return window('shield', 'FX proposal', 'ForexClear · schematic', right, body, ft, floats=floats)


# ----------------------------------------------------------------------------
# AI Platform & Controls · Context, Actions, Services, HITL, Eval
# ----------------------------------------------------------------------------
LAYERS = [('Context', 'MCP servers and domain APIs', 'sky'), ('Actions', 'Pydantic-typed actions', 'sky'),
          ('Services', 'Deterministic, outside the model', ''), ('HITL', 'A human approves the consequential step', 'amber'),
          ('Eval', 'Shared evaluation and QA baselines', 'mint')]


def platform(m):
    right = m.swap(*[m.chip(t, tone, None, str(k)) for k, (t, _, tone) in enumerate(
        [('Context', '', 'sky'), ('Typed actions', '', 'sky'), ('Deterministic', '', ''), ('Awaiting approval', '', 'amber'), ('Shared baselines', '', 'mint')])])
    layers = []
    for k, (tag, text, tone) in enumerate(LAYERS):
        idle = ('0-%d' % (k - 1)) if k > 0 else None
        done = ('%d-' % (k + 1)) if k < len(LAYERS) - 1 else None
        active = m.fx(ico('pause'), str(k), 's-st s-st--wait') if tone == 'amber' else m.fx('<i class="s-spin"></i>', str(k), 's-st s-st--busy')
        st = m.swap(m.fx(ico('clock'), idle, 's-st s-st--idle') if idle else '', active, m.fx(ico('check'), done, 's-st s-st--done') if done else '', cls='s-swap--st')
        act = ''
        if tag == 'HITL':
            act = m.fx(press(m, 'Approve', '3', 1.4, who='Human', tone='amber'), '3', 's-layer__act')
        elif tag == 'Eval':
            act = m.fx(m.chip('Production-ready', 'mint', 'check'), '4', 's-layer__act', d=3)
        # a layer's number turns mint once the request has passed through it
        num = m.el('span', 's-layer__n', '%02d' % (k + 1), on=done)
        layers.append(m.el('div', 's-layer', '%s<span class="s-layer__t"><span class="s-k">%s</span><b>%s</b></span>%s%s' % (
            num, esc(tag), esc(text), act, st), on=str(k)))
    systems = '<div class="s-systems"><span class="s-k">5 systems</span>%s</div>' % ''.join(
        '<span class="s-sys" style="--d:%d">%s%s</span>' % (i, ico('spark'), m.el('i', 's-sys__ok', ico('check'), on='4'))
        for i in range(5))
    body = '<div class="s-plat">%s<span class="s-flow s-flow--v">%s</span><div class="s-layers">%s</div></div>' % (systems, ico('arrow'), ''.join(layers))
    floats = (metric(m, '5', 'enterprise systems, one path', '4', html=count(5))
              + m.fx(m.chip('Scope expands when evals say so', 'ink'), '4', 's-float s-float--bl'))
    return window('layers', 'Agent control plane', 'AI Platform & Controls · schematic', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# OpenGamma What-If · Base, + Trade, Simulate, Compare
# ----------------------------------------------------------------------------
VENUES = ['CME SPAN', 'ICE IRM', 'OTC']


def margin_simulator(m):
    right = m.swap(m.chip('Current portfolio', '', 'doc', '0'), m.chip('Hypothetical trade', 'sky', 'plus', '1'),
                   m.chip('Simulating venues', 'sky', 'spark', '2'), m.chip('Before execution', 'mint', 'check', '3'))
    seg = '<span class="s-seg">%s%s</span>' % (''.join('<span class="s-seg__b">%s</span>' % v for v in VENUES),
                                               var([0, 0, 0, 0], 's-seg__ind'))
    body = ''.join([
        row('Portfolio', '<span class="s-track s-track--wide">%s</span>' % var([.62, .62, .62, .62], 's-fill'), m.chip('Initial margin known', 'soft')),
        row('Trade', m.swap(m.fx(skel(6), '0'),
                            m.fx(chips(m.chip('Hypothetical trade', 'sky', 'plus', cls='s-chip--dash s-slide'), press(m, 'Simulate', '1', 1.4, who='Desk', tone='sky')), '1'),
                            m.fx(chips(m.chip('Hypothetical trade', 'sky', 'plus', cls='s-chip--dash'), '<span class="s-quiet">outside the book</span>'), '2-'))),
        row('Venues', m.swap(m.fx(skel(4, 4, 4), '0-1'), m.fx(seg, '2-'))),
        '<div class="s-cmp">%s%s</div>' % (
            '<div class="s-cmp__row"><span class="s-k">Standalone</span><span class="s-track s-track--wide">%s</span>%s</div>' % (
                var([0, 0, .5, .86], 's-fill s-fill--soft'), m.swap(m.fx(skel(2), '0-2'), m.fx('<b class="s-val s-val--quiet">on its own</b>', '3'), cls='s-swap--end')),
            # the hatched span is what offsets already in the book take off the standalone cost
            '<div class="s-cmp__row"><span class="s-k">Incremental</span><span class="s-track s-track--wide">%s%s</span>%s</div>' % (
                var([0, 0, .5, .6], 's-fill s-fill--mint'), m.el('i', 's-gap', '', on='3'),
                m.swap(m.fx(skel(2), '0-2'), m.fx('<b class="s-val s-val--mint">with offsets</b>', '3', d=3), cls='s-swap--end'))),
    ])
    floats = (metric(m, 'up to −30%', 'initial margin, when offsets apply', '3', html=count(30, pre='up to −', post='%'))
              + m.fx(m.chip('Observed potential, not a guarantee', 'ink'), '3', 's-float s-float--bl'))
    return window('calc', 'Pre-trade what-if', 'OpenGamma · schematic', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# RideLens · Route, Price, Soonest, Value (quote types, not providers, are ranked)
# ----------------------------------------------------------------------------
QUOTES = [('Upfront', 'upfront price, kept distinct', 's-q--solid', (1, 1, 0)),
          ('Range', 'both ends stay on the board', 's-q--range', (0, 2, 1)),
          ('Estimate', 'modeled, shown as an estimate', 's-q--dash', (2, 0, 2)),
          ('Expired', 'a stale quote never wins', 's-q--gone', (3, 3, 3))]


def ridelens(m):
    right = m.swap(m.chip('Route mapped once', 'sky', 'route', '0'), m.chip('By price', '', None, '1'),
                   m.chip('By soonest pickup', '', None, '2'), m.chip('By value', '', None, '3'))
    seg = '<span class="s-seg s-seg--3">%s%s</span>' % (''.join('<span class="s-seg__b">%s</span>' % v for v in ('Price', 'Soonest', 'Value')),
                                                        var([0, 0, 1, 2], 's-seg__ind'))
    quotes = []
    for label, sub, cls, ranks in QUOTES:
        # the quote on top for each rule is outlined; an expired quote never is
        top = ','.join(str(step + 1) for step, rank in enumerate(ranks) if rank == 0)
        style = ';'.join('--v%d:%d' % (i, r) for i, r in enumerate([ranks[0], ranks[0], ranks[1], ranks[2]]))
        quotes.append(m.el('span', 's-var s-q ' + cls, '<span class="s-q__t"><b>%s</b><small>%s</small></span><span class="s-q__viz"><i></i></span>'
                           % (esc(label), esc(sub)), on=top or None, style=style))
    board = ('<div class="s-quotes"><span class="s-ranks">%s</span><span class="s-qlist">%s</span>%s</div>' % (
        ''.join('<i>%d</i>' % (i + 1) for i in range(4)), ''.join(quotes),
        m.fx('<span class="s-qwait">%s</span>' % ''.join(skel(9, 5, busy=True) for _ in range(4)), '0', 's-qskel')))
    # two of the product's quick-fill hubs type themselves in; the compare runs on the keyboard shortcut the product documents
    trip = ('<span class="s-fields"><span class="s-field"><span class="s-field__k">From</span>%s</span>'
            '<i class="s-field__to">%s</i><span class="s-field"><span class="s-field__k">To</span>%s</span></span>') % (
        typed(m, 'Times Sq', '0', .3), ico('arrow'), typed(m, 'JFK', '0', 1.05))
    body = ''.join([
        row('Trip', trip, m.status(busy='0', done='1-')),
        row('Rank', m.swap(m.fx(chips(press(m, 'Compare', '0', 1.7, who='You'), '<span class="s-kbd"><kbd>⌘</kbd><kbd>Enter</kbd></span>'), '0'), m.fx(seg, '1-')),
            m.swap(m.fx(m.chip('Auto-refresh', 'soft', 'refresh', cls='s-spinico'), '1-', d=4), cls='s-swap--end s-hide-sm')),
        board,
    ])
    floats = (note(m, 'route', 'sky', 'Live roads', 'one route, four providers', '0', 'tr')
              + m.fx(m.chip('Final fare confirmed in the provider app', 'ink'), '1-3', 's-float s-float--bl'))
    return window('car', 'Compare rides', 'RideLens · Uber, Lyft, Empower, Curb', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# RailDrop · Booked, Watching, Board, Alert (RailDrop's own sample board)
# ----------------------------------------------------------------------------
RD_BOARD = [('06:10', 'Northeast Regional 95', '4h 08m', '$47', 'Save $81'),
            ('07:00', 'Acela 2155', '3h 50m', '$133', 'Listed'),
            ('09:20', 'Northeast Regional 93', '4h 02m', '$61', 'Save $67'),
            ('13:00', 'Acela 2167', '3h 47m', '$141', 'Listed')]


def raildrop(m):
    right = m.swap(m.chip('Booked', '', 'check', '0'), m.chip('Scanning ±1 day', 'sky', 'search', '1'),
                   m.chip('Cheapest listed $47', '', None, '2'), m.chip('1 alert', 'mint', 'mail', '3'))
    trip = ('<div class="s-trip"><span class="s-stn"><b>BOS</b><small>Boston, MA</small></span>'
            '<span class="s-route"><i class="s-rail"></i><i class="s-runner"></i></span>'
            '<span class="s-stn s-stn--r"><b>NYP</b><small>New York, NY</small></span></div>')
    days = ''.join(m.el('span', 's-chip s-chip--soft s-scan', '<span>%s</span>' % d, on='1', style='--d:%d' % i)
                   for i, d in enumerate(('Day before', 'Travel day', 'Day after')))
    watch = m.fx(''.join([
        trip,
        row('Paid', m.chip('You paid $128', 'ink'), m.swap(m.fx(press(m, 'Watch trip', '0', 1.3, who='You'), '0'), cls='s-swap--end')),
        row('Window', '<span class="s-chips">%s</span>' % days, m.status(idle='0', busy='1')),
        row('Scans', chips(m.swap(m.chip('Now', '', 'clock', '0'), m.chip('Now', 'mint', 'check', '1-')), m.chip('Morning', '', 'clock'),
                           m.chip('Afternoon', '', 'clock'), m.chip('Evening', '', 'clock'))),
        row('Alert', m.chip('One email, only when a listed fare beats $128', 'soft', 'mail')),
    ]), '0-1', 's-view', tag='div')
    rows = ''.join('<div class="s-trow%s"><span class="s-time">%s</span><span class="s-tname"><b>%s</b><small>%s</small></span>'
                   '<span class="s-price%s"><b>%s</b><small>%s</small></span></div>'
                   % (' s-trow--best' if i == 0 else '', t, esc(name), dur, ' s-price--save' if tag.startswith('Save') else '', p, tag)
                   for i, (t, name, dur, p, tag) in enumerate(RD_BOARD))
    # on the board, focus walks down the trains the way J does in the product
    board = m.fx('<div class="s-boardhead"><span>You paid $128</span><span>Cheapest listed $47</span></div>%s%s' % (
        m.el('div', 's-board', rows, on='2'),
        m.fx('<span class="s-kbd"><kbd>J</kbd><kbd>K</kbd></span><span>focus a train</span><span class="s-kbd"><kbd>H</kbd></span><span>hides it</span>',
             '2', 's-boardfoot', d=5)), '2-', 's-view', tag='div')
    body = '<div class="s-views">%s%s</div>' % (watch, board)
    floats = (note(m, 'train', '', 'Every bookable train', 'Regional, Acela, connections', '1', 'tr')
              + note(m, 'mail', 'mint', 'Regional 95 dropped $14', 'Look at switching · confirm on Amtrak', '3', 'br'))
    return window('train', 'Fare watch', 'BOS → NYP · RailDrop sample board', right, body, floats=floats)


# ----------------------------------------------------------------------------
# Daylight · Schedule, Resolve, Explain, Confirm (Balanced preset)
# ----------------------------------------------------------------------------
LADDER = ['Restored', 'Paused', 'Manual override', 'App rule', 'Workspace', 'Schedule']


def daylight(m):
    right = m.swap(m.chip('Balanced', '', 'sun', '0'), m.chip('Resolving', 'sky', 'layers', '1'),
                   m.chip('Explained', '', 'doc', '2'), m.chip('Confirmed', 'mint', 'check', '3'))
    # 12:00 to 24:00 across 200 units; warmth steps with short fades
    chart = ('<svg class="s-chart" viewBox="0 0 200 92" aria-hidden="true" focusable="false">'
             '<path class="s-chart__grid" d="M0 76H200M0 18H200"/>'
             '<path class="s-chart__area" d="M0 18H108L117 40H150L158 55H183L192 64H200V76H0Z"/>'
             '<path class="s-chart__line" d="M0 18H108L117 40H150L158 55H183L192 64H200"/>'
             '<circle class="s-chart__pt" cx="117" cy="40" r="2.4"/><circle class="s-chart__pt" cx="158" cy="55" r="2.4"/><circle class="s-chart__pt" cx="192" cy="64" r="2.4"/>'
             '<line class="s-chart__now" x1="0" y1="10" x2="0" y2="76"/>'
             '<text class="s-chart__t" x="1" y="12">6500 K</text><text class="s-chart__t" x="199" y="72" text-anchor="end">2800 K</text>'
             '<text class="s-chart__x" x="0" y="89">12:00</text><text class="s-chart__x" x="117" y="89" text-anchor="middle">19:00</text>'
             '<text class="s-chart__x" x="158" y="89" text-anchor="middle">21:30</text><text class="s-chart__x" x="200" y="89" text-anchor="end">23:30</text></svg>')
    # a small display: it warms with the schedule, then shows the explained state, neutral and dimmed
    disp = '<span class="s-disp" aria-hidden="true"><i class="s-disp__bar"></i><i class="s-disp__badge">%s</i></span>' % ico('check')
    ladder = ''.join('<span class="s-rung%s" style="--i:%d"><i>%d</i><span>%s</span>%s</span>' % (
        ' s-rung--win' if name in ('App rule', 'Schedule') else '', i, i + 1, name,
        m.chip('Warmth', 'sky') if name == 'App rule' else (m.chip('Brightness', 'mint') if name == 'Schedule' else ''))
        for i, name in enumerate(LADDER))
    steps4 = ''.join('<b class="s-t%d">%s</b><small>%s</small>' % (i + 1, k, t)
                     for i, (k, t) in enumerate((('6500 K', 'by day'), ('4200 K', '19:00'), ('3200 K', '21:30'), ('2800 K', '23:30'))))
    reads = '<i class="s-read__to">%s</i>' % ico('arrow')
    panel = m.swap(
        m.fx('<span class="s-k">Balanced preset</span><span class="s-steps4">%s</span>' % steps4, '0', 's-pane'),
        m.fx('<span class="s-k">Six layers, one fixed order</span><span class="s-ladder">%s</span>' % ladder, '1', 's-pane'),
        m.fx('<span class="s-k">Every state has a sentence</span><q class="s-quote">Your display is neutral because <mark class="s-hl">Colour Work is active for this app</mark>. '
             'Dimming comes from <mark class="s-hl s-hl--2">Balanced</mark>.</q>', '2', 's-pane'),
        m.fx('<span class="s-k">Readback</span><span class="s-read">%s%s%s%s%s</span><span class="s-quiet">Success from an API is not evidence</span>' % (
            m.chip('Asked', 'soft', 'check', '3', 1), reads, m.chip('Accepted', 'soft', 'check', '3', 3), reads,
            m.chip('Confirmed', 'mint', 'check', '3', 5)), '3', 's-pane'),
        cls='s-panes')
    # small frames drop the panel, and this line under the chart carries each step instead
    cap = m.swap(m.chip('6500 K by day to 2800 K at 23:30', 'soft', 'sun', '0'),
                 m.chip('Warmth and brightness decided separately', 'sky', 'layers', '1'),
                 m.chip('Every state has a sentence', 'soft', 'doc', '2'),
                 m.chip('Asked, accepted, confirmed', 'mint', 'check', '3'), cls='s-chartcap')
    body = '<div class="s-daylight"><div class="s-chartbox">%s%s%s</div>%s</div>' % (chart, disp, cap, panel)
    floats = (note(m, 'lock', '', 'Offline', 'no location, no network', '0', 'tr')
              + m.fx(m.chip('Warmth and brightness decided separately', 'ink'), '1-2', 's-float s-float--bl')
              + note(m, 'check', 'mint', 'Three levels of certainty', 'asked, accepted, confirmed', '3', 'tr'))
    return window('sun', 'Display schedule', 'Daylight · Balanced preset', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# Gridiron · Slate, Drive, Odds, Touchdown (captured real games, NFL Week 1 replay)
# ----------------------------------------------------------------------------
# Every figure is one Gridiron shows while replaying the ESPN and Kalshi data it
# captured for Sunday 13 September 2026: the live slate at 4:33 PM Eastern, then
# ARI at LAC, through the touchdown that ended ARI's opening drive.
GR_SLATE = [('OT 4:57', 'NO at DET', (24, 31), 'Overtime · 7-point game'),
            ('Q1 9:34', 'ARI at LAC', (0, 0), 'Tying or go-ahead chance in the red zone'),
            ('Q4 1:57', 'CHI at CAR', (59, 37), None),
            ('Q1 12:11', 'GB at MIN', (3, 0), None)]
# ARI's opening drive, spot to spot, in yards from ARI's own goal line. The
# incomplete pass and the run for no gain left the ball where it was.
GR_DRIVE = [(30, 57, 'pass'), (57, 59, 'run'), (59, 70, 'run'), (70, 75, 'pass'), (75, 79, 'run'),
            (79, 81, 'run'), (81, 92, 'pass'), (92, 95, 'run')]
GR_FAR, GR_NEAR, GR_AXIS = 28.0, 84.0, 56.0


def gr_x(u, y):
    """Where a point u yards from the left end line (0 to 120) sits at height y. The
    far sideline is drawn narrower than the near one: a light broadcast view."""
    t = (y - GR_FAR) / (GR_NEAR - GR_FAR)
    left, right = 44 - 32 * t, 256 + 32 * t
    return left + (right - left) * u / 120


def gr_band(u0, u1):
    return 'M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ' % (gr_x(u0, GR_FAR), GR_FAR, gr_x(u1, GR_FAR), GR_FAR,
                                                        gr_x(u1, GR_NEAR), GR_NEAR, gr_x(u0, GR_NEAR), GR_NEAR)


def gr_across(u):
    return 'M%.1f %.1fL%.1f %.1f' % (gr_x(u, GR_FAR), GR_FAR, gr_x(u, GR_NEAR), GR_NEAR)


def svgel(m, tag, cls, attrs, on=None, style=None):
    """An SVG element that belongs to some phases, written at the resting one."""
    c = cls + (' is-on' if on is not None and in_spec(on, m.rest) else '')
    extra = (' data-on="%s"' % on if on is not None else '') + (' style="%s"' % style if style else '')
    return '<%s class="%s"%s %s/>' % (tag, c, extra, attrs)


def gr_pitch(m):
    ax = lambda u: gr_x(u, GR_AXIS)  # noqa: E731
    nl, nr = gr_x(0, GR_NEAR), gr_x(120, GR_NEAR)
    out = ['<path class="gr-slab" d="M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ"/>' % (nl, GR_NEAR, nr, GR_NEAR, nr + 2, GR_NEAR + 5, nl - 2, GR_NEAR + 5),
           '<path class="gr-turf" d="%s"/>' % gr_band(0, 120)]
    out += ['<path class="gr-mow" d="%s"/>' % gr_band(u, u + 10) for u in (10, 30, 50, 70, 90)]
    out += ['<path class="gr-ez" d="%s"/>' % gr_band(0, 10), '<path class="gr-ez" d="%s"/>' % gr_band(110, 120)]
    # red zone while ARI is inside the LAC 20; the end zone lights once the ball reaches it
    out.append(svgel(m, 'path', 'gr-rz', 'd="%s"' % gr_band(90, 110), on='1-2'))
    out.append(svgel(m, 'path', 'gr-td', 'd="%s"' % gr_band(110, 120), on='3'))
    out += ['<path class="gr-yl%s" d="%s"/>' % (' gr-yl--10' if u % 10 == 0 else '', gr_across(u)) for u in range(15, 110, 5)]
    out += ['<path class="gr-gl" d="%s"/>' % gr_across(u) for u in (10, 110)]
    out += ['<text class="gr-num" x="%.1f" y="79" text-anchor="middle">%d</text>' % (gr_x(u, 79), min(u - 10, 110 - u)) for u in range(20, 101, 10)]
    out += ['<text class="gr-ezt%s" transform="translate(%.1f %.1f) rotate(%d)" text-anchor="middle" dominant-baseline="central">%s</text>'
            % (cls, gr_x(u, GR_AXIS), GR_AXIS, turn, name) for u, turn, name, cls in ((5, -90, 'ARI', ''), (115, 90, 'LAC', ' gr-ezt--lac'))]
    # the drive, drawn only between reported spots: passes arc, runs sweep
    out.append('<circle class="gr-spot" cx="%.1f" cy="%.1f" r="1.1" style="--i:-1"/>' % (ax(10 + GR_DRIVE[0][0]), GR_AXIS))
    for i, (a, b, kind) in enumerate(GR_DRIVE):
        x1, x2 = ax(10 + a), ax(10 + b)
        lift = 5 + .55 * (b - a) if kind == 'pass' else 1.6 + .16 * (b - a)
        out.append('<path class="gr-hop gr-hop--%s" pathLength="1" d="M%.1f %.1fQ%.1f %.1f %.1f %.1f" style="--i:%d"/>'
                   % (kind, x1, GR_AXIS, (x1 + x2) / 2, GR_AXIS - 2 * lift, x2, GR_AXIS, i))
        out.append('<circle class="gr-spot" cx="%.1f" cy="%.1f" r="1.1" style="--i:%d"/>' % (x2, GR_AXIS, i))
    # blue marks the line of scrimmage; on goal to go the goal line, in amber, is the line to gain
    out.append(svgel(m, 'path', 'gr-los', 'd="%s"' % gr_across(105), on='1-2'))
    out.append(svgel(m, 'path', 'gr-ltg', 'd="%s"' % gr_across(110), on='1-2'))
    x1, x2 = ax(105), ax(110)
    out.append(svgel(m, 'path', 'gr-hop gr-hop--run gr-hop--td', 'pathLength="1" d="M%.1f %.1fQ%.1f %.1f %.1f %.1f"'
                     % (x1, GR_AXIS, (x1 + x2) / 2, GR_AXIS - 5, x2, GR_AXIS), on='3'))
    out.append(('<g class="gr-ballg" style="--tx:%.1fpx"><circle class="gr-halo" cx="%.1f" cy="%.1f" r="4.4"/>'
                '<ellipse class="gr-ball" cx="%.1f" cy="%.1f" rx="3.3" ry="2"/>'
                '<path class="gr-lace" d="M%.1f %.1fh3M%.1f %.1fv1M%.1f %.1fv1M%.1f %.1fv1"/></g>')
               % (x2 - x1, x1, GR_AXIS, x1, GR_AXIS, x1 - 1.5, GR_AXIS, x1 - .8, GR_AXIS - .5, x1, GR_AXIS - .5, x1 + .8, GR_AXIS - .5))
    return '<svg class="gr-svg" viewBox="0 0 300 92" aria-hidden="true" focusable="false">%s</svg>' % ''.join(out)


def gr_src(k, v):
    """A source-named figure, the way Gridiron's cards write DRAFTKINGS LAC −8.5."""
    return '<span class="gr-src"><i>%s</i><b>%s</b></span>' % (esc(k), esc(v))


def gridiron(m):
    right = m.swap(m.fx('<span class="s-chip s-chip--mint"><i class="gr-dot"></i><span>6 live</span></span>', '0'),
                   m.chip('Red zone', 'amber', 'alert', '1'), m.chip('Sources named', 'sky', 'layers', '2'),
                   m.chip('Scoring play', 'mint', 'check', '3'))
    games = []
    for i, (clock, name, (away, home), why) in enumerate(GR_SLATE):
        pick = name == 'ARI at LAC'
        sub = '<small><i>Watch next</i>%s</small>' % esc(why) if why else ''
        games.append('<div class="gr-g%s" style="--i:%d"><span class="gr-g__clock">%s</span><span class="gr-g__t"><b>%s</b>%s</span>'
                     '<span class="gr-g__sc"><b>%d</b><i></i><b>%d</b></span>%s</div>'
                     % (' gr-g--pick' if pick else '', i, esc(clock), esc(name), sub, away, home,
                        press(m, 'Open', '0', 1.6, who='You') if pick else '<span></span>'))
    slate = m.fx('<div class="gr-slate"><div class="gr-slate__head"><span class="gr-live"><i class="gr-dot"></i><b>6</b>live</span>'
                 '<span class="s-quiet">1 in overtime · 2 in the red zone</span></div><div class="gr-games">%s</div></div>' % ''.join(games),
                 '0', 's-view', tag='div')
    # the score bug is text over the field, never drawn into it
    bug = ('<div class="gr-bug"><span class="gr-bug__tm"><i class="gr-poss"></i>ARI</span><b class="gr-bug__sc">%s</b>'
           '<span class="gr-bug__clock">%s</span><b class="gr-bug__sc">0</b><span class="gr-bug__tm">LAC</span></div>') % (
        m.swap(m.fx('0', '0-2'), m.fx(count(7), '3')),
        m.swap(m.fx('<b>Q1 9:34</b><small>2nd &amp; Goal · LAC 5</small>', '0-2'), m.fx('<b>Q1 8:49</b><small>Touchdown ARI</small>', '3')))
    pitch = '<div class="gr-pitch">%s%s<span class="gr-note">Schematic · ARI defends left</span></div>' % (gr_pitch(m), bug)
    # ESPN's win probability for LAC: 69.59% after the run to the 5, 64.89% after the touchdown
    meter = ('<span class="gr-wp"><span class="gr-wp__tm">ARI</span><span class="gr-wp__track">%s</span>%s</span>'
             % (var([.5, .5, .304, .351], 'gr-wp__lac'), m.swap(m.fx('<b>LAC 70%</b>', '0-2'), m.fx('<b>LAC 65%</b>', '3'), cls='gr-wp__v')))
    chance = m.el('div', 's-row s-sweep', ''.join([
        m.swap(m.fx('<span class="s-k">Drive</span>', '0-1'), m.fx('<span class="s-k">Win prob</span>', '2-')),
        '<span class="s-cell">%s</span>' % m.swap(
            m.fx(chips(gr_src('ARI drive', '10 plays · 65 yds'), '<span class="s-quiet s-hide-sm">from ARI 30</span>'), '0-1'),
            m.fx(meter, '2-', cls='gr-fill')),
        m.swap(m.fx(m.chip('ESPN', 'soft'), '2-'), cls='s-swap--end gr-end'),
    ]), '2', '--fd:.1s')
    market = m.el('div', 's-row s-sweep', ''.join([
        m.swap(m.fx('<span class="s-k">Spot</span>', '0-1'), m.fx('<span class="s-k">Lines</span>', '2'), m.fx('<span class="s-k">Moment</span>', '3')),
        '<span class="s-cell">%s</span>' % m.swap(
            m.fx(chips(gr_src('Ball spot', 'LAC 5'), '<span class="s-quiet s-hide-sm">from the provider’s field-position label</span>'), '0-1'),
            m.fx(chips(gr_src('DraftKings', 'LAC −8.5 · O/U 47.5'), gr_src('Kalshi', 'LAC 73.5¢')), '2', d=2),
            m.fx(chips(m.chip('Touchdown ARI', 'mint', 'bell'), '<span class="s-quiet s-hide-sm">5-yard run · Q1 8:49</span>'), '3', d=3)),
    ]), '2', '--fd:.45s')
    game = m.fx(pitch + chance + market, '1-', 's-view', tag='div')
    body = '<div class="s-views">%s%s</div>' % (slate, game)
    floats = (note(m, 'spark', 'sky', 'Watch next', 'every pick names its reason', '0', 'tr')
              + note(m, 'field', '', 'Reported spots only', 'a missing spot is never guessed', '1', 'tr')
              + m.fx(m.chip('Gridiron never calculates a chance', 'ink'), '2', 's-float s-float--bl')
              + metric(m, '+5', 'ARI on this play, in ESPN’s model', '3', html=count(5, pre='+')))
    return window('field', 'ARI at LAC', 'Gridiron · NFL Week 1 replay', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# registry: key, group, steps, the step shown at rest, and what it says
# ----------------------------------------------------------------------------
STORIES = {
    'hero': dict(group='agents', n=3, rest=2, fn=hero,
                 label='Schematic interface: two production agents, I-Port and QT CoCo, cut expert work from hours to minutes; their typed actions wait at a human approval gate; offsets then settle multilaterally through LCH SwapAgent, $6.5T eligible under the same control model.'),
    'iport': dict(group='agents', n=3, rest=2, fn=iport,
                  label='Schematic interface: compression-run setup owned by senior engineering at 3.5 hours a run, then an agent with authorised live context and typed, reversible actions held for operator approval, then an 8-minute cycle in operations at three times the volume.'),
    'coco': dict(group='agents', n=3, rest=2, fn=coco,
                 label='Schematic interface: an incident that pages engineering by default, then run and ops evidence gathered through two MCP surfaces with six years of support knowledge, then a complete packet resolved in operations in 11 minutes, with escalations down 78%.'),
    'cross-currency': dict(group='markets', n=4, rest=3, fn=cross_currency,
                           label='Schematic interface: eighteen banks netting only in pairs, then a multilateral run settled through LCH SwapAgent, compressed with $6.5T of notional made eligible and 34% more reduction per run, each book inside its constraints.'),
    'valuation': dict(group='markets', n=3, rest=2, fn=valuation,
                      label='Schematic interface: an independent valuation beside internal marks before the live window, rows outside the tolerance band failing early, then locking only when both sources agree, 48 hours ahead of the live cycle.'),
    'fx-compression': dict(group='markets', n=3, rest=2, fn=fx_compression,
                           label='Schematic interface: an FX forwards and NDF book, then eligibility, ForexClear initial margin inside the optimizer and four agreeing sources gating each proposal before live, then acceptance measured across 40+ live runs.'),
    'platform': dict(group='agents', n=5, rest=4, fn=platform,
                     label='Schematic interface: five enterprise systems on one control plane, passing context through MCP servers and domain APIs, typed actions, deterministic services and a human approval gate, and finishing at shared evaluation baselines.'),
    'margin-simulator': dict(group='markets', n=4, rest=3, fn=margin_simulator,
                             label='Schematic interface: a current portfolio with known initial margin, a hypothetical trade outside the book, the same trade simulated across CME SPAN, ICE IRM and OTC, and incremental cost compared with standalone before execution.'),
    'ridelens': dict(group='labs', n=4, rest=3, fn=ridelens,
                     label='Illustrative interface: one trip mapped once on live roads across Uber, Lyft, Empower and Curb, and the same quotes ranked by price, soonest pickup or value, with upfront prices, ranges and estimates kept distinct and expired quotes never on top.'),
    'raildrop': dict(group='labs', n=4, rest=3, fn=raildrop,
                     label='Illustrative interface using RailDrop’s own sample board: a Boston to New York trip booked at $128, scans across the day before, the travel day and the day after, the board of four trains, and one email when Northeast Regional 95 lists at $47.'),
    'daylight': dict(group='labs', n=4, rest=3, fn=daylight,
                     label='Conceptual interface: the Balanced preset stepping from 6500 K by day to 2800 K at 23:30, a six-layer ladder deciding warmth and brightness separately, the sentence Daylight writes for the state, and a readback that separates asked, accepted and confirmed.'),
    'gridiron': dict(group='labs', n=4, rest=3, fn=gridiron,
                     label='Schematic interface using captured real games from Gridiron’s NFL Week 1 replay: six games live at once with Watch next naming why ARI at LAC deserves attention, ARI’s drive drawn from reported spots to 2nd and Goal at the LAC 5, ESPN win probability for LAC at 70% beside DraftKings’ closing lines and Kalshi at 73.5 cents, and the 5-yard touchdown run that follows.'),
}


def render(key, rest=None, attrs=''):
    st = STORIES[key]
    r = st['rest'] if rest is None else rest
    return stage(key, st['group'], st['n'], r, st['fn'](Mk(r)), st['label'], attrs)
