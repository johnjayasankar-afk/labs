"""Labs content: every word a visitor reads on the Labs site.

Copy comes from John's Labs site (labs-rouge.vercel.app) and from each build's
own public page, captured 13 September 2026. Figures inside the stories are each
product's own published example or sample data, and every bay footer says which
one. The build refuses em and en dashes, so ranges read "8.5 to 19".

A build's phases are (tab, caption). Its story, in tools/stories.py (RideLens,
Daylight, RailDrop and Gridiron, shared with the portfolio) or tools/labs_stories.py (the four
builds only Labs tells), draws one state per phase; the counts must match.
`route` is the short link on this domain; vercel.json redirects it to `live`.
Every figure on a build card comes from tools/claims.py, the ledger, through
M() and V(). No number is written here: tools/verify_claims.py re-derives what
can be re-derived, including the mechanism behind each build's rule, and
reports the rest as unchecked rather than as passing.
"""

import os  # noqa: E402

from claims import M, V, checked_on  # noqa: E402

# ---------------------------------------------------------------------------
# Where the products live.
#
# Every product link on this site resolves through product_url(). Today that
# returns the Vercel hostname each product was deployed under. When the eight
# subdomains of johnjayasankar.com actually serve their products, set
# PRODUCT_SUBDOMAINS=1 in the environment (or flip the default below) and every
# link on the site moves at once.
#
# It is off by default because the subdomains do not serve yet. The wildcard
# DNS record already points them at Vercel, but no Vercel project has claimed
# them, so each one answers DEPLOYMENT_NOT_FOUND. Turning this on before that
# is fixed would replace nine working links with nine 404s. docs/DOMAINS.md
# records the measured state and the exact steps left.
#
# This block is duplicated verbatim in the Labs repository. The two sites have
# to move together: one site linking a subdomain while the other links a Vercel
# hostname is worse than either. Diff them before changing either.
PRODUCT_DOMAIN = 'johnjayasankar.com'
PRODUCT_SUBDOMAINS = os.environ.get('PRODUCT_SUBDOMAINS') == '1'

# The hostname each product is deployed under today, and the subdomain it is
# meant to answer on. The key is the subdomain label.
PRODUCT_HOSTS = dict(
    ridelens='https://ride-lens2.vercel.app/',
    daylight='https://daylight-app-wine.vercel.app/',
    raildrop='https://rail-drop3.vercel.app/',
    gridiron='https://gridiron-pink-chi.vercel.app/',
    agentfit='https://agent-fit2.vercel.app/',
    cartonry='https://cartonry.vercel.app/',
    keepfloor='https://keep-floor.vercel.app/',
    pricing='https://pricing-hub-seven.vercel.app/',
)


# Where each product answers when it is running on this machine. Set
# PRODUCT_LOCAL=1 to point every link and every live preview at these, which is
# the only way to see a preview go live before the products are deployed: the
# handshake that reveals the frame comes from the product itself. The products
# allow a loopback framer in development for the same reason.
PRODUCT_LOCAL = os.environ.get('PRODUCT_LOCAL') == '1'
PRODUCT_LOCAL_PORTS = dict(
    ridelens=3000,
    raildrop=3001,
    gridiron=5178,
)


def product_url(key):
    """The public address of a product, as this site should link it."""
    if PRODUCT_LOCAL and key in PRODUCT_LOCAL_PORTS:
        return 'http://localhost:%d/' % PRODUCT_LOCAL_PORTS[key]
    if PRODUCT_SUBDOMAINS:
        return 'https://%s.%s/' % (key, PRODUCT_DOMAIN)
    return PRODUCT_HOSTS[key]



SITE = dict(
    name='John Jayasankar',
    domain='https://labs.johnjayasankar.com',
    email='johnjayasankar@gmail.com',
    portfolio='https://johnjayasankar.com/',
    substack='https://substack.com/@johnjayasankar',
    linkedin='https://www.linkedin.com/in/johnjayasankar',
    city='New York',
    year='2026',
    title='Labs · John Jayasankar',
    description='Independent products John Jayasankar shipped: RideLens, Daylight, RailDrop, Gridiron, AgentFit, Cartonry, KeepFloor, and Pricing Hub.',
    og_description='Eight independent products John Jayasankar built and shipped, including RideLens, Daylight, RailDrop, Gridiron, and AgentFit.',
    og_image='/assets/img/og.jpg',
    og_alt='Labs · John Jayasankar · independent products, shipped',
    note='Independent products, separate from the day job.',
)

# One line at the foot of every page; the full text is LEGAL, at /legal.
LEGAL_LINE = ('Independent products, built on my own time with my own resources. '
              'Not affiliated with or endorsed by any employer or any service named here.')

LEGAL = dict(
    kicker='Disclaimer',
    h1=('Independent products.', 'Built on my own time.'),
    lede='What Labs is, what it is not, and how to reach me about it.',
    description='Labs is John Jayasankar’s personal project site: independent products built on his own time, not affiliated with any employer.',
    parts=[
        ('Independent work', ['Labs is my personal project site. I designed and built every product here independently, on my own '
                              'time and with my own resources. None of them is a product of, or endorsed by, any company I work for '
                              'or have worked for, and the opinions here are my own.']),
        ('Names of other services', ['Services and brands named here, including Uber, Lyft, Empower, Curb, Amtrak, the NFL, ESPN, '
                                     'DraftKings, Kalshi, Etsy, Apple, Google and Microsoft, belong to their owners. Their names are '
                                     'used only to identify them, and no product here is affiliated with, sponsored by or endorsed by '
                                     'any of them.']),
        ('Data', ['Products show data from public and third-party sources. It can be delayed, incomplete or wrong.']),
        ('Not advice', ['Nothing here is financial, investment, betting, legal or tax advice. Prices, fares and odds are shown for '
                        'information only.']),
        ('Corrections', ['If something here should be corrected or removed, email '
                         '<a href="mailto:johnjayasankar@gmail.com">johnjayasankar@gmail.com</a>.']),
    ],
)

BUILDS = [
    dict(
        slug='ridelens', n='01', name='RideLens', cat='Consumer', tag='Consumer', featured=True,
        line='Every ride, one comparison.',
        blurb='Live roads. Real rate cards. Uber, Lyft, Empower, and Curb ranked before you open four apps and guess.',
        does=['Map the trip once on live roads, then line up four providers side by side',
              'Rank the same quotes by Price, Soonest, or Value',
              'Estimates move with traffic, time of day, hotspots, and weather'],
        stats=[M('ridelens.providers'), M('ridelens.ranks'), M('ridelens.ranges')],
        rule='Ranges stay ranges.',
        rule_body='When a fare is a range, both ends stay on the board. RideLens never invents a midpoint to look decisive.',
        words='Route Price Soonest Value Estimate Range Upfront',
        route='/ridelens', live=product_url('ridelens'), case='https://johnjayasankar.com/work/ridelens',
        bay=dict(title='RideLens · compare board', sub='Illustrative trip · four providers, three sort rules',
                 big='4 → 1', big_sub='providers → one board',
                 foot='Illustrative quote types, not live fares · the final fare is always confirmed in the provider app'),
        phases=[('Route', 'Illustrative: map the trip once on live roads; conditions feed the marketplace model.'),
                ('Price', 'Illustrative: the same four quotes, ranked by lowest listed fare.'),
                ('Soonest', 'Illustrative: the same quotes, ranked by soonest pickup.'),
                ('Value', 'Illustrative: fare and wait traded off. Ranges stay ranges.')],
    ),
    dict(
        slug='daylight', n='02', name='Daylight', cat='Native', tag='Native macOS', featured=True,
        line='Your screen, through the day.',
        blurb='Warmth and brightness on a schedule you set: gradual, offline, and honest about what it is doing and why.',
        does=['Shift warmth and brightness gradually on a schedule, or follow the sun',
              'Decide every control on one printed, six-layer ladder',
              'Read back after every write, and say so when another app took over'],
        stats=[M('daylight.layers'), M('daylight.certainty'), M('daylight.tests')],
        rule='Success is not evidence.',
        rule_body='Daylight separates what it asked for, what macOS accepted, and what it could read back and confirm.',
        words='Schedule Resolve Explain Asked Accepted Confirmed',
        route='/daylight', live=product_url('daylight'), case='https://johnjayasankar.com/work/daylight',
        bay=dict(title='Daylight · display schedule', sub='Balanced preset · warmth and brightness decided separately',
                 big='6 layers', big_sub='one fixed order',
                 foot='Schematic · step values from the Balanced preset · the sentence is one the app writes'),
        phases=[('Schedule', 'Balanced preset: 6500 K by day, 4200 K at 19:00, 3200 K at 21:30, 2800 K at 23:30.'),
                ('Resolve', 'Six layers in a fixed order: the highest layer that speaks about a control wins it.'),
                ('Explain', 'An app rule holds warmth neutral while dimming still comes from the schedule, and a sentence says so.'),
                ('Confirm', 'Asked, accepted, confirmed: an API returning success is not evidence the display changed.')],
    ),
    dict(
        slug='raildrop', n='03', name='RailDrop', cat='Consumer', tag='Consumer', featured=True,
        line='Know when your train gets cheaper.',
        blurb='Book the trip. Watch every bookable Amtrak option across your window. One email when a listed fare actually drops.',
        does=['Watch every bookable rail option across the day before, the day, and the day after',
              'Scan immediately, then again morning, afternoon, and evening',
              'One email when a listed fare beats what you paid'],
        stats=[M('raildrop.window'), M('raildrop.email'), M('raildrop.prices')],
        rule='Never an invented price.',
        rule_body='If the live board is down, RailDrop says so. It never guesses a fare, a change fee, or an itinerary.',
        words='Booked Watching Board Alert Listed Honest',
        route='/raildrop', live=product_url('raildrop'), case='https://johnjayasankar.com/work/raildrop',
        bay=dict(title='RailDrop · Amtrak fare watch', sub='Sample board · BOS → NYP · you paid $128',
                 big='$128 → $47', big_sub='paid → cheapest listed',
                 foot='Sample board from RailDrop’s own site · listed fares · confirm on Amtrak'),
        phases=[('Booked', 'Illustrative: stations, date, and what you actually paid become the baseline.'),
                ('Watching', 'Illustrative: the first scan runs immediately, then morning, afternoon, and evening.'),
                ('Board', 'Illustrative: every bookable option across ±1 day, measured against what you paid.'),
                ('Alert', 'Illustrative: one email when a listed fare beats what you paid. Confirm on Amtrak.')],
    ),
    dict(
        slug='gridiron', n='04', name='Gridiron', cat='Live data', tag='Live data', featured=True,
        line='Every game. Every drive. One view.',
        blurb='A live NFL and college football command center: a 3D field for every game, with the reported ball spot, win probability, and odds beside it.',
        does=['Follow every live NFL and college game, each on its own 3D field',
              'Draw only reported spots: the ball, the line of scrimmage, the line to gain',
              'Put ESPN win probability, DraftKings lines, and Kalshi prices beside the score'],
        stats=[M('gridiron.sources'), M('gridiron.guessed'), M('gridiron.tests')],
        rule='Reported, never guessed.',
        rule_body='Every spot, clock, and chance comes from a source that reported it. A missing ball spot says so; it is never guessed to midfield.',
        words='Slate Drive Spot Chance Lines Touchdown',
        route='/gridiron', live=product_url('gridiron'), case='https://johnjayasankar.com/work/gridiron',
        bay=dict(title='Gridiron · football command center', sub='NFL Week 1 replay · ARI at LAC · captured real games',
                 big='6 → 1', big_sub='live games → one view',
                 foot='Captured real games from Gridiron’s NFL Week 1 replay · figures as ESPN, DraftKings, and Kalshi reported them · not betting advice'),
        phases=[('Slate', 'Replay of captured real games: six live at once, and Watch next names why ARI at LAC deserves attention.'),
                ('Drive', 'Reported spots only: 10 plays and 65 yards to 2nd & Goal at the LAC 5, where the goal line is the line to gain.'),
                ('Odds', 'Every chance is named: ESPN win probability LAC 70%, DraftKings closing lines, Kalshi LAC to win 73.5¢.'),
                ('Touchdown', 'A 5-yard touchdown run, announced once, and ESPN’s model moves ARI +5 on the play.')],
    ),
    dict(
        slug='agentfit', n='05', name='AgentFit', cat='Model', tag='Decision model', featured=False,
        line='When should a workflow get an agent?',
        blurb='AgentFit scores economic opportunity, technical readiness, controllability, and risk before anyone writes an orchestration graph.',
        does=['Score fit from 0 to 100 across six weighted components',
              'Recommend autonomy separately, held down by 31 published gates',
              'Recommend deterministic automation or a human-led process when that is the answer'],
        stats=[M('agentfit.gates'), M('agentfit.rungs'), M('agentfit.workflows')],
        rule='Fit is not autonomy.',
        rule_body='A workflow can score in the eighties and still warrant nothing beyond human-approved execution.',
        words='Fit Autonomy Readiness Capacity Gates Earned',
        route='/agentfit', live=product_url('agentfit'), case=None,
        bay=dict(title='AgentFit · worked example', sub='Support triage · the model’s published reference output',
                 big='78', big_sub='fit · autonomy decided apart',
                 foot='The reference output AgentFit publishes for Support triage · deterministic · nothing leaves the device'),
        phases=[('Fit', 'Six weighted components score the workflow: Support triage lands at 78.'),
                ('Autonomy', 'Autonomy is computed apart from fit, and gates hold it down: Supervised.'),
                ('Readiness', 'Readiness is its own track: Pilot ready, with instrumentation and an exception path.'),
                ('Verdict', 'Effort is always a range, 8.5 to 19. Plausible return, counted as capacity, not savings.')],
    ),
    dict(
        slug='cartonry', n='06', name='Cartonry', cat='Tool', tag='Tool', featured=False,
        line='Packaging dielines: cut, crease, fold, cost.',
        blurb='Production-ready packaging dielines at any size. Export SVG, true-scale PDF, and DXF. Runs entirely in your browser.',
        does=['Enter the internal size, and the board allowances are added on top',
              'Eleven box styles, from shipping cases to tuck-end cartons and pillow boxes',
              'A 3D fold built from the same geometry the dieline is cut from'],
        stats=[M('cartonry.styles'), M('cartonry.formats'), M('cartonry.free')],
        rule='Not a picture.',
        rule_body='The 3D fold is the geometry the dieline is cut from, and the tests fold the net and measure it against the dimensions typed.',
        words='Size Dieline Cut Crease Glue Fold',
        route='/cartonry', live=product_url('cartonry'), case=None,
        bay=dict(title='Cartonry · dieline', sub='Example · Regular Slotted Container 0201 · 200 × 150 × 100 mm',
                 big='747 × 253', big_sub='mm blank, from the internal size',
                 foot='The example on Cartonry’s own page · B-flute board, 3 mm · files are generated on your device'),
        phases=[('Size', 'Type the internal size, the space the product needs: 200 × 150 × 100 mm.'),
                ('Dieline', 'The blank is computed, with cut, crease, and glue on separate named layers.'),
                ('Check', 'Every part is listed, and the outside comes to 206 × 156 × 106 mm.'),
                ('Export', 'SVG, true-scale PDF, or DXF, generated on the device.')],
    ),
    dict(
        slug='keepfloor', n='07', name='KeepFloor', cat='Pricing', tag='Pricing', featured=False,
        line='The Etsy list price that still pays you.',
        blurb='One listing, the published fee stack, and the lowest charmed price that survives Offsite Ads. Math stays on this device.',
        does=['Every published Etsy fee, stacked line by line for one listing',
              'Three floors: organic, Offsite Ads safe, and survive-all',
              'Charm rounding, with the leftover shown and never counted as a fee'],
        stats=[M('keepfloor.floors'), M('keepfloor.fees'), M('keepfloor.local')],
        rule='Every published fee, counted.',
        rule_body='The whole published fee stack, including Offsite Ads, then the lowest charmed list price that survives it.',
        words='Listing Fees Floors Keep Charm Ads',
        route='/keepfloor', live=product_url('keepfloor'), case=None,
        bay=dict(title='KeepFloor · one listing', sub='Example listing · Linen tote · US shop',
                 big='$19.08', big_sub='kept at a $32.00 list',
                 foot='The example listing on KeepFloor’s own page · rates as of 4 September 2026 · not affiliated with Etsy'),
        phases=[('Listing', 'One listing: a $32.00 list, $5.50 shipping charged, and the costs behind it.'),
                ('Fees', 'The published fee stack: $4.02 in Etsy-side fees on this order.'),
                ('Floors', 'Three floors: organic $24.99, ads-safe $30.99, survive-all $35.99.'),
                ('Keep', 'At $32.00 you keep $19.08, and the math stays on the device.')],
    ),
    dict(
        slug='pricing', n='08', name='Pricing Hub', cat='Workbook', tag='Workbook', featured=False,
        line='Contractor job costing, estimate to invoice.',
        blurb=f"Estimate, schedule, track crew hours and costs, handle change orders, invoice, and see real profit per job. {V('pricinghub.sheets')} connected sheets for Excel and Google Sheets.",
        does=['Price a job line by line, then print a client-ready proposal',
              'Change orders with a signable form, invoices, and payments in one workbook',
              'Budget against actual per cost code, on a dashboard that keeps itself up to date'],
        stats=[M('pricinghub.sheets'), M('pricinghub.checks'), M('pricinghub.macros')],
        rule='Plain formulas only.',
        rule_body='No subscription, no add-ins, no macros. Every link between sheets is a real formula reference.',
        words='Estimate Sheets Margin Overrun Checks',
        route='/pricing', live=product_url('pricing'), case=None,
        bay=dict(title='Pricing Hub · job costing', sub='Profit check example · one job, one blended markup',
                 big='$46,831', big_sub='proposal total',
                 foot='The example on the product’s own Profit check · one blended markup · not accounting or tax advice'),
        phases=[('Estimate', 'Cost times markup, plus contingency: a $46,831 proposal.'),
                ('Connect', 'Every sheet feeds the next: setup, inputs, documents, reports.'),
                ('Overrun', 'A 10% overrun keeps $1,602 of the $5,288 net profit priced in.'),
                ('Checked', f"{V('pricinghub.checks')} formula checks and {V('pricinghub.probes')} bad-data probes. No macros, no add-ins.")],
    ),
]

HOME = dict(
    badge='Independent products · 2026',
    h1=('Instruments I shipped.', 'Built end-to-end. No demos.'),
    lede='Consumer tools, a native macOS app, a live football command center, pricing tools, and a model for when a workflow should get an agent.',
    meta=[V('labs.live.padded'), V('labs.featured'), 'New York'],
    # the hero showcase keeps the Labs site's own framing: range, one bench
    show=[('consumer', 'Consumer', 'ridelens'), ('native', 'Native', 'daylight'), ('model', 'Model', 'agentfit'), ('live', 'Live data', 'gridiron')],
    # the narrowest phones name the four tabs without their numbers
    show_short=dict(consumer='Consumer', native='Native', model='Model', live='Live'),
    proof=[M('labs.live') + ('#featured',),
           M('ridelens.board') + ('#ridelens',),
           (V('agentfit.gates'), 'autonomy gates in AgentFit', '#agentfit'),
           (V('pricinghub.checks'), 'formula checks in Pricing Hub', '#pricing')],
    # What the split means, said rather than implied. All eight carry a worked
    # example; these four also carry a case study on the portfolio.
    featured=dict(n='01', kicker='Featured', h2=('Four systems', 'that show the range.'),
                  lede='The four with a full case study on the portfolio: how each was built, '
                       'and what it refuses to do.'),
    also=dict(n='02', kicker='Also shipped', h2=('Narrower instruments.', 'Same bar.'),
              lede='Smaller in scope, held to the same rule. Each carries its own worked example '
                   'and its own figures, counted the same way.'),
    rules=dict(n='03', kicker='What they share', h2=('No demos.', 'The rule each build keeps.')),
    # Counted, not asserted: the same move each build makes about its own data,
    # applied to the bench. The date comes from the ledger, so it cannot drift
    # away from the last check.
    provenance='Each figure on these cards is counted from the build’s own '
               'repository, or dated where it cannot be counted, and every rule '
               'below names the mechanism that enforces it. Last checked '
               + checked_on('ridelens.providers', 'ridelens.ranks', 'ridelens.ranges',
                            'daylight.layers', 'daylight.certainty', 'daylight.tests',
                            'raildrop.window', 'raildrop.email', 'raildrop.prices',
                            'gridiron.sources', 'gridiron.guessed', 'gridiron.tests',
                            'agentfit.gates', 'agentfit.rungs', 'agentfit.workflows',
                            'cartonry.styles', 'cartonry.formats', 'cartonry.free',
                            'keepfloor.floors', 'keepfloor.fees', 'keepfloor.local',
                            'pricinghub.sheets', 'pricinghub.checks', 'pricinghub.macros')
               + '.',
    visit=dict(k='johnjayasankar.com', h2='The portfolio.',
               lede='Production AI agents and 0→1 financial infrastructure, with case studies for RideLens, Daylight, RailDrop, and Gridiron.',
               link='Open the portfolio'),
    hint='j / k builds · Enter opens · 1-4 phases · ⌘K jump · ? keys',
)

NOT_FOUND = dict(
    kicker='Not found',
    h1=('Not a build.', 'Nothing lives at this address.'),
    lede='Every Labs build is below, one click from live.',
    hint='j / k builds · Enter opens · ⌘K jump',
)
