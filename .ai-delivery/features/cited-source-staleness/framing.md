# Problem Framing: cited-source-staleness

**Created:** 2026-08-12
**Status:** Completed
**Profile:** software (of config: software)
**Risk challenge:** requested
**Council roster:** constraint, precedent, stress, null, operator (of: constraint, precedent, stress, null, operator)

## Raw Description

The kit's own conventions files go stale and nobody notices. Setup writes conventions
grounded in fetched documentation with a verified date on each line, and today one of those
source URLs was already dead — a 404 the kit shipped and only caught by chance. There's no
mechanism that re-checks whether a cited source still resolves or whether what it says has
changed since. I don't know if the right answer is a checker, a re-verification pass, a
shorter shelf life on some claim types, or nothing at all because the cost outweighs it.
That's what I want explored.

## Who Is Affected

- **Primary: the agent reading the artifact.** An agent treats `verified:` as a fact and
  reviews against a rule whose grounding evaporated, silently. It never clicks the link, so
  it has no path to noticing.
- **Secondary: the person.** At least might notice a dead link on clicking it. This split is
  real, and the agent is the worse case.
- **Scale:** assume real installs, not one repo. The load is asymmetric by construction —
  conventions and rubrics are written once per project and read on every skill run
  afterward, so the read count grows without bound while the verification count stays at one.

## Pain Points — What's Broken Today

- **The record lies about why a rule is trusted.** The rule itself usually stays right, which
  is the trap: this is a trust failure, not a correctness failure, and it never announces
  itself. It surfaces only after a rule that quietly stopped being true has been enforced for
  months.
- **Staleness is not one object; it bites differently by tier.** A `1-docs` line can be
  falsified by fetching its URL. A `3-model` line in conventions.md and a scaffold-default
  threshold in gates.md have no external source to go stale — they were never grounded. One
  policy does not cover both.
- **The only existing mechanism is weak and anti-correlated with need.** Setup's re-run path
  offers re-verification for conventions whose `verified:` date is older than about six
  months, and never forces it. It fires on a stack change, not on a schedule — so conventions
  rot fastest in the repos whose code moves least, which are exactly the repos nobody re-runs
  setup on. And an offer that never forces is declined by whoever is in a hurry, which is
  everyone.
- **The worst moment is handoff.** Someone inheriting the repo reads conventions.md as the
  team's decisions, cannot tell which lines were grounded in a source that still says that
  and which were grounded in a 404, and cannot ask the person who ran setup because that
  person has moved on. First setup is fine — everything was just fetched. A re-run months
  later at least touches the file. At handoff nobody is checking anything and every line
  reads equally authoritative.

## The Opportunity

- The inheritor can see, per line, whether the grounding behind it is still live — and,
  separately, whether it was ever grounded at all — without opening forty URLs.
- They stop treating the file as a single all-or-nothing trust object. Today the only moves
  are believe conventions.md wholesale or re-derive it, and re-deriving is expensive enough
  that people just believe it.
- **The outcome that matters is honest artifacts as an end in itself — explicitly not review
  quality.** The rule usually stays right, so the review-quality gain is probably small and
  the exploration must not optimize for a benefit that likely does not exist. The goal is
  that when a line says `verified: <date>`, that claim is true, and when it cannot be true,
  the line says so instead of pretending.
- **Why that outcome over the review outcome:** this kit's whole argument is that its records
  are trustworthy — plans, gates, findings, conventions. A file that asserts verification it
  does not have undermines that claim everywhere, not only on the line that went stale. The
  cost of the dishonest line is not the bad review it might cause; it is that it teaches the
  reader that the metadata is decorative.

## Constraints

- **Node only, no shell.** Anything executable is a Node script under the kit's shared
  runtime. This is not a preference: the kit is macOS-proven and untested on Windows and
  Linux, and Windows is where shell assumptions break first. A solution that needs a shell is
  a solution that does not ship.
- **Offline by default.** Assume network is absent at review time and treat its presence as a
  bonus. A check that only works online makes the artifact honest on connected machines and
  silent everywhere else, which reintroduces the same problem in a new place. Whatever is
  written into the file must carry enough on its own to be interpreted offline. Fetching, if
  it happens at all, belongs in an explicit human-triggered pass — not a hook, not a skill
  run, not CI, because none of those is guaranteed to have network or to be run at all.
- **The annotation grammar may change; existing files must stay readable.** Not necessarily
  still valid, but a file written under the old grammar must not become unparseable or
  silently misread. If the grammar changes there must be a way to tell which grammar a given
  file was written under. `schema_version` is already written into every artifact and nothing
  currently reads it; that is the obvious place.
- **No central state — the artifact is the only durable memory.** The kit writes these files
  into other people's repositories. conventions.md, gates.md and rubrics.md live in the
  user's project, committed to their git history, and the kit touches them only when a skill
  runs. There is no registry, no database, no kit-side record of what was verified when.
  Whatever the mechanism knows must be inside the artifact, in the user's repo, or it does
  not exist. This rules out anything shaped like a service.
- **Hand editing is invited, not tolerated.** config.md states that user edits are treated as
  team decisions. The mechanism must survive a human rewriting a line, deleting an
  annotation, or adding a convention with no annotation at all. It cannot assume the kit
  wrote everything it reads.
- **Interpretable without kit internals.** It must work for someone who installed the kit and
  has no idea it has a source catalog. Reading a line's annotation must not require network,
  the catalog, or knowledge of the kit's internals.

### Must not

- **Must not add a check that cannot fail.** A mechanism that can only ever say "fine" is
  decoration, and worse than nothing because it looks like assurance.
- **Must not silently rewrite or refresh a `verified:` date without something actually having
  been re-checked.** Refreshing the date is the dishonest act; the stale date is not.
- **Must not require the reader to have network, the kit's source catalog, or knowledge of
  the kit's internals** in order to interpret what a line's annotation is telling them.

## Prior Art and Context

**Inside the kit: nothing built.** There is an open row, W-16, for exactly this, motivated by
a different instance — Databricks renamed Asset Bundles to Declarative Automation Bundles in
March 2026, so shipped content referred to a product name that no longer existed. That row
proposes a three-month volatile clock plus source-and-`verified:` metadata. The clock was
never built. An annotation format resembling the metadata half does appear in generated
output; **whether that was implemented from W-16 or arrived independently is not known, and
no lineage should be asserted.** What is certain either way: the format in use today is
consistent with a design that expected a freshness mechanism which does not exist.

**Certificate expiry — transfers.** It puts an explicit expiry inside the artifact, the
reader evaluates it offline with no network and no registry, and an expired certificate fails
loudly rather than degrading quietly. That matches the constraints exactly.

**Lockfile and content-hash pinning — do not transfer.** Both detect change: the thing you
pinned is not the thing you have now. Here change is not the failure. The OWASP sheet could
be rewritten wholesale and still say what the convention claims; it could also be
byte-identical while the convention was a misreading from the start. A hash tells you the
bytes moved, which is not the question.

**Link-rot tooling — partial.** Catches the loudest and rarest case, the 404. Cheap and
useful, but it reaches only `1-docs` lines. It does nothing for tier-3 lines and nothing for
a source that still resolves but no longer supports the claim.

**Docs-as-tests — interesting near-miss.** It makes the claim executable so it can actually
fail. But these claims are prose conventions: "validation is allowlist-based" is not
runnable, and forcing it to be would change what the artifact is.

**Candidate shapes, all live.** Checker, re-verification pass, shorter shelf life by claim
type, or nothing at all. Nothing is ruled out. The null seat may hold the strongest hand: the
honest answer might be that the format should stop asserting `verified:` at all rather than
that something should verify it.

## Success Signal

**The primary test.** A person who did not run setup opens conventions.md and sorts the lines
into piles without leaving the file. If they cannot do that, nothing shipped that matters.

The piles are four, not three:

1. **Still-grounded** — the grounding behind this line is live.
2. **Expired** — it was grounded, and that grounding is no longer current.
3. **Never-grounded** — the kit asserted this with no external source (tier-3 lines,
   scaffold-default thresholds).
4. **Human-authored** — a person asserted this themselves: no source, no tier, no date.
   Today this is indistinguishable from a kit-written line whose annotation was dropped. If
   the design cannot tell "a person asserted this" from "the kit asserted this and lost its
   grounding," it has not solved the honesty problem — it has moved it.

**What failing looks like in the good world.** Lines read as expired and someone acts, where
acting means exactly one of three moves, all three of which must be real:

- **Re-verify and re-date it**, having actually gone and looked.
- **Delete it**, because it turned out not to be a convention this project holds.
- **Demote it**, dropping it from a grounded tier to a stated-without-grounding tier so it
  stops claiming what it cannot back. This is expected to be the most common move and is the
  one a naive design forgets to allow.

**The agent-side half, which matters more.** A verify or critique run that cites an expired
line says so in its own output — "this rubric item's grounding expired on this date" —
rather than citing it as though it were current. This half matters more because the agent is
the reader that never clicks.

**The signal it went wrong: expiry becoming routine noise.** If the normal state of a mature
project is forty expired lines nobody triages, the mechanism has re-created the original
problem with extra steps — the reader learns to skip the annotation, which is exactly what a
decorative `verified:` teaches. The test is therefore not whether lines expire. It is whether
anything gets deleted or demoted, because those are the moves that prove someone read it
rather than dismissed it.

**Measurable form.** After the first year, the count of demoted-or-deleted lines is non-zero.
If every expired line is re-dated and none is ever dropped, people are rubber-stamping and
the mechanism is theatre.
