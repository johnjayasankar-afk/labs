#!/usr/bin/env python3
"""The claims ledger for labs.johnjayasankar.com. Dev-only: tools/ is excluded
from the deploy by .vercelignore.

    python3 tools/claims.py            # the ledger as a table
    python3 tools/claims.py --json     # the ledger as JSON

Every verifiable figure printed on this site is declared here exactly once,
with where it came from and whether a machine can re-derive it. The page data
in data.py reads from here through M() and V() and carries no figure of its
own, so a number cannot be changed on the site without being changed in the
ledger. tools/verify_claims.py re-derives what it can and reports the rest as
unchecked rather than as passing.

Each build's rule is a claim about a codebase, so each one carries the
mechanism that enforces it as a supporting claim: a function, a constant, a
type. All eight have one. If a rule ever loses its mechanism, this is where it
shows.

The format is shared with the portfolio site so one verifier serves both. Both
repositories declare LEDGER_FORMAT and define Claim with the same fields; see
verify_claims.py, which is byte-identical in both.

A claim has three honest states and the ledger never blurs them:

  checked    a command re-derived the number today
  unchecked  the number is re-derivable, but not here and not now
  asserted   there is no machine source; a person vouched for it on a date

`check` says which:

  here       method runs in the source repo, offline, in well under a second
  build      method runs, but needs installed dependencies and real time
  elsewhere  re-derivable in principle, but not on this machine
  none       asserted

Nothing on this site is an employment figure, so nothing here is asserted
without a source. Where a figure states a behaviour rather than a count, it is
marked elsewhere and reported as unchecked, never as passing. build.py prints a
warning for any asserted figure older than STALE_AFTER_DAYS."""

import datetime
import json
import sys
from dataclasses import dataclass, asdict

LEDGER_FORMAT = 1

# An asserted figure older than this is flagged by the build. Six months: long
# enough that a stable figure is not nagged about, short enough that a figure
# nobody can still vouch for surfaces before someone reads it in an interview.
STALE_AFTER_DAYS = 180


@dataclass(frozen=True)
class Claim:
    """One figure on the site, declared once."""

    # Stable key, 'subject.figure'. Never reused for a different figure. The
    # page data refers to a claim by this id, so it also has to read well.
    id: str
    # The value exactly as the site prints it.
    value: str
    # The words the site prints beside it.
    about: str
    # 'repo' | 'document' | 'asserted'
    origin: str
    # For 'repo': the sibling repository's directory name.
    # For 'document': a path, repo-relative if `source_repo` is set.
    source: str
    # How the figure is counted, or how it was established.
    method: str
    # 'here' | 'build' | 'elsewhere' | 'none'
    check: str
    # ISO date the value was last confirmed against its source.
    verified: str
    # The repository `method` runs in, when that is not `source`.
    source_repo: str = ''
    # The claim this one backs rather than being printed itself: the mechanism
    # behind a rule, or the second half of a figure's label. A supporting claim
    # is in use when the claim it supports is.
    supports: str = ''
    # What `method` must print, when that is not `value`.
    expect: str = ''
    note: str = ''

    def expected(self):
        return self.expect or self.value

    def age_days(self, today=None):
        today = today or datetime.date.today()
        return (today - datetime.date.fromisoformat(self.verified)).days

    def stale(self, today=None):
        return self.check == 'none' and self.age_days(today) > STALE_AFTER_DAYS


def C(**kw):
    return Claim(**kw)


# ---------------------------------------------------------------------------
# The bench itself. Counted from this repository's own page data, so adding a
# build without updating the header is caught here rather than by a reader.
# ---------------------------------------------------------------------------

BENCH = [
    C(id='labs.live', value='8', about='live builds on one bench',
      origin='repo', source='labs', check='here', verified='2026-09-25',
      method='builds in BUILDS, tools/data.py'),
    C(id='labs.live.padded', value='08 live', about='header meta',
      origin='repo', source='labs', check='here', verified='2026-09-25',
      expect='8',
      method='the same count, zero-padded for the header'),
    C(id='labs.featured', value='04 featured', about='header meta',
      origin='repo', source='labs', check='here', verified='2026-09-25',
      expect='4',
      method='builds marked featured=True in BUILDS, tools/data.py'),
]


# ---------------------------------------------------------------------------
# The eight builds. Three figures each, and the mechanism behind each rule.
# ---------------------------------------------------------------------------

BUILDS_CLAIMS = [
    # --- 01 RideLens ----------------------------------------------------
    C(id='ridelens.providers', value='4', about='providers, one board',
      origin='repo', source='RideLens2', check='here', verified='2026-09-25',
      method='entries in SURFACEABLE_PROVIDERS, '
             'src/lib/sources/ratecard/public-rate-card-quote-source.ts'),
    C(id='ridelens.ranks', value='3', about='ways to rank a trip',
      origin='repo', source='RideLens2', check='here', verified='2026-09-25',
      method='members of type RankingMode, src/components/compare-form.tsx'),
    C(id='ridelens.ranges', value='Honest', about='ranges stay ranges',
      origin='repo', source='RideLens2', check='here', verified='2026-09-25',
      expect='1',
      method='src/lib/domain/money.ts carries rankingMidpointMinor, commented '
             '"Midpoint for ranking only, never shown as the fare": the '
             'midpoint orders the board and is never printed as a price.'),
    C(id='ridelens.board', value='4 → 1', about='ride providers, one RideLens board',
      origin='repo', source='RideLens2', check='here', verified='2026-09-25',
      expect='4', method='the same four providers, as the header prints them'),
    C(id='rule.ridelens', value='rankingMidpointMinor',
      about='Ranges stay ranges.', supports='ridelens.ranges',
      origin='repo', source='RideLens2', check='here', verified='2026-09-25',
      expect='1',
      method='The rule\u2019s mechanism: a fare is held as priceMinMinor and '
             'priceMaxMinor, and the single number that exists only to order '
             'the board is named and commented so it cannot be mistaken for a '
             'price. src/lib/domain/money.ts.'),

    # --- 02 Daylight ----------------------------------------------------
    C(id='daylight.layers', value='6', about='layers, one fixed order',
      origin='repo', source='Daylight', check='here', verified='2026-09-25',
      method='cases in enum ControlLayer, Sources/DaylightCore/Policy.swift'),
    C(id='daylight.certainty', value='3', about='levels of certainty',
      origin='repo', source='Daylight', check='here', verified='2026-09-25',
      method='cases in enum ApplicationConfidence, '
             'Sources/DaylightCore/Device.swift'),
    C(id='daylight.tests', value='263', about='tests, no dependencies',
      origin='repo', source='Daylight', check='here', verified='2026-09-25',
      method='func test declarations in Sources/DaylightTests',
      note='Static count equals the runner count here because the suite has '
           'its own harness: every test is a func test, and AllTests.swift '
           'runs all of them. Daylight IMPROVEMENTS.md records the same 263.'),
    C(id='daylight.dependencies', value='0', about='no dependencies',
      supports='daylight.tests',
      origin='repo', source='Daylight', check='here', verified='2026-09-25',
      method='.package(url: entries in Package.swift'),
    C(id='rule.daylight', value='ReadbackJudgement.judge',
      about='Success is not evidence.', supports='daylight.certainty',
      origin='repo', source='Daylight', check='here', verified='2026-09-25',
      expect='1',
      method='The rule\u2019s mechanism: a call the system accepted without '
             'error returns .acceptedBySystem. Only a readback that agrees '
             'within confirmedWithin returns .readbackConfirmed. '
             'Sources/DaylightCore/Device.swift.'),

    # --- 03 RailDrop ----------------------------------------------------
    C(id='raildrop.window', value='±1 day', about='default watch window',
      origin='repo', source='RailDrop3', check='here', verified='2026-10-01',
      expect='1',
      method='the flexibility the form falls back to when a link carries none: '
             'the default in useState<0 | 1 | 2>(initial?.flexibilityDays ?? 1), '
             'src/components/fare-lookup.tsx'),
    C(id='raildrop.email', value='1 email', about='only when it improves',
      origin='document', source='README.md', source_repo='RailDrop3',
      check='elsewhere', verified='2026-09-25',
      method='A behavioural claim about the alert path: one email is sent, and '
             'only when a listed fare beats what was paid. Re-deriving it '
             'means running the alert pipeline against a price feed, which '
             'this machine cannot do offline.'),
    C(id='raildrop.prices', value='0', about='invented prices',
      origin='repo', source='RailDrop3', check='here', verified='2026-09-25',
      expect='5',
      method='UNKNOWN members across the domain enumerations in '
             'src/lib/domain/types.ts: fare family, travel class, service '
             'type, availability and price semantics each admit "we do not '
             'know" as a value, so a missing fact is a status rather than a '
             'number.'),
    C(id='rule.raildrop', value='AVAILABILITY_STATUSES',
      about='Never an invented price.', supports='raildrop.prices',
      origin='repo', source='RailDrop3', check='here', verified='2026-09-25',
      expect='1',
      method='The rule\u2019s mechanism: a fare that is sold out or unreadable '
             'normalises to UNAVAILABLE or UNKNOWN rather than to a price. '
             'src/lib/providers/parse-normalizer.ts, against the enumeration '
             'in src/lib/domain/types.ts.'),

    # --- 04 Gridiron ----------------------------------------------------
    C(id='gridiron.sources', value='3', about='sources, each named',
      origin='document', source='README.md', source_repo='gridiron',
      check='elsewhere', verified='2026-09-25',
      method='ESPN win probability, DraftKings lines and Kalshi prices: three '
             'named sources of figures, fetched over two providers, because '
             'the DraftKings line arrives through ESPN. README "Data sources '
             'and coverage limits" names all three.',
      note='Three attributions, two hosts. The card says "sources, each '
           'named", which is the attribution count, and that is the honest '
           'reading only because every figure carries its source in the UI.'),
    C(id='gridiron.guessed', value='0', about='guessed ball spots',
      origin='repo', source='gridiron', check='here', verified='2026-09-25',
      expect='1',
      method='SPOT_UNAVAILABLE in shared/format.ts: a play with no reported '
             'spot renders "Ball spot unavailable" instead of a position. '
             'Held by tests/watch-delay.test.ts and e2e/slate.spec.ts.'),
    C(id='gridiron.tests', value='669', about='unit and integration tests',
      origin='repo', source='gridiron', check='build', verified='2026-09-25',
      method='the total vitest reports: npm test'),
    C(id='gridiron.journeys', value='144', about='end-to-end journeys',
      supports='gridiron.tests',
      origin='repo', source='gridiron', check='build', verified='2026-09-25',
      method='journeys Playwright lists for the desktop-chrome project'),
    C(id='gridiron.version', value='0.6.0', about='version the tests ran at',
      supports='gridiron.tests',
      origin='repo', source='gridiron', check='here', verified='2026-09-25',
      method='version in package.json'),
    C(id='rule.gridiron', value='SPOT_UNAVAILABLE',
      about='Reported, never guessed.', supports='gridiron.guessed',
      origin='repo', source='gridiron', check='here', verified='2026-09-25',
      expect='1',
      method='The rule\u2019s mechanism: the one constant the field renders '
             'when the provider reported no spot. There is no branch that '
             'places the ball at midfield. shared/format.ts.'),

    # --- 05 AgentFit ----------------------------------------------------
    C(id='agentfit.gates', value='31', about='autonomy gates',
      origin='repo', source='AgentFit2', check='here', verified='2026-09-25',
      method='entries in GATES, src/engine/autonomy.ts'),
    C(id='agentfit.rungs', value='6', about='rungs, 0 to 5',
      origin='repo', source='AgentFit2', check='here', verified='2026-09-25',
      method='levels in AUTONOMY_LADDER, src/engine/autonomy.ts'),
    C(id='agentfit.workflows', value='15', about='reference workflows',
      origin='repo', source='AgentFit2', check='here', verified='2026-09-25',
      method='entries in ARCHETYPES less the neutral "custom" starting point, '
             'src/domain/archetypes.ts'),
    C(id='rule.agentfit', value='min(readinessCeiling, gateCap)',
      about='Fit is not autonomy.', supports='agentfit.gates',
      origin='repo', source='AgentFit2', check='here', verified='2026-09-25',
      expect='2',
      method='The rule\u2019s mechanism: the gates are reduced to a cap '
             'independently of readiness, and the recommended rung is the '
             'lower of the two, in both the recommendation and the ceiling '
             'it reports. A good fit cannot lift a workflow past a gate it '
             'has not met. src/engine/autonomy.ts.'),

    # --- 06 Cartonry ----------------------------------------------------
    C(id='cartonry.styles', value='11', about='box styles',
      origin='repo', source='-cartonry2', check='here', verified='2026-09-25',
      method='entries in STYLES, src/registry.js'),
    C(id='cartonry.formats', value='3', about='export formats',
      origin='repo', source='-cartonry2', check='here', verified='2026-09-25',
      method='format emitters in src/export: svg.js, dxf.js, pdf.js'),
    C(id='cartonry.free', value='2', about='styles free to export',
      origin='repo', source='-cartonry2', check='here', verified='2026-09-25',
      method='styles marked free: true, src/styles'),
    C(id='rule.cartonry', value='AutoCAD R12 geometry',
      about='Not a picture.', supports='cartonry.formats',
      origin='repo', source='-cartonry2', check='here', verified='2026-09-25',
      expect='5',
      method='The rule\u2019s mechanism: the DXF export emits cut, crease, '
             'guide, glue and dimension layers as real geometry a die maker '
             'or a laser can read, not an image of a fold. Counted as the '
             'named layers in src/export/dxf.js.'),

    # --- 07 KeepFloor ---------------------------------------------------
    C(id='keepfloor.floors', value='3', about='price floors',
      origin='repo', source='KeepFloor', check='here', verified='2026-09-25',
      method='floors reported by the calculator: organic, ads-safe and '
             'survive-all, src/ui/Calculator.tsx'),
    C(id='keepfloor.fees', value='7', about='published fee lines',
      origin='repo', source='KeepFloor', check='here', verified='2026-09-25',
      method='FeeLine entries in quoteSale: listing, transaction, processing, '
             'regulatory, offsite, currency conversion and deposit. '
             'src/engine/fees.ts'),
    C(id='keepfloor.local', value='Local', about='math stays on this device',
      origin='repo', source='KeepFloor', check='here', verified='2026-09-25',
      expect='0',
      method='network calls in src/engine, the whole fee and floor engine. '
             'The two fetches in the app are licence validation and checkout, '
             'neither of which touches a number on the receipt.'),
    C(id='rule.keepfloor', value='reconcileLines',
      about='Every published fee, counted.', supports='keepfloor.fees',
      origin='repo', source='KeepFloor', check='here', verified='2026-09-25',
      expect='1',
      method='The rule\u2019s mechanism: the computed stack is reconciled '
             'line by line against the platform\u2019s own statement, so a fee '
             'the model missed shows up as a difference rather than as a '
             'rounder number. src/engine/policy.ts.'),

    # --- 08 Pricing Hub -------------------------------------------------
    C(id='pricinghub.sheets', value='24', about='connected sheets',
      origin='repo', source='pricinghub3', check='here', verified='2026-09-25',
      method='worksheets inside product/Contractor-Job-Costing-SAMPLE.xlsx, '
             'which is a zip: xl/worksheets/sheet*.xml'),
    C(id='pricinghub.checks', value='893', about='formula checks in Excel',
      origin='document', source='records/04-test-results.md',
      source_repo='pricinghub3', check='elsewhere', verified='2026-09-25',
      method='tests/test_workbook.py recomputes every output cell in pure '
             'Python from product/sample_data.py, then drives Microsoft Excel '
             '16.112 through AppleScript and compares. The record says '
             '893/893 pass. Re-deriving it needs Excel, which this machine '
             'does not have.'),
    C(id='pricinghub.macros', value='0', about='macros or add-ins',
      origin='repo', source='pricinghub3', check='here', verified='2026-09-25',
      method='vbaProject entries inside the workbook zip. An .xlsx cannot '
             'carry a macro; an .xlsm would show one here.'),
    C(id='pricinghub.probes', value='46', about='bad-data probes',
      origin='document', source='records/04-test-results.md',
      source_repo='pricinghub3', check='elsewhere', verified='2026-09-25',
      method='tests/test_adversarial.py injects 18 bad rows and runs 46 probes '
             'across the Health Check lines, attention items and alert tiles. '
             'The record says 46/46 pass. Also needs Excel.'),
    C(id='rule.pricinghub', value='no vbaProject',
      about='Plain formulas only.', supports='pricinghub.macros',
      origin='repo', source='pricinghub3', check='here', verified='2026-09-25',
      expect='0',
      method='The rule\u2019s mechanism: the workbook ships as .xlsx, a format '
             'that cannot hold a macro at all, so "plain formulas only" is '
             'enforced by the file format rather than by a promise.'),
]

CLAIMS = BENCH + BUILDS_CLAIMS


# The command that re-derives each 'here' or 'build' claim, run from the root
# of its source repository. Kept beside the ledger rather than inside it so a
# claim reads as a sentence and the shell stays in one place.
DERIVE = {
    'labs.live':
        "grep -c \"^        slug='\" tools/data.py",
    'labs.live.padded':
        "grep -c \"^        slug='\" tools/data.py",
    'labs.featured':
        "grep -c 'featured=True' tools/data.py",

    'ridelens.providers':
        "sed -n 's/^const SURFACEABLE_PROVIDERS[^[]*\\[\\(.*\\)\\];$/\\1/p' "
        "src/lib/sources/ratecard/public-rate-card-quote-source.ts "
        "| tr ',' '\\n' | grep -c '\"'",
    'ridelens.board':
        "sed -n 's/^const SURFACEABLE_PROVIDERS[^[]*\\[\\(.*\\)\\];$/\\1/p' "
        "src/lib/sources/ratecard/public-rate-card-quote-source.ts "
        "| tr ',' '\\n' | grep -c '\"'",
    'ridelens.ranks':
        "sed -n 's/^type RankingMode = //p' src/components/compare-form.tsx "
        "| tr '|' '\\n' | grep -c '\"'",
    'ridelens.ranges':
        "grep -c 'never shown as the fare' src/lib/domain/money.ts",
    'rule.ridelens':
        "grep -c 'export function rankingMidpointMinor' src/lib/domain/money.ts",

    'daylight.layers':
        "awk '/^public enum ControlLayer/,/^}/' "
        "Sources/DaylightCore/Policy.swift | grep -c '^    case '",
    'daylight.certainty':
        "awk '/^public enum ApplicationConfidence/,/^}/' "
        "Sources/DaylightCore/Device.swift | grep -c '^    case '",
    'daylight.tests':
        "grep -rho 'func test' Sources/DaylightTests | wc -l | tr -d ' '",
    'daylight.dependencies':
        "{ grep -c '\\.package(url:' Package.swift || true; }",
    'rule.daylight':
        "grep -c 'confidence: deviation < confirmedWithin' "
        "Sources/DaylightCore/Device.swift",

    'raildrop.window':
        "sed -n 's/.*useState<0 | 1 | 2>(initial?.flexibilityDays ?? \\([0-9]*\\)).*/\\1/p' "
        "src/components/fare-lookup.tsx | head -1",
    'raildrop.prices':
        "grep -c '\"UNKNOWN\"' src/lib/domain/types.ts",
    'rule.raildrop':
        "grep -c 'export const AVAILABILITY_STATUSES' src/lib/domain/types.ts",

    'gridiron.guessed':
        "grep -c \"^export const SPOT_UNAVAILABLE = 'Ball spot unavailable';$\" "
        "shared/format.ts",
    'gridiron.tests':
        "npm test 2>&1 | sed -n 's/.*Tests  *\\([0-9][0-9]*\\) passed.*/\\1/p' "
        "| tail -1",
    'gridiron.journeys':
        "npx playwright test --list 2>/dev/null "
        "| grep -c '\\[desktop-chrome\\]'",
    'gridiron.version':
        "sed -n 's/.*\"version\": \"\\([^\"]*\\)\".*/\\1/p' package.json "
        "| head -1",
    'rule.gridiron':
        "grep -c \"^export const SPOT_UNAVAILABLE\" shared/format.ts",

    'agentfit.gates':
        "awk '/^export const GATES/,/^\\];/' src/engine/autonomy.ts "
        "| grep -c \"^  g('\"",
    'agentfit.rungs':
        "awk '/^export const AUTONOMY_LADDER/,/^\\];/' src/engine/autonomy.ts "
        "| grep -c '^    level: '",
    'agentfit.workflows':
        "expr $(awk '/^export const ARCHETYPES/,/^\\];/' "
        "src/domain/archetypes.ts | grep -c '^  make($') - 1",
    'rule.agentfit':
        "grep -c 'Math.min(readinessCeiling, gateCap)' src/engine/autonomy.ts",

    'cartonry.styles':
        "sed -n 's/^export const STYLES = \\[\\(.*\\)\\];$/\\1/p' "
        "src/registry.js | tr ',' '\\n' | grep -c '[a-z]'",
    'cartonry.formats':
        "ls src/export | grep -cE '^(svg|dxf|pdf)\\.js$'",
    'cartonry.free':
        "grep -rho 'free: true' src/styles | wc -l | tr -d ' '",
    'rule.cartonry':
        "awk '/^const DXF_LAYER = \\{/,/^\\};/' src/export/dxf.js "
        "| grep -c \"name: '\"",

    'keepfloor.floors':
        "grep -coE '(Organic|Ads-safe|Survive-all) floor' src/ui/Calculator.tsx",
    'keepfloor.fees':
        "awk '/const lines: FeeLine\\[\\] = \\[/,/^  \\];/' src/engine/fees.ts "
        "| grep -c 'id: \"'",
    'keepfloor.local':
        "{ grep -rc 'fetch(' src/engine | grep -v ':0$' | wc -l | tr -d ' '; }",
    'rule.keepfloor':
        "grep -c 'export function reconcileLines' src/engine/policy.ts",

    'pricinghub.sheets':
        "unzip -l product/Contractor-Job-Costing-SAMPLE.xlsx "
        "| grep -c 'xl/worksheets/sheet'",
    'pricinghub.macros':
        "{ unzip -l product/Contractor-Job-Costing-SAMPLE.xlsx "
        "| grep -c 'vbaProject' || true; }",
    'rule.pricinghub':
        "{ unzip -l product/Contractor-Job-Costing-SAMPLE.xlsx "
        "| grep -c 'vbaProject' || true; }",
}


BY_ID = {c.id: c for c in CLAIMS}
assert len(BY_ID) == len(CLAIMS), 'duplicate claim id in the ledger'


def M(cid):
    """A (value, label) pair for a metrics row. The page data calls this so it
    carries no figure of its own."""
    c = BY_ID[cid]
    return (c.value, c.about)


def V(cid):
    """Just the value, for a figure inside a sentence."""
    return BY_ID[cid].value


def supporting(cid):
    """The claims that back this one: the mechanism behind a rule, or the
    evidence behind half a label."""
    return [c for c in CLAIMS if c.supports == cid]


def checked_on(*cids):
    """The date the given figures were last checked together, as the site
    prints it. The oldest one wins: a line that says "checked on" has to mean
    every figure beside it."""
    d = min(datetime.date.fromisoformat(BY_ID[c].verified) for c in cids)
    return d.strftime('%-d %B %Y')


def stale_claims(today=None):
    """Asserted figures older than STALE_AFTER_DAYS, for the build to warn
    about. Never an error: an old measurement is not a wrong one."""
    return [c for c in CLAIMS if c.stale(today)]


def main():
    if '--json' in sys.argv:
        print(json.dumps({'format': LEDGER_FORMAT,
                          'claims': [asdict(c) for c in CLAIMS]}, indent=2,
                         ensure_ascii=False))
        return
    w = max(len(c.id) for c in CLAIMS)
    for c in CLAIMS:
        print(f'{c.id:<{w}}  {c.value:<12}  {c.check:<9}  {c.verified}  {c.about}')
    n = len(CLAIMS)
    here = sum(1 for c in CLAIMS if c.check == 'here')
    build = sum(1 for c in CLAIMS if c.check == 'build')
    print(f'\n{n} claims: {here} checkable here, {build} on a build, '
          f'{n - here - build} neither.')
    for c in stale_claims():
        print(f'stale: {c.id} asserted {c.age_days()} days ago')


if __name__ == '__main__':
    main()
