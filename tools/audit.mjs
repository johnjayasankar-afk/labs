// audit.mjs · opens every page of the built site in headless Chrome and reports
// what a reviewer would otherwise check by hand. Dev-only: tools/ is excluded
// from the deploy by .vercelignore. Node >= 22 (global WebSocket and fetch).
//
//   python3 tools/serve.py . 4400
//   node tools/audit.mjs http://127.0.0.1:4400
//
// Per page, at 1440, 1024, 768 and 390:
//   h1          exactly one h1
//   console     no error-level console message
//   network     no failed or 4xx/5xx request
//   overflow    no horizontal scroll (scrollWidth > clientWidth + 1)
//   alt         every img has an alt attribute (empty is fine, absent is not)
//
// Then, once per page at 1440:
//   reduced     the page renders with prefers-reduced-motion: reduce
//   forced      the page renders in forced-colors: active
//   print       the print stylesheet produces a page with visible text
//   nojs        the page renders with JavaScript disabled
//
// Exit status is 1 if anything failed. This file is byte-identical in the
// portfolio and Labs repositories.
import { spawn } from 'node:child_process';
import { mkdirSync, rmSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const BASE = (process.argv[2] || 'http://127.0.0.1:4400').replace(/\/$/, '');
const ROOT = new URL('..', import.meta.url).pathname;
const PORT = 9344;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const WIDTHS = [[1440, 900], [1024, 768], [768, 1024], [390, 844]];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function pages(dir = ROOT, out = []) {
  for (const name of readdirSync(dir).sort()) {
    if (name.startsWith('.') || name === 'node_modules' || name === 'tools') continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) pages(p, out);
    else if (name.endsWith('.html') && !name.startsWith('_')) {
      let rel = '/' + relative(ROOT, p).replace(/\\/g, '/');
      rel = rel.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
      out.push(rel === '' ? '/' : rel);
    }
  }
  return out;
}

const profile = join('/tmp', 'audit-profile-' + process.pid);
mkdirSync(profile, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--hide-scrollbars', '--mute-audio', 'about:blank'],
  { stdio: 'ignore' });

async function endpoint() {
  for (let i = 0; i < 100; i++) {
    try { return (await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json()).webSocketDebuggerUrl; }
    catch { await sleep(120); }
  }
  throw new Error('Chrome did not start');
}

function session(ws) {
  let id = 0;
  const waiting = new Map();
  const events = [];
  ws.addEventListener('message', (m) => {
    const msg = JSON.parse(m.data);
    if (msg.id && waiting.has(msg.id)) { waiting.get(msg.id)(msg); waiting.delete(msg.id); }
    else if (msg.method) events.push(msg);
  });
  const send = (method, params = {}, sessionId) => new Promise((res) => {
    const n = ++id;
    waiting.set(n, res);
    ws.send(JSON.stringify({ id: n, method, params, sessionId }));
  });
  return { send, events };
}

const fails = [];
const note = (page, what, detail) => {
  fails.push({ page, what, detail });
  console.log(`  FAIL  ${page}  ${what}: ${detail}`);
};

const wsUrl = await endpoint();
const ws = new WebSocket(wsUrl);
await new Promise((r) => ws.addEventListener('open', r));
const { send } = session(ws);

const paths = pages();
console.log(`${paths.length} pages, ${WIDTHS.length} widths, against ${BASE}\n`);

for (const path of paths) {
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' }).then((r) => r.result);
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true }).then((r) => r.result);
  const S = (m, p) => send(m, p, sessionId);
  await S('Page.enable'); await S('Runtime.enable'); await S('Log.enable'); await S('Network.enable');

  for (const [w, h] of WIDTHS) {
    const errs = [];
    const bad = [];
    const onMsg = (m) => {
      const msg = JSON.parse(m.data);
      if (msg.sessionId !== sessionId) return;
      if (msg.method === 'Log.entryAdded' && msg.params.entry.level === 'error') errs.push(msg.params.entry.text);
      if (msg.method === 'Runtime.exceptionThrown') errs.push(msg.params.exceptionDetails.text);
      if (msg.method === 'Network.loadingFailed') bad.push('load failed ' + msg.params.errorText);
      if (msg.method === 'Network.responseReceived' && msg.params.response.status >= 400)
        bad.push(msg.params.response.status + ' ' + msg.params.response.url);
    };
    ws.addEventListener('message', onMsg);
    await S('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: w < 768 });
    await S('Page.navigate', { url: BASE + path });
    await sleep(1400);
    const probe = await S('Runtime.evaluate', {
      expression: `JSON.stringify({
        h1: document.querySelectorAll('h1').length,
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        noAlt: [...document.images].filter(i => !i.hasAttribute('alt')).map(i => i.currentSrc || i.src).slice(0, 3),
        text: document.body.innerText.trim().length
      })`, returnByValue: true,
    });
    ws.removeEventListener('message', onMsg);
    const r = JSON.parse(probe.result.result.value);
    const label = `${path} @${w}`;
    if (r.h1 !== 1) note(label, 'h1', `${r.h1} h1 elements`);
    if (r.overflow > 1) note(label, 'overflow', `${r.overflow}px of horizontal scroll`);
    if (r.noAlt.length) note(label, 'alt', `${r.noAlt.length} image(s) without alt: ${r.noAlt[0]}`);
    if (errs.length) note(label, 'console', errs[0].slice(0, 120));
    if (bad.length) note(label, 'network', bad[0].slice(0, 120));
    if (r.text < 200) note(label, 'empty', `only ${r.text} characters of text`);
  }

  // once per page, at 1440
  await S('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  for (const [mode, features] of [
    ['reduced', [{ name: 'prefers-reduced-motion', value: 'reduce' }]],
    ['forced', [{ name: 'forced-colors', value: 'active' }]],
    ['print', null],
  ]) {
    if (mode === 'print') await S('Emulation.setEmulatedMedia', { media: 'print' });
    else await S('Emulation.setEmulatedMedia', { media: '', features });
    await S('Page.navigate', { url: BASE + path });
    await sleep(900);
    const t = await S('Runtime.evaluate', {
      expression: 'document.body.innerText.trim().length', returnByValue: true,
    });
    if ((t.result.result.value || 0) < 200) note(path, mode, `only ${t.result.result.value} characters of text`);
  }
  await S('Emulation.setEmulatedMedia', { media: '', features: [] });

  await S('Emulation.setScriptExecutionDisabled', { value: true });
  await S('Page.navigate', { url: BASE + path });
  await sleep(700);
  const nojs = await S('Runtime.evaluate', {
    expression: 'document.body.innerText.trim().length', returnByValue: true,
  });
  if ((nojs.result.result.value || 0) < 200) note(path, 'nojs', `only ${nojs.result.result.value} characters of text`);
  await S('Emulation.setScriptExecutionDisabled', { value: false });

  await send('Target.closeTarget', { targetId });
  if (!fails.some((f) => f.page.startsWith(path))) console.log(`  ok    ${path}`);
}

console.log(`\n${paths.length - new Set(fails.map((f) => f.page.split(' @')[0])).size} of ${paths.length} pages clean.`);
if (fails.length) console.log(`${fails.length} problem(s).`);
ws.close();
chrome.kill();
// Chrome is still flushing its profile when kill() returns, so the first rm
// can lose a race with it. Retry briefly, then leave it: a stray temp profile
// is not worth failing an otherwise clean audit over.
for (let i = 0; i < 20; i++) {
  try { rmSync(profile, { recursive: true, force: true }); break; }
  catch { await sleep(100); }
}
process.exit(fails.length ? 1 : 0);
