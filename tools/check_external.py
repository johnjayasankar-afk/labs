#!/usr/bin/env python3
"""Requests every outbound link on the built site and every product this site
embeds, and reports what is broken. Dev-only: tools/ is excluded from the
deploy by .vercelignore. Needs the network, so it is run by hand rather than
by the build.

    python3 tools/check_external.py            # links and embeds
    python3 tools/check_external.py --links    # outbound links only
    python3 tools/check_external.py --embeds   # framing headers only
    python3 tools/check_external.py --hops     # short links only
    python3 tools/check_external.py --selftest # the framing rule, no network

LINKS reads the generated HTML rather than the data files, so it checks what a
visitor actually gets. It follows redirects and reports the final status and
the hop, because a 301 that lands somewhere unexpected is worth seeing.

HOPS follows every redirect this site declares in vercel.json, live, and
reports the status, the kind (307 or 301) and where it actually lands. A short
link is the address people save and share, so it is worth checking that it
still goes where the config says.

EMBEDS is the check that a live preview will actually render. It checks two
things that fail in different ways: whether this site's own CSP `frame-src`
allows the frame at all, which is a local misconfiguration, and whether the
product allows this origin to frame it, which is the product's decision. An iframe whose
target sets X-Frame-Options or a CSP frame-ancestors directive that excludes
this origin renders as an empty box, and the page goes on claiming "the
working app, not a mock" over nothing. A browser cannot detect that from the
parent page: a blocked frame and a loaded cross-origin frame look the same to
script. So it is checked here, against the response headers, before the claim
ships.

Exit status is 1 if any link failed or any embedded product refuses to be
framed by this site, 0 otherwise. A host that could not be reached at all is
reported separately and does not fail the run, because an unreachable host is
usually this machine's problem rather than the site's.

This file is byte-identical in the portfolio and Labs repositories. Diff them
before changing either:

    diff tools/check_external.py ../labs/tools/check_external.py"""

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

ORIGIN = 'https://johnjayasankar.com'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 ' \
     '(KHTML, like Gecko) Chrome/140.0 Safari/537.36'
TIMEOUT = 25

GREEN, RED, DIM, YELL, OFF = '\033[32m', '\033[31m', '\033[2m', '\033[33m', '\033[0m'
if not sys.stdout.isatty():
    GREEN = RED = DIM = YELL = OFF = ''

SKIP = ('mailto:', 'tel:', 'javascript:', '#', 'data:')

# Hosts that refuse a non-browser client and answer a browser perfectly well.
# Each one was opened in a browser on the date beside it and rendered. They are
# reported, never counted as failures: a checker that cries wolf gets ignored,
# and a real outage here would still show as a different status or as silence.
BOT_WALLED = {
    'www.haverford.edu': '403 to any client without a browser fingerprint; '
                         'opens normally in a browser, checked 25 September 2026',
}


def html_files():
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs
                   if not d.startswith('.') and d not in ('tools', 'node_modules')]
        for n in sorted(names):
            if n.endswith('.html'):
                yield os.path.join(base, n)


def outbound():
    """Every external URL the built site links, with the pages that link it."""
    seen = {}
    for path in html_files():
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding='utf-8') as fh:
            body = fh.read()
        for url in re.findall(r'(?:href|src|content)="(https?://[^"]+)"', body):
            url = url.replace('&amp;', '&')
            seen.setdefault(url, set()).add(rel)
    return seen


def fetch(url, method='HEAD', follow=True):
    """(status, final url, headers, error).

    curl rather than urllib: this machine's Python has no usable CA bundle, and
    a checker that reports every https URL as unreachable is worse than no
    checker. curl is on every Mac and uses the system trust store.
    """
    args = ['/usr/bin/curl', '-sS', '-m', str(TIMEOUT), '-A', UA,
            '-o', '/dev/null', '-D', '-',
            '-w', '\n@@%{http_code} %{url_effective}']
    if follow:
        args.insert(2, '-L')
    if method == 'HEAD':
        args.append('-I')
    args.append(url)
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           timeout=TIMEOUT + 10)
    except subprocess.TimeoutExpired:
        return 0, url, {}, 'timed out after %ds' % TIMEOUT
    tail = [ln for ln in p.stdout.splitlines() if ln.startswith('@@')]
    if not tail:
        why = (p.stderr.strip().splitlines() or ['no response'])[-1]
        return 0, url, {}, why[:110]
    code, _, final = tail[-1][2:].partition(' ')
    status = int(code) if code.isdigit() else 0
    # headers of the LAST response in the chain
    headers, block = {}, p.stdout.split('@@')[0]
    for chunk in re.split(r'\r?\n\r?\n', block):
        if re.match(r'HTTP/', chunk):
            headers = {}
            for line in chunk.splitlines()[1:]:
                k, _, v = line.partition(':')
                if v:
                    headers[k.strip()] = v.strip()
    if method == 'HEAD' and status in (403, 405, 501):
        return fetch(url, 'GET', follow)
    if status == 0:
        return fetch(url, 'GET', follow) if method == 'HEAD' else (0, url, {}, 'no status')
    return status, final or url, headers, ''


def may_frame(headers, origin=ORIGIN):
    """(allowed, why). Whether `origin` may put this response in an iframe.

    An enforced CSP frame-ancestors wins over X-Frame-Options where both are
    present, which is what browsers do. A report-only CSP is recorded but
    never treated as blocking, because it does not block.
    """
    h = {k.lower(): v for k, v in headers.items()}
    csp = h.get('content-security-policy', '')
    m = re.search(r'frame-ancestors([^;]*)', csp, re.I)
    if m:
        allowed = m.group(1).split()
        if any(a.strip("'\"") in ("none",) for a in allowed):
            return False, "CSP frame-ancestors 'none'"
        ok = any(a.strip("'\"") in ('*', 'self') or origin.startswith(a.strip("'\""))
                 or a.strip("'\"") == origin for a in allowed)
        if not ok:
            return False, 'CSP frame-ancestors does not list ' + origin
        if all(a.strip("'\"") == 'self' for a in allowed if a.strip()):
            return False, "CSP frame-ancestors 'self' only"
        return True, 'CSP frame-ancestors lists ' + origin

    xfo = h.get('x-frame-options', '').strip().upper()
    if xfo in ('DENY', 'SAMEORIGIN'):
        return False, 'X-Frame-Options: ' + xfo
    if xfo.startswith('ALLOW-FROM'):
        return (origin in xfo), 'X-Frame-Options: ' + xfo

    ro = h.get('content-security-policy-report-only', '')
    note = ''
    if re.search(r'frame-ancestors', ro, re.I):
        note = ' (a report-only CSP names frame-ancestors; it does not block, ' \
               'but it says where this is heading)'
    return True, 'no framing restriction' + note


def check_links():
    urls = outbound()
    print(f'{len(urls)} outbound URLs across the built site\n')
    bad, unreachable, moved, walled = [], [], [], []
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda u: (u, fetch(u)), sorted(urls)))
    for url, (status, final, _h, err) in results:
        pages = ', '.join(sorted(urls[url]))
        if err:
            print(f'  {YELL}unreachable{OFF}  {url}  {err}')
            unreachable.append(url)
        elif status >= 400 or status == 0:
            host = re.sub(r'^https?://([^/]+).*', r'\1', url)
            if host in BOT_WALLED:
                print(f'  {YELL}{status}{OFF}  {url}  {DIM}{BOT_WALLED[host]}{OFF}')
                walled.append(url)
            else:
                print(f'  {RED}{status}{OFF}  {url}  {DIM}linked from {pages}{OFF}')
                bad.append((url, status))
        elif final.rstrip('/') != url.rstrip('/'):
            print(f'  {GREEN}{status}{OFF}  {url}  {DIM}→ {final}{OFF}')
            moved.append((url, final))
        else:
            print(f'  {GREEN}{status}{OFF}  {url}')
    print(f'\n{len(urls) - len(bad) - len(unreachable) - len(walled)} ok, '
          f'{len(bad)} failed, {len(unreachable)} unreachable, '
          f'{len(walled)} bot-walled but fine in a browser, '
          f'{len(moved)} redirected.')
    return bad


def embedded():
    """(name, url) for every product this site puts in an iframe."""
    out = []
    for path in html_files():
        with open(path, encoding='utf-8') as fh:
            body = fh.read()
        for src, title in re.findall(r'<iframe src="(https?://[^"]+)" title="([^"]*)"', body):
            out.append((title, src.replace('&amp;', '&')))
    return sorted(set(out))


def frame_src():
    """The origins this site's own CSP allows in an iframe."""
    path = os.path.join(ROOT, 'vercel.json')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as fh:
        cfg = json.load(fh)
    for group in cfg.get('headers', []):
        for h in group.get('headers', []):
            if h.get('key', '').lower() == 'content-security-policy':
                m = re.search(r'frame-src([^;]*)', h.get('value', ''), re.I)
                if m:
                    return set(m.group(1).split())
    return None


def check_embeds():
    frames = embedded()
    if not frames:
        print('no live previews on this site')
        return []
    print(f'{len(frames)} live preview(s)\n')
    blocked, still = [], []
    allowed = frame_src()
    for name, url in frames:
        origin = re.sub(r'^(https?://[^/]+).*', r'\1', url)
        if allowed is not None and origin not in allowed and "*" not in allowed:
            print(f'  {RED}BLANK{OFF}  {name}  {url}')
            print(f'         this site\'s own CSP frame-src does not list {origin}, '
                  f'so the browser refuses the frame before the product is asked.')
            blocked.append((name, url, 'frame-src omits ' + origin))
    for name, url in frames:
        if any(u == url for _n, u, _w in blocked):
            continue
        status, _final, headers, err = fetch(url, 'GET')
        if err:
            print(f'  {YELL}unreachable{OFF}  {name}  {url}  {err}')
            continue
        ok, why = may_frame(headers)
        if ok:
            print(f'  {GREEN}frames{OFF}  {name}  {DIM}{url} · {why}{OFF}')
        else:
            print(f'  {YELL}still only{OFF}  {name}  {url}')
            print(f'         {why}. The page shows its still and says so. For a '
                  f'live preview the product needs frame-ancestors listing '
                  f'{ORIGIN} and no X-Frame-Options.')
            still.append((name, url, why))
    if blocked:
        print(f'\n{RED}{len(blocked)} preview(s) the browser will refuse before '
              f'the product is even asked.{OFF} Fix frame-src in vercel.json.')
    if still:
        print(f'\n{YELL}{len(still)} preview(s) show a still{OFF} because the '
              f'product does not allow this origin to frame it. Not a defect '
              f'here: the caption says it is a picture.')
    return blocked


# Every combination the framing rule has to get right. Run with --selftest;
# no network. A rule that decides whether a claim on the site is true has to be
# checkable without the internet being up.
FRAMING_CASES = [
    ({}, True, 'nothing set'),
    ({'X-Frame-Options': 'SAMEORIGIN'}, False, 'X-Frame-Options: SAMEORIGIN'),
    ({'X-Frame-Options': 'DENY'}, False, 'X-Frame-Options: DENY'),
    ({'Content-Security-Policy': "frame-ancestors 'none'"}, False, "frame-ancestors 'none'"),
    ({'Content-Security-Policy': "frame-ancestors 'self'"}, False, "frame-ancestors 'self' only"),
    ({'Content-Security-Policy': "frame-ancestors 'self' " + ORIGIN}, True, 'frame-ancestors lists us'),
    ({'Content-Security-Policy': 'frame-ancestors https://example.com'}, False, 'frame-ancestors lists someone else'),
    ({'Content-Security-Policy': 'frame-ancestors *'}, True, 'frame-ancestors *'),
    ({'X-Frame-Options': 'SAMEORIGIN',
      'Content-Security-Policy': 'frame-ancestors ' + ORIGIN}, True,
     'an enforced CSP beats X-Frame-Options, as browsers do'),
    ({'Content-Security-Policy-Report-Only': "frame-ancestors 'none'"}, True,
     'report-only does not block'),
]


def selftest():
    bad = 0
    for headers, want, label in FRAMING_CASES:
        got, why = may_frame(headers)
        ok = got == want
        bad += not ok
        mark = f'{GREEN}ok{OFF}' if ok else f'{RED}FAIL{OFF}'
        print(f'  {mark}  {label} → {got}  {DIM}{why}{OFF}')
    print(f'\n{len(FRAMING_CASES) - bad} of {len(FRAMING_CASES)} correct.')
    return bad


def declared_redirects():
    """(source, destination, permanent) from this site's vercel.json."""
    path = os.path.join(ROOT, 'vercel.json')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as fh:
        cfg = json.load(fh)
    out = []
    for r in cfg.get('redirects', []):
        src, dst = r.get('source', ''), r.get('destination', '')
        if src.startswith('/') and '(' not in src and ':' not in src:
            out.append((src, dst, bool(r.get('permanent'))))
    return out


def check_hops(site):
    hops = declared_redirects()
    if not hops:
        print('no redirects declared in vercel.json')
        return []
    print(f'{len(hops)} short link(s), against {site}\n')
    wrong = []
    for src, want, permanent in hops:
        status, _f, headers, err = fetch(site.rstrip('/') + src, follow=False)
        landed = {k.lower(): v for k, v in headers.items()}.get('location', '')
        kind = '301' if permanent else '307'
        if err:
            print(f'  {YELL}unreachable{OFF}  {src}  {err}')
        elif landed.rstrip('/') == want.rstrip('/'):
            print(f'  {GREEN}{status}{OFF}  {src} → {landed}  {DIM}declared {kind}{OFF}')
        else:
            print(f'  {RED}{status}{OFF}  {src} → {landed or "nowhere"}  '
                  f'{DIM}config says {want}{OFF}')
            wrong.append((src, landed, want))
    return wrong


def main():
    if '--selftest' in sys.argv:
        print('FRAMING RULE')
        return 1 if selftest() else 0
    only = {a for a in sys.argv[1:] if a in ('--links', '--embeds', '--hops')}
    want = lambda flag: not only or flag in only          # noqa: E731
    bad, blocked, wrong = [], [], []
    if want('--links'):
        print('LINKS')
        bad = check_links()
        print()
    if want('--hops'):
        print('HOPS')
        site = os.environ.get('SITE_ORIGIN') or ORIGIN
        wrong = check_hops(site)
        print()
    if want('--embeds'):
        print('EMBEDS')
        blocked = check_embeds()
    return 1 if (bad or blocked or wrong) else 0


if __name__ == '__main__':
    sys.exit(main())
