#!/usr/bin/env python3
"""Copy for /evidence, the page that prints the Labs claims ledger.

Every figure on Labs is declared once in claims.py with its source, its method
and the date it was last confirmed. Until this page existed none of that was
visible: the ledger ships in tools/, which the deploy excludes.

Labs and the portfolio share the ledger format and this page's shape, but not
its argument. Nothing on Labs is employer work, so nothing on Labs is asserted:
every figure here is counted out of a repository by a command. The copy says
that, and the build counts the groups rather than restating them, so if that
ever stops being true the page will say so on its own."""

KICKER = 'Evidence'

H1 = ('Nothing here is my word for it.', 'Every figure is counted.')

LEDE = ('These are my own products, so every number on this site comes out of a repository rather than out of a '
        'system you cannot see. Each one is declared below with its source, how it is counted, and the date it '
        'was last confirmed.')

GROUPS = [
    dict(key='checked', n=1,
         kicker='Re-derived here',
         h2=('Counted from source.', 'Offline, in under a second.'),
         lede='A script in this repository counts each of these from the product source, offline. '
              'If one of these numbers moved and the site did not, the check would say so.'),
    dict(key='unchecked', n=2,
         kicker='Re-derivable, not here',
         h2=('Countable, but not here.', 'The method is still written down.'),
         lede='Real counts with real methods that this checkout cannot run on its own: some need installed '
              'dependencies and real time, some live in another repository. The ledger records the method and '
              'does not claim a check it did not perform.'),
    dict(key='asserted', n=3,
         kicker='Asserted',
         h2=('My word, with a date on it.', 'No command can check these.'),
         lede='Figures with no machine source, carrying the date they were last affirmed. This group is empty '
              'on Labs, and the count above is read from the ledger rather than written here, so it will stop '
              'being empty the moment that changes.'),
]

CHECK_WORDS = dict(
    here='runs in this repository, offline',
    build='runs, but needs installed dependencies',
    elsewhere='re-derivable in principle, not on this machine',
    none='no machine source',
)

NOTE_H = 'What this page does not prove'
NOTE = ['A ledger is a record of method, not a guarantee of truth. It shows that every figure on this site has '
        'one declared source and one declared way of being counted, and that the countable ones are counted.',
        'What it does prove is narrower and worth saying plainly: none of these numbers is a claim about work '
        'you cannot inspect. The products are mine, the repositories are real, and the counts come out of them.']

BAND_LABEL = 'The ledger at a glance'

DESCRIPTION = ('The claims ledger for the Labs site: every figure with its source, its method, and the date it '
               'was last confirmed.')
