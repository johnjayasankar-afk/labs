#!/usr/bin/env python3
"""Re-derives the figures in tools/claims.py and reports drift. Dev-only:
tools/ is excluded from the deploy by .vercelignore.

    python3 tools/verify_claims.py           # everything that runs in a second
    python3 tools/verify_claims.py --build   # also the ones that need a build
    python3 tools/verify_claims.py --all     # same as --build

This file is byte-identical in the portfolio and Labs repositories, because
both ledgers declare the same LEDGER_FORMAT and the same Claim fields. Diff
them before changing either:

    diff tools/verify_claims.py ../labs/tools/verify_claims.py

It checks three things, and keeps them apart in the output:

  IN USE      every claim the ledger declares is referenced by the page data,
              and the page data refers to no claim that is not declared.
              A figure nothing prints is a figure nobody maintains.
  DERIVED     a command re-derives the value from its source repository.
              Catches the site going stale when the source is edited.
  UNCHECKED   the ledger says this cannot be re-derived here, and it is
              reported as unchecked. It never counts as a pass.

A missing source repository is a failure to check, not a pass. Set
CLAIMS_REPO_ROOT if the product repositories are not siblings of this one.

Exit status is 1 if any IN USE or DERIVED check failed, 0 otherwise. An
unchecked claim never fails the run; it is counted and named, every time, so
the summary can never be read as "everything verified"."""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import claims as L  # noqa: E402

REPO_ROOT = os.environ.get('CLAIMS_REPO_ROOT') or os.path.dirname(ROOT)
SUPPORTED_FORMAT = 1

GREEN, RED, DIM, YELL, OFF = '\033[32m', '\033[31m', '\033[2m', '\033[33m', '\033[0m'
if not sys.stdout.isatty():
    GREEN = RED = DIM = YELL = OFF = ''


def run(cmd, cwd):
    """Run a derivation. Returns (stdout stripped, error or '')."""
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True,
                           text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return '', 'timed out after 15 minutes'
    out = p.stdout.strip()
    if not out:
        why = (p.stderr.strip().splitlines() or ['no output'])[-1]
        return '', why
    return out.splitlines()[-1].strip(), ''


def main():
    want_build = '--build' in sys.argv or '--all' in sys.argv

    if L.LEDGER_FORMAT != SUPPORTED_FORMAT:
        print(f'{RED}ledger format {L.LEDGER_FORMAT}, verifier speaks '
              f'{SUPPORTED_FORMAT}{OFF}')
        return 2

    # The ledger has to be internally consistent before it can check anything.
    ids = [c.id for c in L.CLAIMS]
    problems = []
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        problems.append(f'duplicate claim ids: {", ".join(dupes)}')
    for c in L.CLAIMS:
        if c.check in ('here', 'build') and c.id not in L.DERIVE:
            problems.append(f'{c.id}: check={c.check} but no derivation')
        if c.check not in ('here', 'build', 'elsewhere', 'none'):
            problems.append(f'{c.id}: unknown check {c.check!r}')
        if c.origin not in ('repo', 'document', 'asserted'):
            problems.append(f'{c.id}: unknown origin {c.origin!r}')
    for key in L.DERIVE:
        if key not in ids:
            problems.append(f'derivation {key}: no such claim')
    if problems:
        print(f'{RED}the ledger itself is wrong{OFF}')
        for p in problems:
            print(f'  {p}')
        return 2

    site_fail, derive_fail, derived, unchecked, asserted = [], [], 0, [], []

    print(f'{len(L.CLAIMS)} claims, ledger format {L.LEDGER_FORMAT}\n')
    print('IN USE')
    data = ''
    for name in sorted(os.listdir(HERE)):
        if name.startswith('data') and name.endswith('.py'):
            with open(os.path.join(HERE, name), encoding='utf-8') as fh:
                data += fh.read()
    for c in L.CLAIMS:
        if c.supports:
            if c.supports not in [x.id for x in L.CLAIMS]:
                print(f'  {RED}dangling{OFF}  {c.id}  supports {c.supports}, '
                      f'which the ledger does not declare')
                site_fail.append(c.id)
            continue
        if f"'{c.id}'" not in data:
            print(f'  {RED}unused{OFF}  {c.id}  declared but nothing on the '
                  f'site prints it')
            site_fail.append(c.id)
    for ref in sorted(set(re.findall(r"[MV]\('([a-z0-9.\-]+)'\)", data))):
        if ref not in [c.id for c in L.CLAIMS]:
            print(f'  {RED}missing{OFF}  {ref}  the page data asks for a claim '
                  f'the ledger does not declare')
            site_fail.append(ref)
    if not site_fail:
        print(f'  {GREEN}ok{OFF}  every claim is printed or supports one '
              f'that is, and every figure printed is a claim')

    print('\nDERIVED')
    for c in L.CLAIMS:
        if c.check == 'here' or (c.check == 'build' and want_build):
            repo = c.source if c.origin == 'repo' else c.source_repo
            cwd = os.path.join(REPO_ROOT, repo)
            if not os.path.isdir(cwd):
                print(f'  {YELL}no repo{OFF}  {c.id}  {repo} not found under '
                      f'{REPO_ROOT}')
                unchecked.append((c, f'{repo} is not checked out here'))
                continue
            got, err = run(L.DERIVE[c.id], cwd)
            want = c.expected()
            if err:
                print(f'  {YELL}no answer{OFF}  {c.id}  {err}')
                unchecked.append((c, err))
            elif got == want:
                print(f'  {GREEN}ok{OFF}  {c.id} = {got}  {DIM}{c.method}{OFF}')
                derived += 1
            else:
                print(f'  {RED}DRIFT{OFF}  {c.id}: the site says {want}, '
                      f'{repo} says {got}')
                print(f'         {c.method}')
                derive_fail.append((c, got))
        elif c.check == 'build':
            unchecked.append((c, 'needs a build; re-run with --build'))
        elif c.check == 'elsewhere':
            unchecked.append((c, 'not re-derivable on this machine'))
        else:
            asserted.append(c)

    print('\nUNCHECKED')
    if unchecked:
        for c, why in unchecked:
            print(f'  {YELL}·{OFF} {c.id} = {c.value}  ({why})')
    else:
        print(f'  {DIM}none{OFF}')

    print('\nASSERTED')
    if asserted:
        for c in asserted:
            print(f'  {DIM}·{OFF} {c.id} = {c.value}  '
                  f'{DIM}affirmed {c.verified}{OFF}')
    else:
        print(f'  {DIM}none{OFF}')

    stale = L.stale_claims()
    if stale:
        print(f'\n{YELL}STALE{OFF}  asserted more than {L.STALE_AFTER_DAYS} '
              f'days ago. Not an error: an old measurement is not a wrong one.')
        for c in stale:
            print(f'  {YELL}·{OFF} {c.id} = {c.value}  '
                  f'({c.age_days()} days)')

    total = len(L.CLAIMS)
    print(f'\n{derived} of {total} re-derived. '
          f'{len(unchecked)} not checked. '
          f'{len(asserted)} asserted, never checked by anything.')
    if site_fail:
        print(f'{RED}{len(set(site_fail))} claims are out of step with the '
              f'page data.{OFF}')
    if derive_fail:
        print(f'{RED}{len(derive_fail)} figures on the site no longer match '
              f'their source:{OFF}')
        for c, got in derive_fail:
            print(f'  {c.id}: site {c.value} → source {got}')
    if not want_build:
        print(f'{DIM}Run with --build to check the figures that need a test '
              f'run.{OFF}')
    return 1 if (site_fail or derive_fail) else 0


if __name__ == '__main__':
    sys.exit(main())
