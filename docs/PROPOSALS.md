# Proposals

One question this site should answer before it builds anything else. Argument,
cost, recommendation. Nothing here has been built.

---

## Eight products on one bench, held as equals

### The question, as it was put

Labs presents eight products as equals on one bench, and they are not equals.
Gridiron is a large codebase with a licensed-provider abstraction and hundreds
of tests; KeepFloor is a fee calculator. Both get a card, three figures and a
rule. Is the flatness the point, or does it flatten the one build that would
make someone stop scrolling?

### First, the measurement

Lines of TypeScript, JavaScript, Swift and Python in each product's repository,
excluding `node_modules`, `dist` and build output, counted 25 September 2026:

```
gridiron       61,693      RailDrop3      17,511
RideLens2      50,719      Daylight       17,098
AgentFit2      18,100      KeepFloor      10,221
                           -cartonry2     10,009
                           pricinghub3     2,774
```

Two things fall out of this that change the question.

**The gap is not one build against seven.** It is two against six. RideLens is
50,719 lines, within a fifth of Gridiron, and it is already featured. The
premise that Gridiron alone would stop someone scrolling does not survive the
count.

**The floor is higher than it looks.** KeepFloor is 10,221 lines with a
seven-line published fee stack, three price floors, a reconciliation against the
platform's own statement, and its own test files. Pricing Hub at 2,774 lines is
the genuine outlier, and most of what it is does not live in source at all: it
is a 24-sheet workbook whose 893 formula checks are driven through Excel. Its
line count measures the harness, not the product.

So the real spread is not 22 to 1. It is: two large web applications, three
mid-sized ones, two small focused tools, and one product that is not a codebase.

### What the flatness actually buys

The bench's argument is not "these are the same size". It is "these are held to
the same standard", and the page now proves that rather than asserting it. Every
card carries three figures counted from the product's own repository, and every
card carries one rule with a named mechanism behind it. As of this cycle all
eight rules have one: a function, a constant or a type that enforces the
promise, recorded in `tools/claims.py` and re-derived by
`tools/verify_claims.py`.

That is a claim a bench of eight can make and a showcase of one cannot. Pricing
Hub's "plain formulas only" is enforced by the file format: an `.xlsx` cannot
hold a macro. Gridiron's "reported, never guessed" is enforced by a single
exported constant and the absence of any branch that would place the ball at
midfield. Those are the same kind of claim at very different scales, and putting
them side by side is the point. A page that showed only Gridiron would be a demo
reel. A page that shows eight, each with its refusal named and checkable, is an
argument about how the person works.

### What the flatness costs

A visitor who scrolls the bench in twenty seconds sees eight equally sized cards
and has no way to know that two of them are large applications and one of them
is a spreadsheet. Everything on the page is designed to be scannable and
comparable, so nothing on the page communicates scale. The three figures make
this worse rather than better: "11 box styles" and "667 unit and integration
tests" sit in the same slot, in the same type, and only one of them is a
statement about engineering weight.

That is a real cost, and it is paid by exactly the reader the site is for:
someone giving it ninety seconds.

### What I would change

**Not the flatness. The figures.**

The three figures per card are the entire evidentiary content of the page, and
they currently answer "what does it do" rather than "how much is there". Add a
fourth, in smaller type, that is the same question for every build and therefore
comparable across them: **how much of it there is, and how much of it is
tested.** Lines of source and tests, counted from the repository the same way
the other figures are, through the same ledger.

That gives a scanner the scale they cannot currently see, without breaking the
bench:

```
Gridiron     61,693 lines · 667 tests
KeepFloor    10,221 lines · 31 test files
Pricing Hub  a workbook, not a codebase · 893 formula checks
```

The third line is the interesting one. Pricing Hub cannot answer the question in
the same units, and saying so is more informative than leaving the slot empty or
filling it with a number that does not mean the same thing. That is the same
move every product on this bench makes about its own data.

The featured and also-shipped split already carries meaning as of this cycle:
the four featured builds are the four with a full case study on the portfolio,
and both section headings now say so. Scale is a different axis from depth of
writeup, and conflating them is what made the split look arbitrary.

### What would be lost

The cards get denser, and a fourth figure is a fourth thing to keep true. The
cost of keeping it true is now low: it goes in `tools/claims.py` with a
derivation command like every other figure, and `tools/verify_claims.py` reports
drift. The real loss is visual: three figures fit the card's rhythm and four may
not, which is a design problem to solve rather than an argument against.

There is also a version of this that is worse than doing nothing. If the fourth
figure is presented as a ranking, the bench becomes a leaderboard and the
smaller builds read as the ones that did not make it. The figure has to sit as
scale, in quieter type than the three above it, next to a line count that Pricing
Hub is allowed to decline.

### Cost

Small. One derivation per product in `tools/claims.py`, one slot in the card
template, and a decision about what Pricing Hub says instead of a number.

---

## Decided: no live embeds on this page

The portfolio embeds RideLens, RailDrop and Gridiron live in their case studies,
and as of cycle 22 that works properly: the preview ships as a still and the
frame comes forward only when the product says it rendered. The mechanism is
built and shared, so putting one on each featured card here is now cheap.

It still should not happen, for two reasons that are about this page rather than
about the mechanism.

**A launcher's job is the click.** A case study is a long read where a live frame
earns its space, because the alternative is leaving the page. Here the product is
one click away and the card already carries a worked example of it running. An
embed would put a third rendering of the same product on the same card, under
the schematic that was built to stand in for exactly that.

**It would double the page everyone lands on.** The Labs index transfers 203 KB
today, measured 25 September 2026. Four embeds would add four cross-origin
document loads, each pulling its own framework, fonts and data, on the one page
every visitor sees first. The portfolio pays that cost on a case study a reader
chose to open. Charging it at the front door is a different trade.

Revisit if the schematics ever stop being built, or if a build arrives that
cannot be shown as a worked example.

## Related, and open elsewhere

**Per-build pages on this domain.** Decided and recorded in `README.md`: Labs
stays a single launcher. The reasoning is there rather than here because it is a
decision, not a proposal.

**Where the case studies live.** The portfolio's `docs/PROPOSALS.md` argues that
question from its side and recommends keeping both, with reciprocal links. It
depends on this site not growing case studies of its own, which the README
decision settles.

**The subdomains and the framing headers.** `docs/DOMAINS.md`.
