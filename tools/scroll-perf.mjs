// scroll-perf.mjs · measures what scrolling actually costs, so a change can be
// shown to help rather than assumed to. Dev-only: tools/ is excluded from the
// deploy by .vercelignore. Node >= 22 (global WebSocket and fetch).
//
//   python3 tools/serve.py . 4400
//   node tools/scroll-perf.mjs http://127.0.0.1:4400 [/path ...]
//   node tools/scroll-perf.mjs <baseA> <baseB> [/path ...]   # interleaved A/B
//   CPU=4 node tools/scroll-perf.mjs http://127.0.0.1:4400      # throttled
//
// CPU throttling is the important one. This machine holds 60fps on every page
// of both sites without trying, which hides every cost that matters on the
// laptop someone actually reads this on. At CPU=4 the work shows up.
//
// Per page it drives a real scroll gesture through the compositor
// (Input.synthesizeScrollGesture, the same path Chrome's own Telemetry uses)
// and records, from inside the page:
//
//   frames      requestAnimationFrame intervals while the gesture runs
//   late        frames over 16.7ms, and over 33ms, which is a visible stutter
//   longtasks   main-thread tasks over 50ms, which is what drops those frames
//   layout      Chrome's own LayoutCount and RecalcStyleCount deltas
//
// Numbers from one run on a busy machine mean very little. Give it two origins
// and it alternates between them, round by round, in one browser: build the
// change into one copy of the site, serve both, and compare. That interleaving
// is the point. Two measurements of the SAME build, taken one after the other,
// have differed here by a third.
//
// It prints the spread beside every median. **If the two ranges overlap, the
// result said nothing** and the only honest moves are more rounds or a quieter
// machine. Of six candidate improvements measured this way, five turned out to
// be noise that a single run had made look real, and the sixth measured better
// because it had quietly stopped the effect from running at all. So: read the
// result, not the counter. Check the thing still does what it did.
//
// This file is byte-identical in the portfolio and Labs repositories.
import { spawn } from 'node:child_process';
import { mkdirSync, rmSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

const ORIGINS = process.argv.slice(2).filter((a) => a.startsWith('http')).map((a) => a.replace(/\/$/, ''));
const BASE = ORIGINS[0] || 'http://127.0.0.1:4400';
const AB = ORIGINS.length > 1 ? ORIGINS[1] : null;
const ARGS = process.argv.slice(2).filter((a) => a.startsWith('/'));
const RUNS = Number(process.env.RUNS || 3);
const CPU = Number(process.env.CPU || 1);
const ROOT = new URL('..', import.meta.url).pathname;
const PORT = 9355;
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function pages(dir = ROOT, out = []) {
  for (const name of readdirSync(dir).sort()) {
    if (name.startsWith('.') || name === 'node_modules' || name === 'tools') continue;
    const p = join(dir, name);
    if (statSync(p).isDirectory()) pages(p, out);
    else if (name.endsWith('.html') && !name.startsWith('_') && name !== '404.html') {
      let rel = '/' + relative(ROOT, p).replace(/\\/g, '/');
      out.push(rel.replace(/\/index\.html$/, '/').replace(/\.html$/, '') || '/');
    }
  }
  return out;
}

const profile = join('/tmp', 'perf-profile-' + process.pid);
mkdirSync(profile, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check',
  '--disable-extensions', '--hide-scrollbars', '--mute-audio',
  '--window-size=1440,900', 'about:blank'], { stdio: 'ignore' });

async function endpoint() {
  for (let i = 0; i < 100; i++) {
    try { return (await (await fetch(`http://127.0.0.1:${PORT}/json/version`)).json()).webSocketDebuggerUrl; }
    catch { await sleep(120); }
  }
  throw new Error('Chrome did not start');
}

const ws = new WebSocket(await endpoint());
await new Promise((r) => ws.addEventListener('open', r));
let seq = 0;
const waiting = new Map();
ws.addEventListener('message', (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && waiting.has(msg.id)) { waiting.get(msg.id)(msg); waiting.delete(msg.id); }
});
const send = (method, params = {}, sessionId) => new Promise((res) => {
  const n = ++seq;
  waiting.set(n, res);
  ws.send(JSON.stringify({ id: n, method, params, sessionId }));
});

const RECORDER = `(() => {
  window.__perf = { frames: [], long: [], done: false };
  let last = performance.now();
  const tick = (t) => {
    window.__perf.frames.push(t - last);
    last = t;
    if (!window.__perf.done) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  try {
    new PerformanceObserver((l) => {
      for (const e of l.getEntries()) window.__perf.long.push(Math.round(e.duration));
    }).observe({ type: 'longtask', buffered: true });
  } catch (e) { /* not every build reports long tasks */ }
})()`;

const pct = (a, p) => (a.length ? a.slice().sort((x, y) => x - y)[Math.min(a.length - 1, Math.floor(a.length * p))] : 0);

async function measure(path, base = BASE) {
  const { targetId } = await send('Target.createTarget', { url: 'about:blank' }).then((r) => r.result);
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true }).then((r) => r.result);
  const S = (m, p) => send(m, p, sessionId);
  await S('Page.enable'); await S('Runtime.enable'); await S('Performance.enable');
  await S('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  if (CPU > 1) await S('Emulation.setCPUThrottlingRate', { rate: CPU });
  await S('Page.navigate', { url: base + path });
  await sleep(2200);

  const height = await S('Runtime.evaluate', {
    expression: 'document.documentElement.scrollHeight', returnByValue: true,
  }).then((r) => r.result.result.value);

  const before = await S('Performance.getMetrics').then((r) =>
    Object.fromEntries(r.result.metrics.map((m) => [m.name, m.value])));
  await S('Runtime.evaluate', { expression: RECORDER });

  // one long gesture through the compositor, top to bottom
  await S('Input.synthesizeScrollGesture', {
    x: 720, y: 450, xDistance: 0, yDistance: -(height - 900),
    speed: 1400, gestureSourceType: 'mouse', repeatCount: 0,
  });
  await sleep(400);

  const after = await S('Performance.getMetrics').then((r) =>
    Object.fromEntries(r.result.metrics.map((m) => [m.name, m.value])));
  const perf = await S('Runtime.evaluate', {
    expression: 'window.__perf.done = true; JSON.stringify(window.__perf)', returnByValue: true,
  }).then((r) => JSON.parse(r.result.result.value));

  await send('Target.closeTarget', { targetId });

  const f = perf.frames.slice(2).filter((x) => x > 0 && x < 2000);
  return {
    path,
    frames: f.length,
    p50: +pct(f, 0.5).toFixed(1),
    p95: +pct(f, 0.95).toFixed(1),
    worst: +Math.max(0, ...f).toFixed(1),
    over17: f.filter((x) => x > 16.7).length,
    over33: f.filter((x) => x > 33).length,
    longtasks: perf.long.length,
    longestTask: perf.long.length ? Math.max(...perf.long) : 0,
    layouts: Math.round((after.LayoutCount || 0) - (before.LayoutCount || 0)),
    restyles: Math.round((after.RecalcStyleCount || 0) - (before.RecalcStyleCount || 0)),
    layoutMs: +(((after.LayoutDuration || 0) - (before.LayoutDuration || 0)) * 1000).toFixed(1),
    styleMs: +(((after.RecalcStyleDuration || 0) - (before.RecalcStyleDuration || 0)) * 1000).toFixed(1),
  };
}

const paths = ARGS.length ? ARGS : pages();
const median = (a) => a.slice().sort((x, y) => x - y)[Math.floor(a.length / 2)];

if (AB) {
  console.log(`${paths.length} page(s), ${RUNS} interleaved rounds` +
    (CPU > 1 ? `, CPU throttled ${CPU}x` : '') + `\n  A = ${BASE}\n  B = ${AB}\n`);
  for (const path of paths) {
    const a = [], b = [];
    for (let i = 0; i < RUNS; i++) { a.push(await measure(path, BASE)); b.push(await measure(path, AB)); }
    console.log(`  ${path}`);
    for (const key of ['p95', 'over33', 'longtasks', 'layoutMs', 'styleMs']) {
      const ga = a.map((x) => x[key]), gb = b.map((x) => x[key]);
      const ma = median(ga), mb = median(gb);
      const delta = ma ? ((mb - ma) / ma) * 100 : 0;
      const lo = Math.min(...ga), hi = Math.max(...ga), lo2 = Math.min(...gb), hi2 = Math.max(...gb);
      const overlaps = lo2 <= hi && lo <= hi2;
      const verdict = overlaps ? 'says nothing, the ranges overlap'
        : (delta < 0 ? 'BETTER' : 'WORSE');
      console.log(`    ${key.padEnd(10)} A ${String(ma).padStart(7)} [${lo}..${hi}]` +
        `   B ${String(mb).padStart(7)} [${lo2}..${hi2}]   ${delta >= 0 ? '+' : ''}${delta.toFixed(0)}%  ${verdict}`);
    }
    console.log('');
  }
} else {
  console.log(`${paths.length} page(s), ${RUNS} run(s) each, 1440x900` +
    (CPU > 1 ? `, CPU throttled ${CPU}x` : '') + `, against ${BASE}\n`);
  console.log('  page                      p50    p95   worst  >17ms >33ms  tasks  layout  style');
  console.log('  ' + '-'.repeat(84));
  const all = [];
  for (const path of paths) {
    const runs = [];
    for (let i = 0; i < RUNS; i++) runs.push(await measure(path));
    const med = (k) => median(runs.map((r) => r[k]));
    const r = { path, p50: med('p50'), p95: med('p95'), worst: med('worst'), over17: med('over17'),
      over33: med('over33'), longtasks: med('longtasks'), layoutMs: med('layoutMs'), styleMs: med('styleMs') };
    all.push(r);
    console.log(`  ${path.padEnd(24)} ${String(r.p50).padStart(5)} ${String(r.p95).padStart(6)} ` +
      `${String(r.worst).padStart(7)} ${String(r.over17).padStart(6)} ${String(r.over33).padStart(5)} ` +
      `${String(r.longtasks).padStart(6)} ${String(r.layoutMs + 'ms').padStart(7)} ${String(r.styleMs + 'ms').padStart(6)}`);
  }
  const worst = all.slice().sort((a, b) => b.over33 - a.over33 || b.p95 - a.p95)[0];
  console.log(`\n  worst page: ${worst.path}  p95 ${worst.p95}ms, ${worst.over33} frames over 33ms`);
}
ws.close();
chrome.kill();
for (let i = 0; i < 20; i++) {
  try { rmSync(profile, { recursive: true, force: true }); break; } catch { await sleep(100); }
}
