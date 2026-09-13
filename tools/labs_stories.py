"""The four builds only Labs tells: AgentFit, Cartonry, KeepFloor, Pricing Hub.

Same language and mechanics as tools/stories.py (shared with the portfolio): one
light stage, one product-style window, one state per phase, data-on specs, and a
resting phase that is complete without script. Every label and figure is the
product's own published example or wording:

  AgentFit     the reference output its methodology page publishes for Support triage
  Cartonry     the example on its page, a Regular Slotted Container at 200 x 150 x 100 mm
  KeepFloor    the example listing on its page, a Linen tote in a US shop
  Pricing Hub  the Profit check example on its page

Importing this module registers the four stories in stories.STORIES."""

import stories
from stories import ICONS, chips, count, esc, foot, ico, metric, note, press, row, skel, typed, var, window

ICONS.update(
    gauge='<path d="M2.6 11.4a5.6 5.6 0 1 1 10.8 0"/><path d="M8 11.2l2.6-3.4"/><circle cx="8" cy="11.2" r=".9" fill="currentColor" stroke="none"/>',
    ruler='<rect x="1.8" y="5.2" width="12.4" height="5.6" rx="1.2"/><path d="M4.4 5.2v2.2M6.8 5.2v1.4M9.2 5.2v2.2M11.6 5.2v1.4"/>',
    box='<path d="M8 2.2l5.4 2.8v6L8 13.8 2.6 11V5z"/><path d="M2.6 5L8 7.8 13.4 5M8 7.8v6"/>',
    tag='<path d="M2.4 8.2V3a.6.6 0 0 1 .6-.6h5.2l5.4 5.4a.9.9 0 0 1 0 1.3l-4.3 4.3a.9.9 0 0 1-1.3 0z"/><circle cx="5.4" cy="5.4" r="1" fill="currentColor" stroke="none"/>',
    grid='<rect x="2.4" y="2.4" width="11.2" height="11.2" rx="1.6"/><path d="M2.4 6.2h11.2M2.4 9.8h11.2M6.4 2.4v11.2"/>',
)


# ----------------------------------------------------------------------------
# AgentFit · Fit, Autonomy, Readiness, Verdict
# ----------------------------------------------------------------------------
LADDER = ['Conventional', 'Assist', 'Assistive', 'Supervised', 'Bounded', 'Autonomous']
READY = ['Not ready', 'Discovery ready', 'Pilot ready', 'Production candidate']
# component weights from the methodology page, as cumulative edges of a 0 to 100 bar
WEIGHT_EDGES = [20, 35, 55, 75, 90]


def agentfit(m):
    right = m.swap(m.chip('Scoring fit', 'sky', 'spark', '0'), m.chip('Held by gates', 'amber', 'lock', '1'),
                   m.chip('Pilot ready', '', 'check', '2'), m.chip('Plausible return', 'mint', 'check', '3'))
    edges = ''.join('<i class="af-edge" style="left:%d%%"></i>' % x for x in WEIGHT_EDGES)
    fit = ('<span class="af-fit"><span class="s-track af-track"><i class="af-fill"></i>%s</span>'
           '<b class="s-val af-score">%s</b></span>') % (edges, count(78))
    rungs = ''.join('<i class="af-rung%s" style="--i:%d">%s</i>' % (
        ' af-rung--on' if i < 3 else (' af-rung--cur' if i == 3 else ' af-rung--lock'), i,
        ico('lock') if i > 3 else '<b>%d</b>' % i) for i in range(6))
    autonomy = '<span class="af-auto"><span class="af-ladder">%s</span>%s</span>' % (rungs, m.chip(LADDER[3], 'soft'))
    dots = ''.join('<i class="af-dot%s"></i>' % (' af-dot--on' if i < 2 else (' af-dot--cur' if i == 2 else '')) for i in range(4))
    ready = '<span class="af-auto"><span class="af-ready">%s</span>%s</span>' % (dots, m.chip(READY[2], 'soft'))
    effort = chips('<span class="s-chip af-range"><i></i><span>8.5 to 19</span><i></i></span>', m.chip('Plausible return', 'mint', 'check'))
    body = ''.join([
        row('Example', chips(m.chip('Support triage', 'mint', 'check'), m.chip('Reconciliation', 'soft', cls='s-hide-sm'),
                             m.chip('Compliance review', 'soft', cls='s-hide-sm'))),
        row('Fit', fit, m.status(busy='0', done='1-', d=6), m=m, sweep='0', fd=.2),
        row('Autonomy', m.swap(m.fx(skel(7, 3), '0'), m.fx(autonomy, '1-')), m.status(idle='0', wait='1', done='2-'), m=m, hold='1'),
        row('Readiness', m.swap(m.fx(skel(6.2), '0-1'), m.fx(ready, '2-')), m.status(idle='0-1', done='2-', d=3), m=m, sweep='2', fd=.3),
        row('Effort', m.swap(m.fx(skel(4, 5), '0-2'), m.fx(effort, '3')), m.status(idle='0-2', done='3', d=4), m=m, sweep='3', fd=.3),
    ])
    ft = '<div class="s-foot s-foot--note"><span class="s-k">Model</span><span class="s-quiet">AgentFit 1.0 · deterministic · nothing leaves the device</span></div>'
    floats = (note(m, 'spark', 'sky', 'Fit is not autonomy', 'scored apart, by a separate function', '0', 'tr')
              + note(m, 'lock', 'amber', 'Autonomy is earned', 'one unmet gate holds it down', '1', 'tr')
              + note(m, 'check', 'mint', 'Pilot ready', 'instrumentation and an exception path', '2', 'tr')
              + metric(m, '78', 'fit, recommended Supervised', '3', html=count(78))
              + m.fx(m.chip('Capacity returned, not a cost saving', 'ink'), '3', 's-float s-float--bl'))
    return window('gauge', 'Assessment', 'AgentFit · worked example', right, body, ft, floats=floats)


# ----------------------------------------------------------------------------
# Cartonry · Size, Dieline, Check, Export
# ----------------------------------------------------------------------------
def dieline(m):
    """The example blank, 747 x 253 mm: glue tab, side, end, side, end; 75 mm flaps."""
    edges = [35, 238, 391, 594, 747]
    panels = list(zip(edges[:-1], edges[1:]))
    cut = ['M35 75L2 86V167L35 178', 'M747 75V178']
    for a, b in panels:
        cut.append('M%g 75V2H%gV75' % (a + 1.5, b - 1.5))
        cut.append('M%g 178V251H%gV178' % (a + 1.5, b - 1.5))
    crease = ['M35 75H747', 'M35 178H747'] + ['M%g 75V178' % x for x in edges[:-1]]
    svg = ('<svg class="ct-svg" viewBox="-6 -6 759 265" aria-hidden="true" focusable="false">'
           '<path class="ct-glue" d="M35 75L2 86V167L35 178Z"/>'
           '<g class="ct-crease">%s</g><g class="ct-cut">%s</g></svg>') % (
        ''.join('<path d="%s"/>' % d for d in crease), ''.join('<path d="%s"/>' % d for d in cut))
    labels = ''.join('<span class="ct-lab" style="left:%.2f%%">%s</span>' % ((a + b) / 2 / 747 * 100, name)
                     for (a, b), name in zip(panels, ('Side', 'End', 'Side', 'End')))
    legend = ('<p class="s-legend ct-legend"><span><i class="ct-lg ct-lg--cut"></i>Cut</span><span><i class="ct-lg ct-lg--crease"></i>Crease</span>'
              '<span><i class="ct-lg ct-lg--glue"></i>Glue</span></p>')
    return ('<div class="ct-draw"><div class="ct-sheet">%s%s%s%s</div>%s</div>') % (
        svg, m.fx(labels, '1-', 'ct-labs', tag='span', d=4),
        m.fx('<span class="ct-dim ct-dim--w">747 mm</span><span class="ct-dim ct-dim--h">253 mm</span>', '1-', 'ct-dims', d=6), '', legend)


def field(m, k, v, delay):
    return '<span class="s-field ct-field"><span class="s-field__k">%s</span>%s</span>' % (k, typed(m, v, '0', delay))


def cartonry(m):
    right = m.swap(m.chip('Internal size', 'sky', 'ruler', '0'), m.chip('Blank computed', '', 'box', '1'),
                   m.chip('Parts listed', '', 'check', '2'), m.chip('Generated on your device', 'mint', 'check', '3'))
    size = '<span class="ct-fields">%s%s%s<span class="s-quiet">mm</span></span>' % (
        field(m, 'L', '200', .3), field(m, 'W', '150', .8), field(m, 'H', '100', 1.3))
    parts = chips(m.chip('Side ×2', 'soft'), m.chip('End ×2', 'soft'), m.chip('Flap ×8', 'soft', cls='s-hide-sm'), m.chip('Glue', 'soft'))
    export = chips(m.chip('SVG', ''), press(m, 'PDF · true scale', '3', 1.1, who='You'), m.chip('DXF', ''))
    stats = ''.join([
        '<div class="s-stat"><span class="s-k">Internal size</span>%s</div>' % size,
        '<div class="s-stat"><span class="s-k">Blank</span>%s</div>' % m.swap(
            m.fx(skel(5.4), '0'), m.fx('<span class="s-line2">747 × 253 mm</span>', '1-', d=5)),
        '<div class="s-stat"><span class="s-k">Parts</span>%s</div>' % m.swap(m.fx(skel(4, 3.4), '0-1'), m.fx(parts, '2-')),
        '<div class="s-stat"><span class="s-k">Export</span>%s</div>' % m.swap(m.fx(skel(3, 3, 3), '0-2'), m.fx(export, '3')),
    ])
    body = '<div class="s-split ct-split">%s<div class="s-stats">%s</div></div>' % (dieline(m), stats)
    floats = (note(m, 'ruler', 'sky', 'Always the internal size', 'allowances are added on top', '0', 'tr')
              + note(m, 'layers', '', 'Cut, crease, glue', 'separate named layers in SVG and DXF', '1', 'tr')
              + note(m, 'box', '', 'Outside 206 × 156 × 106 mm', 'panels are internal size plus caliper', '2', 'tr')
              + m.fx(m.chip('No account, no upload, no tracking', 'ink'), '3', 's-float s-float--bl'))
    return window('box', 'Dieline', 'Cartonry · RSC 0201 · B-flute, 3 mm', right, body, cls='s-win--wide', floats=floats)


# ----------------------------------------------------------------------------
# KeepFloor · Listing, Fees, Floors, Keep
# ----------------------------------------------------------------------------
FLOORS = [('Organic', 24.99, 'soft'), ('Ads-safe', 30.99, 'sky'), ('Survive-all', 35.99, 'amber')]


def keepfloor(m):
    right = m.swap(m.chip('One listing', '', 'tag', '0'), m.chip('Fees $4.02', 'amber', 'alert', '1'),
                   m.chip('Ads-safe $30.99', 'sky', 'shield', '2'), m.chip('You keep $19.08', 'mint', 'check', '3'))
    fees = chips(m.chip('Listing $0.20', 'soft', None, '1-', 0), m.chip('Transaction $2.44', 'soft', None, '1-', 2),
                 m.chip('Processing $1.38', 'soft', None, '1-', 4))
    pos = lambda v: (v - 20) / 20 * 100
    marks = ''.join('<i class="kf-mark kf-mark--%s" style="left:%.2f%%;--i:%d"><b>$%.2f</b></i>' % (tone, pos(v), i, v)
                    for i, (_, v, tone) in enumerate(FLOORS))
    ruler = ('<span class="kf-ruler"><i class="kf-list" style="left:%.2f%%"><b>List</b></i>%s</span>' % (pos(32), marks))
    body = ''.join([
        row('List', chips(m.chip('$32.00 list', 'ink'), m.chip('$5.50 shipping', 'soft'), m.chip('Qty 1', 'soft', cls='s-hide-sm')),
            m=m, sweep='0', fd=.1),
        row('Costs', chips(m.chip('Materials $8.40', 'soft'), m.chip('Postage $3.20', 'soft'), m.chip('Labor $2.00', 'soft', cls='s-hide-sm')),
            m=m, sweep='0', fd=.55),
        row('Fees', m.swap(m.fx(skel(5, 3.4), '0'), m.fx(fees, '1-')),
            m.swap(m.fx('<b class="s-val">$4.02</b>', '1-', d=6), cls='s-swap--end'), m=m, sweep='1', fd=.2),
        row('Floors', m.swap(m.fx(skel(8), '0-1'), m.fx(ruler, '2-'), cls='s-swap--fill'), m.status(idle='0-1', done='2-', d=5), m=m, sweep='2', fd=.2),
    ])
    ft = foot('You keep', var([0, 0, 0, .509], 's-fill s-fill--mint'),
              m.swap(m.fx(skel(3), '0-2'), m.fx('<b class="s-val s-val--mint">%s</b>' % count(19, pre='$', post='.08'), '3'), cls='s-swap--end'))
    floats = (note(m, 'tag', '', 'One listing', 'the published fee stack', '0', 'tr')
              + note(m, 'alert', 'amber', '$4.02 Etsy-side fees', '11% of merchandise', '1', 'tr')
              + metric(m, '$30.99', 'ads-safe floor, charm +$0.93', '2')
              + m.fx(m.chip('Math stays on this device', 'ink'), '3', 's-float s-float--bl'))
    return window('tag', 'Linen tote', 'KeepFloor · US shop · example listing', right, body, ft, floats=floats)


# ----------------------------------------------------------------------------
# Pricing Hub · Estimate, Connect, Overrun, Checked
# ----------------------------------------------------------------------------
GROUPS = ['Setup', 'Inputs', 'Documents', 'Reports']


def pricing(m):
    right = m.swap(m.chip('Estimate', '', 'calc', '0'), m.chip('24 connected sheets', 'sky', 'grid', '1'),
                   m.chip('Break-even 14.3%', 'amber', 'alert', '2'), m.chip('Checked in Excel', 'mint', 'check', '3'))
    arrow = '<i class="ph-to">%s</i>' % ico('arrow')
    sheets = '<span class="ph-flow">%s</span>' % arrow.join(
        m.el('span', 's-chip s-chip--soft ph-group', '<span>%s</span>' % g, '1', '--i:%d' % i) for i, g in enumerate(GROUPS))
    overrun = ('<span class="ph-over"><span class="ph-over__t"><i class="ph-over__fill"></i><i class="ph-be"><b>14.3%</b></i>'
               '<i class="ph-at"><b>10%</b></i></span><span class="s-quiet">keeps $1,602</span></span>')
    body = ''.join([
        row('Proposal', chips(m.chip('Cost × markup', 'soft'), m.chip('Contingency', 'soft', cls='s-hide-sm')),
            '<b class="s-val">$46,831</b>', m=m, sweep='0', fd=.2),
        row('Sheets', m.swap(m.fx(skel(4, 4, 4), '0'), m.fx(sheets, '1-')), m.status(idle='0', done='1-', d=6), m=m, sweep='1', fd=.1),
        row('Margin', m.swap(m.fx(skel(4.4, 4.4), '0-1'), m.fx(chips(m.chip('Gross 21.3%', 'soft'), m.chip('Net after overhead 11.3%', 'soft')), '2-')),
            m.status(idle='0-1', done='2-', d=3), m=m, sweep='2', fd=.1),
        row('Overrun', m.swap(m.fx(skel(8), '0-1'), m.fx(overrun, '2-', d=2), cls='s-swap--fill'), m.status(idle='0-1', wait='2', done='3'), m=m, hold='2'),
        row('Checks', m.swap(m.fx(skel(4, 4, 3), '0-2'), m.fx(chips(m.chip('893 formula checks', 'mint', 'check'), m.chip('46 bad-data probes', 'soft'),
                                                                     m.chip('0 macros', 'soft', cls='s-hide-sm')), '3')),
            m.status(idle='0-2', done='3', d=5), m=m, sweep='3', fd=.2),
    ])
    # the Profit check's own split of the proposal: job cost, overhead, profit
    ft = ('<div class="s-foot"><span class="s-k">Each dollar</span><span class="s-track ph-dollar">'
          '<i style="--w:78.7%"></i><i style="--w:10%"></i><i style="--w:11.3%"></i></span><b class="s-val">11.3% profit</b></div>')
    floats = (note(m, 'calc', '', 'Same math as the workbook', 'cost × markup, contingency, overhead', '0', 'tr')
              + note(m, 'grid', 'sky', 'Every sheet feeds the next', 'each link a real formula reference', '1', 'tr')
              + metric(m, '$1,602', 'kept after a 10% overrun', '2')
              + m.fx(m.chip('No subscription, no add-ins, no macros', 'ink'), '3', 's-float s-float--bl'))
    return window('grid', 'Job costing', 'Pricing Hub · Profit check example', right, body, ft, floats=floats)


stories.STORIES.update({
    'agentfit': dict(group='agents', n=4, rest=3, fn=agentfit,
                     label='Schematic interface using AgentFit’s published reference output for Support triage: a fit score of 78 across six weighted components, autonomy computed apart and held at Supervised by gates, readiness at Pilot ready, and an effort range of 8.5 to 19 with a verdict of Plausible return.'),
    'cartonry': dict(group='markets', n=4, rest=3, fn=cartonry,
                     label='Schematic interface using Cartonry’s own example: an internal size of 200 by 150 by 100 millimetres on 3 millimetre board, a computed blank of 747 by 253 millimetres with cut, crease and glue lines, the listed parts, and SVG, true-scale PDF and DXF exports generated on the device.'),
    'keepfloor': dict(group='labs', n=4, rest=3, fn=keepfloor,
                      label='Schematic interface using KeepFloor’s own example listing: a Linen tote listed at $32.00, $4.02 in published Etsy-side fees, floors of $24.99 organic, $30.99 ads-safe and $35.99 survive-all, and $19.08 kept.'),
    'pricing': dict(group='agents', n=4, rest=3, fn=pricing,
                    label='Schematic interface using Pricing Hub’s Profit check example: a $46,831 proposal, setup, input, document and report sheets that feed each other, a 10% overrun that keeps $1,602 against a 14.3% break-even, and 893 formula checks.'),
})
