#!/usr/bin/env python3
"""Local stand-in for Vercel: cleanUrls, trailingSlash:false, the redirects and
headers from vercel.json (so a build's short link and CSP violations behave as
they will live), 404.html with a real 404, and an optional POST sink for test
harnesses.

  python3 serve.py <site-root> <port> [sink-dir]

Without a sink dir, POST answers 405, which is how the final server runs."""
import http.server, json, os, re, sys, base64, urllib.parse

ROOT = os.path.abspath(sys.argv[1])
PORT = int(sys.argv[2])
SINK = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else None

TYPES = {
    '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8', '.json': 'application/json',
    '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.webp': 'image/webp', '.woff2': 'font/woff2', '.pdf': 'application/pdf',
    '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8', '.ico': 'image/x-icon',
    '.webmanifest': 'application/manifest+json',
}


def load_rules():
    try:
        cfg = json.load(open(os.path.join(ROOT, 'vercel.json')))
    except Exception:
        return []
    rules = []
    for h in cfg.get('headers', []):
        parts = re.split(r'(\([^)]*\))', h['source'])
        rx = ''.join(p if p.startswith('(') else re.escape(p) for p in parts)
        rules.append((re.compile('^' + rx + '$'), h['headers']))
    return rules


def load_redirects():
    try:
        cfg = json.load(open(os.path.join(ROOT, 'vercel.json')))
    except Exception:
        return {}
    return {r['source']: (r['destination'], 308 if r.get('permanent', True) else 307) for r in cfg.get('redirects', [])}


class H(http.server.BaseHTTPRequestHandler):
    server_version = 'jj-local'

    def log_message(self, *a):
        pass

    def _resolve(self, path):
        if path == '/':
            return os.path.join(ROOT, 'index.html'), 200
        rel = path.lstrip('/')
        full = os.path.normpath(os.path.join(ROOT, rel))
        if not full.startswith(ROOT):
            return None, 404
        if os.path.isfile(full):
            return full, 200
        if os.path.isfile(full + '.html'):
            return full + '.html', 200
        return os.path.join(ROOT, '404.html'), 404

    def _send(self, head_only=False):
        u = urllib.parse.urlsplit(self.path)
        path = urllib.parse.unquote(u.path)
        # trailingSlash:false and cleanUrls both redirect rather than serve twice
        if len(path) > 1 and path.endswith('/'):
            return self._redirect(path.rstrip('/'), u.query)
        hop = load_redirects().get(path)   # re-read, like the headers
        if hop:
            self.send_response(hop[1])
            self.send_header('Location', hop[0])
            self.end_headers()
            return
        if path.endswith('.html') and path != '/404.html':
            clean = path[:-5]
            if clean.endswith('/index'):
                clean = clean[:-6] or '/'
            return self._redirect(clean or '/', u.query)
        full, code = self._resolve(path)
        if not full or not os.path.isfile(full):
            self.send_response(404); self.end_headers(); return
        body = open(full, 'rb').read()
        self.send_response(code)
        ext = os.path.splitext(full)[1].lower()
        self.send_header('Content-Type', TYPES.get(ext, 'application/octet-stream'))
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        for rx, hs in load_rules():   # re-read so a vercel.json edit applies without a restart
            if rx.match(path):
                for kv in hs:
                    if kv['key'].lower() in ('cache-control', 'strict-transport-security'):
                        continue
                    if kv['key'] == 'Content-Security-Policy':
                        # localhost is plain http: upgrade-insecure-requests would break it
                        self.send_header(kv['key'], kv['value'].replace('; upgrade-insecure-requests', ''))
                    else:
                        self.send_header(kv['key'], kv['value'])
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _redirect(self, to, query):
        self.send_response(308)
        self.send_header('Location', to + ('?' + query if query else ''))
        self.end_headers()

    def do_GET(self):
        self._send()

    def do_HEAD(self):
        self._send(head_only=True)

    def do_POST(self):
        u = urllib.parse.urlsplit(self.path)
        if not SINK or u.path != '/__sink':
            self.send_response(405); self.end_headers(); return
        q = urllib.parse.parse_qs(u.query)
        name = re.sub(r'[^A-Za-z0-9._-]', '_', (q.get('name') or ['payload'])[0])
        n = int(self.headers.get('Content-Length') or 0)
        data = self.rfile.read(n)
        os.makedirs(SINK, exist_ok=True)
        if data.startswith(b'data:image/'):
            data = base64.b64decode(data.split(b',', 1)[1])
        with open(os.path.join(SINK, name), 'wb') as f:
            f.write(data)
        self.send_response(204); self.end_headers()


RULES = load_rules()
http.server.ThreadingHTTPServer.allow_reuse_address = True
http.server.ThreadingHTTPServer.request_queue_size = 128
http.server.ThreadingHTTPServer.daemon_threads = True
print('serving', ROOT, 'on', PORT, 'sink' if SINK else 'no sink', flush=True)
http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
