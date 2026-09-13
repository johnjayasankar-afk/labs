// shoot.mjs · a minimal Chrome DevTools Protocol driver (Node >= 22: global
// WebSocket and fetch). Real time, one tab per job, so requestAnimationFrame
// and IntersectionObserver behave the way they do for a person.
//
//   node shoot.mjs jobs.json
//
// jobs.json: { base, out, port?, reduced?, dsf?, jobs: [{ name, path, w, h,
//   mobile?, dsf?, wait?, eval?, shots: [{ y?, js?, wait?, full?, dsf?, max? }] }] }
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';

const cfg = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const PORT = cfg.port || 9333;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const profile = join(cfg.out, '.profile-' + process.pid);
mkdirSync(cfg.out, { recursive: true });

const args = ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, '--no-first-run',
  '--no-default-browser-check', '--disable-extensions', '--hide-scrollbars', '--mute-audio', '--window-size=1440,900'];
if (cfg.reduced) args.push('--force-prefers-reduced-motion');
const chrome = spawn(CHROME, [...args, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function devtools(path, method = 'GET') {
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}${path}`, { method });
      if (r.ok) return await r.json();
    } catch (e) { /* not up yet */ }
    await sleep(150);
  }
  throw new Error('devtools endpoint not reachable: ' + path);
}

class CDP {
  constructor(url) { this.ws = new WebSocket(url); this.id = 0; this.pending = new Map(); this.handlers = []; }
  open() {
    return new Promise((res, rej) => {
      this.ws.onopen = () => res();
      this.ws.onerror = (e) => rej(e);
      this.ws.onmessage = (m) => this.dispatch(JSON.parse(typeof m.data === 'string' ? m.data : m.data.toString()));
    });
  }
  dispatch(msg) {
    if (msg.id && this.pending.has(msg.id)) {
      const { res, rej } = this.pending.get(msg.id);
      this.pending.delete(msg.id);
      if (msg.error) rej(new Error(msg.error.message)); else res(msg.result);
    } else if (msg.method) {
      for (const h of [...this.handlers]) h(msg);
    }
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((res, rej) => this.pending.set(id, { res, rej }));
  }
  on(fn) { this.handlers.push(fn); }
  once(method, timeout = 20000) {
    return new Promise((res) => {
      const h = (m) => { if (m.method === method) { clearTimeout(t); this.handlers = this.handlers.filter((x) => x !== h); res(m.params); } };
      const t = setTimeout(() => { this.handlers = this.handlers.filter((x) => x !== h); res(null); }, timeout);
      this.handlers.push(h);
    });
  }
}

const report = [];
try {
  await devtools('/json/version');
  for (const job of cfg.jobs) {
    const target = await devtools('/json/new?about:blank', 'PUT');
    const c = new CDP(target.webSocketDebuggerUrl);
    await c.open();
    const logs = [];
    c.on((m) => {
      if (m.method === 'Runtime.consoleAPICalled' && ['error', 'warning', 'assert'].includes(m.params.type)) {
        logs.push(m.params.type + ': ' + m.params.args.map((a) => a.value ?? a.description ?? '').join(' '));
      }
      if (m.method === 'Runtime.exceptionThrown') {
        const d = m.params.exceptionDetails;
        logs.push('exception: ' + ((d.exception && d.exception.description) || d.text) + ' @' + (d.url || '') + ':' + d.lineNumber);
      }
      if (m.method === 'Log.entryAdded' && ['error', 'warning'].includes(m.params.entry.level)) {
        logs.push('log/' + m.params.entry.source + ': ' + m.params.entry.text + (m.params.entry.url ? ' ' + m.params.entry.url : ''));
      }
    });
    await c.send('Page.enable');
    await c.send('Runtime.enable');
    await c.send('Log.enable');
    const dsf = job.dsf || cfg.dsf || 1;
    const metrics = (h, d) => c.send('Emulation.setDeviceMetricsOverride', { width: job.w, height: h, deviceScaleFactor: d, mobile: !!job.mobile });
    await metrics(job.h, dsf);
    if (job.mobile) await c.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
    const loaded = c.once('Page.loadEventFired');
    await c.send('Page.navigate', { url: cfg.base + job.path });
    await loaded;
    await sleep(job.wait ?? 2500);
    const result = { name: job.name, path: job.path, w: job.w, h: job.h, files: [] };
    if (job.eval) {
      const r = await c.send('Runtime.evaluate', { expression: job.eval, returnByValue: true, awaitPromise: true });
      result.eval = r.exceptionDetails ? 'EVAL ERROR: ' + (r.exceptionDetails.exception?.description || r.exceptionDetails.text) : r.result.value;
    }
    const shots = job.shots || [{ y: 0 }];
    for (let i = 0; i < shots.length; i++) {
      const s = shots[i];
      if (s.js) await c.send('Runtime.evaluate', { expression: s.js, awaitPromise: true });
      const file = join(cfg.out, `${job.name}-${i}.png`);
      if (s.full) {
        const hr = await c.send('Runtime.evaluate', { expression: `Math.min(document.documentElement.scrollHeight, ${s.max || 16000})`, returnByValue: true });
        await metrics(hr.result.value, s.dsf || dsf);
        await sleep(s.wait ?? 2500);
        const shot = await c.send('Page.captureScreenshot', { format: 'png' });
        writeFileSync(file, Buffer.from(shot.data, 'base64'));
        await metrics(job.h, dsf);
      } else {
        if (s.y != null) await c.send('Runtime.evaluate', { expression: `window.scrollTo({ top: ${s.y}, behavior: 'instant' })` });
        await sleep(s.wait ?? 1000);
        const shot = await c.send('Page.captureScreenshot', { format: 'png' });
        writeFileSync(file, Buffer.from(shot.data, 'base64'));
      }
      result.files.push(file);
      if (s.eval) {
        const r = await c.send('Runtime.evaluate', { expression: s.eval, returnByValue: true, awaitPromise: true });
        result['eval' + i] = r.exceptionDetails ? 'EVAL ERROR' : r.result.value;
      }
    }
    result.logs = logs;
    report.push(result);
    try { await c.send('Page.close'); } catch (e) { /* closing */ }
    try { c.ws.close(); } catch (e) { /* closed */ }
    console.log('done', job.name, logs.length ? `(${logs.length} console entries)` : '');
  }
} catch (e) {
  console.error('harness error:', e.message);
} finally {
  writeFileSync(join(cfg.out, 'report.json'), JSON.stringify(report, null, 2));
  chrome.kill('SIGTERM');
  await sleep(600);
  try { chrome.kill('SIGKILL'); } catch (e) { /* gone */ }
  try { rmSync(profile, { recursive: true, force: true }); } catch (e) { /* busy */ }
}
