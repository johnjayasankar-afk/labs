#!/usr/bin/env python3
"""Writes the dev pages for the Labs stories. None of them is deployed.

    python3 tools/stories_lab.py

_stories.html  every build's story at the sizes this site shows it, one step or playing:
               /_stories?only=agentfit&step=1   /_stories?auto=1   /_stories?frames=Build card
_og.html       the 1200x630 link-preview card (assets/img/og.jpg)"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import data as D  # noqa: E402
import stories  # noqa: E402
import labs_stories  # noqa: E402,F401

# (label, width px, aspect ratio) for the places a story appears on Labs
FRAMES = [('Showcase', 846, '16 / 9'), ('Tablet', 700, '16 / 9'), ('Featured bay', 646, '16 / 10'),
          ('Build card', 560, '16 / 10'), ('Card narrow', 470, '16 / 10'), ('Mobile', 326, '4 / 3.4')]

LAB = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Story lab · Labs</title>
<link rel="stylesheet" href="/assets/css/site.css">
<style>
body { padding: 28px; background: var(--ground); }
.lab-sec { margin-bottom: 48px; }
.lab-h { margin: 0 0 14px; font: 500 13px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--ink-3); }
.lab-row { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 24px; }
.lab-f { display: grid; gap: 8px; }
.lab-f > p { font: 400 12px/1 var(--mono); color: var(--ink-3); }
.lab-f .story { width: 100%; aspect-ratio: var(--ar); }
</style>
<script src="/_stories.js" defer></script>
</head><body>
{{body}}
</body></html>
"""

OG = """<!doctype html>
<html lang="en" data-page="og">
<head>
<meta charset="utf-8">
<title>og card · Labs</title>
<link rel="stylesheet" href="/assets/css/site.css">
<style>
html, body { margin: 0; overflow: hidden; }
body { width: 1200px; height: 630px; }
.og {
  position: relative; isolation: isolate; box-sizing: border-box; width: 1200px; height: 630px; padding: 50px 52px 44px 60px;
  display: grid; grid-template-columns: 500px 1fr; gap: 36px; align-items: stretch; overflow: hidden;
  background-color: var(--ground);
  background-image: radial-gradient(60% 70% at 20% 0%, rgba(110, 231, 183, .28), transparent 70%), radial-gradient(circle at 1px 1px, rgba(28, 51, 38, .07) 1px, transparent 1.2px);
  background-size: auto, 24px 24px;
}
.og__copy { display: flex; flex-direction: column; }
.og__badge { align-self: flex-start; }
.og__name { display: flex; align-items: center; gap: 14px; margin-top: 28px; font: 450 50px/1 var(--sans); letter-spacing: -.05em; color: var(--ink); white-space: nowrap; }
.og__name .brand__tag { height: 32px; padding: 0 12px; font-size: 15px; }
.og__lede { margin-top: 18px; font: 400 30px/1.18 var(--sans); letter-spacing: -.032em; color: var(--ink); }
.og__lede span { display: block; color: var(--tone); }
.og__career { margin-top: 16px; font: 500 14px/1.45 var(--sans); color: var(--ink-3); text-wrap: balance; }
.og__proof { margin-top: auto; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
.og__proof p { padding: 13px 14px 12px; border-radius: 16px; background: #fff; box-shadow: 0 0 0 1px var(--line), var(--sh-1); }
.og__proof b { display: block; font: 400 30px/1 var(--sans); letter-spacing: -.045em; color: var(--ink); white-space: nowrap; }
.og__proof span { display: block; margin-top: 7px; font: 400 13px/1.25 var(--sans); color: var(--ink-3); }
.og__stage { position: relative; display: flex; flex-direction: column; padding: 8px; border-radius: 30px; background: rgba(255, 255, 255, .7); box-shadow: 0 0 0 1px var(--line), 0 40px 80px -40px rgba(15, 42, 29, .55); }
.og__head { display: flex; justify-content: space-between; align-items: baseline; padding: 12px 14px 12px; }
.og__head span:first-child { font: 500 12px/1.3 var(--mono); letter-spacing: .09em; text-transform: uppercase; color: var(--ink); }
.og__head span:last-child { font: 400 24px/1 var(--sans); letter-spacing: -.04em; color: var(--ink); white-space: nowrap; }
.og__stage .story { flex: 1; aspect-ratio: auto; border-radius: 22px; }
.og__stage .s-in { font-size: 17px; }
.og__stripes { position: absolute; z-index: -1; left: 548px; right: 0; bottom: 0; height: 250px; }
.og__stripes::after { content: ""; position: absolute; left: 0; right: 0; top: 88px; bottom: 0; background: var(--forest-3); }
.og__dom { position: absolute; left: 60px; bottom: 16px; font: 500 12px/1 var(--mono); letter-spacing: .04em; color: var(--ink-3); }
</style>
</head>
<body>
<div class="og">
  <div class="og__stripes stripes"><i></i><i></i><i></i><i></i></div>
  <div class="og__copy">
    <p class="badge og__badge"><span class="badge__dot"></span>Independent products · 2026</p>
    <p class="og__name">John Jayasankar <span class="brand__tag">Labs</span></p>
    <p class="og__lede">Instruments I shipped. <span>Built end-to-end. No demos.</span></p>
    <p class="og__career">RideLens · Daylight · RailDrop · AgentFit · Cartonry · KeepFloor · Pricing Hub</p>
    <div class="og__proof">
      <p><b>7</b><span>live builds on one bench</span></p>
      <p><b>4 → 1</b><span>ride providers, one RideLens board</span></p>
      <p><b>31</b><span>autonomy gates in AgentFit</span></p>
      <p><b>893</b><span>formula checks in Pricing Hub</span></p>
    </div>
  </div>
  <div class="og__stage">
    <p class="og__head"><span>Range · one bench</span><span>07 live</span></p>
    {{body}}
  </div>
  <p class="og__dom">{{domain}}</p>
</div>
</body>
</html>
"""


def write(name, text):
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
        f.write(text)


def main():
    keys = [b['slug'] for b in D.BUILDS]
    secs = []
    for key in keys:
        frames = ''.join('<div class="lab-f" style="width:%dpx;--ar:%s"><p>%s · %dpx</p>%s</div>' % (w, ar, label, w, stories.render(key))
                         for label, w, ar in FRAMES)
        secs.append('<section class="lab-sec" data-lab="%s"><h2 class="lab-h">%s</h2><div class="lab-row">%s</div></section>' % (key, key, frames))
    write('_stories.html', LAB.replace('{{body}}', '\n'.join(secs)))
    write('_og.html', OG.replace('{{body}}', stories.render('ridelens')).replace('{{domain}}', D.SITE['domain'].split('://', 1)[-1]))
    print('wrote _stories.html and _og.html for %d stories' % len(keys))


if __name__ == '__main__':
    main()
