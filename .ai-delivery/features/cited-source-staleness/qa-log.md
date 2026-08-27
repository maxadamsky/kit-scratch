# Q&A Log: cited-source-staleness

Enabled by `qa_log: on` in `.ai-delivery/config.md`. One entry per exchange, in order.
This log records the reasoning; `framing.md` records the conclusions.

## Phase 0 — Problem Framing

### Q1 — What problem or opportunity are you trying to explore?

**A.** The kit's conventions files go stale and nobody notices. Setup writes conventions
grounded in fetched documentation with a `verified:` date per line; one of those source URLs
was already dead the day it was written — a 404 the kit shipped, caught only by chance.
Nothing re-checks whether a cited source still resolves or whether what it says has changed.
Candidate answers named and deliberately left open: a checker, a re-verification pass, a
shorter shelf life on some claim types, or nothing at all if cost outweighs benefit.

**Facilitator note.** The failure is not that a URL died — URLs always die. It is that the
line carries `verified:` and so asserts a confidence the kit no longer has, with nothing able
to tell the difference.

### Q2 — Who experiences this problem?

**A.** Primary is the agent reading it, and that is what makes it bad: an agent treats
`verified:` as fact and reviews against a rule whose grounding evaporated, silently.
Secondary is the person, who at least might notice a dead link on clicking. The agent is the
worse case because it never clicks. Scale: today one person and a handful of repos, but
assume real installs — conventions and rubrics are written once per project and read on every
skill run after, so read count grows without bound while verification count stays at one.

**Decision recorded.** The primary reader is the agent, not the person.

### Q3 — What does the failure look like today, and what currently catches it?

**A.** Walk-through: an agent hits a rubric item cited to the OWASP input-validation sheet,
marked verified today; six months on it blocks a change on that item. The rule is still
probably right — that is the trap. The outcome usually does not change; the harm is that the
record lies about why the rule is trusted. A slow failure, not a loud one.

Tier-3 lines are the exception: `3-model` conventions and scaffold-default thresholds have no
external source to go stale because they were never grounded. Staleness bites differently by
tier and one policy does not cover both.

The existing six-month re-verification offer is a weak workaround: it fires only on a setup
re-run, which happens after a stack change rather than on a schedule, so conventions rot
fastest where code moves least. It never forces, so it is declined by whoever is in a hurry.

Worst moment is handoff — the inheritor cannot tell a live-source line from a 404 line and
cannot ask the person who ran setup.

**Decision recorded.** This is a trust failure, not a correctness failure. Tiers are separate
objects requiring separate treatment.

### Q4 — If this were solved well, what is different, and what outcome do you actually want?

**A.** The inheritor can see per line whether the grounding is still live and, separately,
whether it was ever grounded at all, without opening forty URLs. They stop treating the file
as one all-or-nothing trust object.

The outcome wanted is honest artifacts as an end in itself — explicitly **not** fewer bad
reviews, because the rule usually stays right and that benefit probably does not exist. The
council must not optimize for it. Rationale: the kit's whole argument is that its records are
trustworthy; a file asserting verification it does not have undermines that claim everywhere,
teaching the reader that the metadata is decorative.

Constraint volunteered: it has to work for someone who installed the kit and does not know it
has a source catalog. Reading the artifact must not require knowing the kit's internals.

**Decision recorded.** Optimization target is artifact honesty, not review quality. This is
binding on the council briefs.

### Q5 — What else are we working within? (portability, network, blast radius, must-nots)

**A.** *Portability:* inherits the no-shell rule strictly — Node under the shared runtime.
The kit is macOS-proven and untested on Windows and Linux; a solution needing a shell does
not ship. *Network:* assume absent at review time, treat presence as a bonus; a check that
only works online makes the artifact honest on connected machines and silent everywhere else.
Fetching belongs in an explicit human-triggered pass — not a hook, not a skill run, not CI.
*Blast radius:* the annotation grammar may change; existing files must stay readable, not
necessarily valid, and a file must declare which grammar it was written under —
`schema_version` exists and nothing reads it.

*Must not:* add a check that cannot fail; silently re-stamp a `verified:` date without an
actual re-check (re-dating is the dishonest act, not the stale date); require the reader to
have network, the catalog, or internals knowledge.

**Decision recorded.** All three must-nots are hard constraints carried into every brief.

### Q6 — Prior art, and what is already ruled out?

**A.** Nothing built inside the kit. Open row W-16 proposes a three-month volatile clock plus
source-and-`verified:` metadata, motivated by Databricks renaming Asset Bundles to
Declarative Automation Bundles in March 2026. The clock was never built.

Certificate expiry transfers — explicit expiry inside the artifact, evaluable offline, fails
loudly. Lockfile and content-hash pinning do not: they detect change, and change is not the
failure — a source can be rewritten wholesale and still support the claim, or be
byte-identical while the claim was a misreading from the start. Link-rot tooling catches the
loudest and rarest case and reaches only `1-docs` lines. Docs-as-tests is a near-miss: it
makes claims fail-able, but prose conventions are not runnable and forcing them to be changes
what the artifact is.

All four candidate shapes go to the council live; nothing ruled out. The null seat may hold
the strongest hand — the honest answer might be that the format should stop asserting
`verified:` at all.

**Decision recorded.** No direction pre-eliminated. Hash- and diff-based approaches are
identified as addressing the wrong failure mode, but that is an argument for the council to
test, not a ruling.

### Q7 — Six months out, how do you know it worked?

**A.** A person who did not run setup can open conventions.md and sort the lines into piles
without leaving the file. Acting on an expired line means exactly one of three moves, all of
which must be real: re-verify and re-date having actually looked; delete, because it is not a
convention this project holds; or demote, dropping it from a grounded tier to a
stated-without-grounding tier. Demotion is expected to be most common and is what a naive
design forgets to allow.

Agent-side: a verify or critique run citing an expired line says so in its own output rather
than citing it as current. That half matters more, since the agent never clicks.

Failure signal: expiry becoming routine noise. Forty expired lines nobody triages re-creates
the original problem with extra steps. The test is not whether lines expire but whether
anything is deleted or demoted. Measurable form: after the first year, the count of
demoted-or-deleted lines is non-zero; if every expired line is re-dated and none dropped, it
is rubber-stamping and the mechanism is theatre.

### Q8 — Anything wrong or missing in the framing?

**A.** Three additions and one correction.

*No central state.* The kit writes these files into other people's repositories, committed to
their git history, touched only when a skill runs. There is no registry, no database, no
kit-side record of what was verified when. Whatever the mechanism knows must be inside the
artifact or it does not exist. This rules out anything shaped like a service.

*Hand editing is invited.* config.md states user edits are team decisions, so the mechanism
must survive a human rewriting a line, deleting an annotation, or adding a convention with no
annotation. It cannot assume the kit wrote everything it reads.

*A fourth pile.* A line a human wrote themselves — no source, no tier, no date — is today
indistinguishable from a kit-written line whose annotation was dropped. A design that cannot
tell "a person asserted this" from "the kit asserted this and lost its grounding" has moved
the honesty problem rather than solved it.

*Correction.* Do not assert that the metadata half of W-16 shipped. An annotation format
resembling the W-16 proposal appears in generated output; whether it was implemented from
W-16 or arrived independently is not known. No lineage should be asserted.

**Decision recorded.** Framing amended on all four points before dispatch. The no-central-
state constraint is treated as direction-killing and is carried into every council brief.

## Phase 1b — Synthesis Review

No questions asked of the user in this phase. Four factual claims were adjudicated by direct
inspection before the synthesis was written; three confirmed defects in artifacts generated
earlier the same day.

- `gates.md:83-84` stamps `tier: 3-model · verified: 2026-08-12` on coverage thresholds
  nobody verified. **Confirmed.**
- The kit ships unannotated lines (Linear Conventions skeleton bullets), so a bare line does
  not mean human authorship. **Confirmed** — pile 4 is unreachable today.
- `schema_version` is read by no script or hook, while `provenanceMatches()` proves the
  offline-frontmatter technique works. **Confirmed.**
- No CI, alerting, or logging exists in either tree. **Confirmed.**

## Phase 2 — Direction Setting

### Q9 — Do you accept the premise challenge?

**A.** Partly. Take the authoring-time fix (never emit a source annotation for a failed
fetch); decline the claim that the format should stop asserting grounding entirely.

**Decision recorded.** The QA bug is split away from the design question and is in scope
regardless of direction.

### Q10 — Which direction?

**A.** A now, B or C later — sequenced rather than combined.

### Q11 — Is the eventual mechanical check ever allowed to block a skill run?

**A.** Blocks, but only in the human-triggered pass. Never at the setup gate, never in a
hook.

**Decision recorded.** This keeps operator's first-night page off the table while still
satisfying the must-not about checks that cannot fail.

### Q12 — Should the grammar reserve room for a snapshot reference?

**A.** No. Add it if and when C happens. An unfilled field would be the kit asserting
structure it is not backing — the defect under repair. Accepted cost: a second schema bump
if C is adopted.

### Q13 — Scope sketch, plus the two undecided items (shelf life, same-day cliff)

**A.** MVP as proposed, plus one addition: the grammar must have somewhere to put a dated
run record, because without it "the pass ran and everything was fine" and "the pass never
ran" are the same file — and the success metric is a count that could come back zero for
either reason.

*Shelf life:* do not invent one. Two options offered — write no expiry at all and let the
reader judge, or keep `expires:` and fill it only where something real determines it. The
user explicitly asked for a recommendation and for an honest "it doesn't hold together" if
warranted.

*Same-day cliff:* not solved in this MVP, but A must not make it structural.

**Facilitator recommendation given (explicitly requested).** Option 1, with one amendment.
Option 2 was rejected because none of this project's four source pages publishes a validity
window, so the field would ship absent on effectively every line — the same
field-nobody-fills problem rejected for the snapshot slot. The amendment: Option 1 as stated
keeps `verified:`, the state-word that caused the problem; change it to an event-word
recording that a source was *read on* a date. Two consequences surfaced that had not been
priced: the same-day cliff does not arise at all under A (no policy, no date-derived
behaviour), and the run record becomes load-bearing rather than supplementary, with the
constraint that it must be itemised rather than a stamp.

**A.** Amendment accepted — read on rather than verified.

### Q14 — Success criteria

**A.** Four. (1) A person who did not run setup sorts every line into grounded / ungrounded
/ human-authored offline without leaving the file — the primary test. (2) Zero occurrences
of `verified:` in generated output and every kit-written line annotated — both
grep-checkable. (3) `schema_version` is read by something; today it is the same defect in
miniature. (4) A negative: no new field ships that setup cannot fill from something real.

**Decision recorded.** Criterion 4 is recorded as a standing design constraint rather than a
test, per the user's own framing of it.

### Q15 — Why this direction?

**A.** The honest fix is mostly a deletion and needs no permission from anything. B is the
part nobody yet knows they need — whether a reader acts on "last read fourteen months ago"
is an empirical question with no data on either side, and A is the cheapest way to get that
data. Building B first would enforce a ritual before knowing whether the prompt works, in a
system whose only enforcement paths turn a trust problem into an outage.

### Q16 — Confirm direction and risk pass

**A.** Direction confirmed as summarized. Risk pass requested.

## Phase 2b — Risk Challenge

One fresh-context subagent, working from the risk brief alone with no workspace access and
no exploration output. Seven risks returned; none merged on de-duplication. Three were
independently re-found from Phase 1 (`OPR-3`, `STR-5`/`STR-6`, `STR-1`); four were new, and
two of those landed on decisions made during direction setting in this same session.

### Q17 — How to handle the risk findings before the brief?

**A.** Revise the direction on both blockers, and add the reader test.

### Q18 — How should the run record be handled?

**A.** Define the rule, ship nothing empty. A pass writes an itemised dated record when it
runs; absence of a record means no pass has ever run.

**Decision recorded.** This resolves the contradiction the risk pass found: as originally
scoped, the run-record slot was a reserved field under a different name, violating the
standing constraint adopted earlier in the same session and matching the snapshot slot
already rejected on that reasoning.

### Q19 — What does an annotation vouch for?

**A.** The derivation, with a stated editor obligation. An annotation claims that someone
read this source on this date **and that this line follows from it**. The file's legend
states that editing an annotated line's text obliges the editor to update or drop its
annotation, and states that the human-authored distinction is heuristic rather than
guaranteed.

**Decision recorded.** The read-event-only alternative was rejected because it stops being
evidence for the claim it sits beside. Success criterion 1 was amended to claim only what
the mechanism delivers — a deliberate, stated weakening rather than a silent one.

**Third revision applied:** a validation step before the grammar is committed — test whether
a model sorts lines differently given an event-word date versus a state-word one. The verb
change is declared to be the substance of the work and the primary reader is an agent, so
the assumption is load-bearing and was untested.

## Phase 3 — Brief

No questions. `brief.md` generated from framing, synthesis (including the revised Chosen
Direction), and the risk challenge. Seven open questions carried forward for the shape
skill, each with a named owner.

---

## Build — Phase 1A (2026-08-27)

### Q20 — The requirements target the kit repo, but the build is running in kit-scratch. Where should this be built?

**A.** Design and specs only; stop before code.

**Decision recorded.** The requirements' § 8 file list is entirely in
`/Users/maxdamsky/Projects/ai-delivery-kit` (Node and markdown). The setup record governing
this build is kit-scratch's, which records Python, pytest, and `greenfield: true` — a stack
`docs/decisions.md` says was *chosen, not detected*, because the repository was empty. The
kit repository has no `.ai-delivery/` of its own, so Phase 4's required conventions and
rubrics describe nothing that this feature touches.

Alternatives declined: building in the kit repository directly (needs setup run there first,
and would discard this session's Phase 1 work); building a Python analogue here as a harness
exercise (exercises the build skill but does not fix the real defect).

Consequence: Phases 1A–1C, unit confirmation, and per-unit specs run here, written against
the real kit files read directly. Implementation is deferred to the kit repository.

### Q21 — FR-015 makes the verb change a merge gate. How should the design treat it?

**A.** Note it as an open gate and defer to the maintainer.

**Decision recorded.** The experiment — two versions of a conventions file, one `verified:`
and one `read_on:`, put to a model to classify each line's grounding — has not run. The
design therefore treats `read_on` as **provisional** and says so at every point it commits to
the name. Owner: kit maintainer.

Alternatives declined: designing sequencing around it as a hard blocker on Unit 1 (premature
while the field name itself is unsettled); running it during this phase (out of scope for a
design-and-specs invocation).

### Phase 1A findings not carried from requirements

**A fourth defect, found by direct inspection.** `conventions.md` carries
`[source: kit design · tier: 1-docs · verified: 2026-08-12]`. "kit design" is neither a path
nor a URL, and `1-docs` is defined as documentation "actually fetched." The kit has no tier
for its own design decisions, so one was borrowed dishonestly. Raised as ADR-003, left open
for the maintainer.

**FR-010's target counted.** Eight of the thirteen Linear Conventions bullets in
`conventions.md` ship with no annotation.

**FR-012 has a contract collision.** `artifact-schemas.md § 8` states the gate prints
*exactly* `MISSING`, `STALE`, or `FRESH`; thirteen skills branch on that word and
`tests/portability-conformance.js` asserts it. Reporting version drift on stdout would break
all three. Resolved as ADR-002: the advisory goes to stderr, leaving stdout and the exit code
byte-for-byte unchanged.

---

## Phase 1B — Detailed Contracts (2026-08-27)

### Q22 — ADR-003: how should the kit's own specification files be cited?

**A.** Add a new `1-kit` tier.

**Decision recorded.** `1-kit` means the kit's own methodology and specification files other
than the active delivery profile, cited by path. `1-profile` is unchanged, and the boundary is
decidable by path: the active profile file is `1-profile`, any other kit file is `1-kit`.

This is the alternative Phase 1A argued against. Its cost was stated when the question was
put and is accepted: the requirements' § 8 says "Custom needs: None", so this is vocabulary
beyond what they authorised, and the requirements' tier preamble now needs editing to match.
That edit is carried as an action in `design/1b-contracts.md`.

Alternatives declined: widening `1-profile` to cover all kit files (Phase 1A's own proposal —
overloads a tier that currently names one specific file); marking the lines `ungrounded`
(understates the truth, since those lines are grounded in a file a reader can open).

### Q23 — FR-015: the verb-change validation gate has not run. What now?

**A.** Keep it provisional — write 1B and the specs with `read_on` marked provisional, and run
the gate before implementation begins in the kit repository.

**Decision recorded.** The contracts are written so the verb is substitutable: `read_on`
appears only in the third slot of an annotation, never in a function name, exported symbol,
file name, or fixture path, and the schema-version reader never matches on it. Conformance
assertion 22 enforces that property, which is what turns "provisional" from a promise into
something checkable.

Alternatives declined: running the gate during this phase (blocks contract work on an
experiment that changes one token); waiving it in writing (ships the untested bet the
requirements deliberately made a merge gate).

### Phase 1B findings not carried from Phase 1A

**The gate's return shape is frozen by the test, not just by the documentation.**
`ai-delivery/tests/portability-conformance.js` asserts `evaluateGate()`'s return with
`assert.deepStrictEqual` in nine cases, so adding a third key to that object fails all nine.
Phase 1A's ADR-002 reached the stderr answer by reasoning about the § 8 stdout contract; this
phase found the harder constraint underneath it. The same test does *not* assert on stderr,
which is what leaves the advisory channel open. Recorded as Contract 5.

**`reference-output/` contradicts the schema specification.** `artifact-schemas.md § 1` says
`rubrics.md` carries `schema_version: 2`, but all three files in the kit's `reference-output/`
carry `schema_version: 1`. Artifacts generated on 2026-08-12 carry conventions 1, gates 1,
rubrics 2 — matching FR-011. `reference-output/` is a stale sample predating the rubrics bump.
Refreshing it is folded into Unit 4's scope rather than raised as a separate defect.

**A row of the conversion mapping cannot be mechanical.** `source: kit design` names no file,
so the conversion cannot derive the replacement path by transformation. Phase 3 must enumerate
the nine affected bullets with their target paths individually — a table of specific edits, not
a rule.

---

## Phase 2 — Decomposition (2026-08-27)

### Q24 — All five units append assertions to the kit's single test file. How should the decomposition handle that conflict?

**A.** Accept and serialize.

**Decision recorded.** `ai-delivery/tests/portability-conformance.js` is treated as this
repository's `requirements.txt` — the decomposition guide's own named example of an acceptable
shared file. The consequence is stated rather than hidden: **there is no parallel first batch**,
and the five units run in six sequential batches. The cost is low because every unit is a small
text edit to a specification file, so serialization spends ordering rather than weeks.

Alternatives declined: splitting into per-unit test files (invents a new test convention in a
repository whose portability is a hard, tested constraint, and nothing currently discovers or
runs multiple test files); moving all assertions into the integration unit (breaks the
profile's test-first rule — assertions would follow the behaviour rather than precede it).

### Q25 — Approve creating the integration issue in Linear?

**A.** Skeletons only, no Linear write.

**Decision recorded.** The six spec skeletons were written to `specs/` and Linear was left
untouched. No issue was created and no issue state was changed; all five units remain in
Backlog. Creating the integration issue is carried as a pending action in `tracker.md § Build`
with the kit maintainer as owner, including the exact shape it must take — top-level,
`integration` label, final milestone, blocked-by CDR-10..14.

### Phase 2 findings

**One conflict was eliminated rather than accepted.** CDR-10 and CDR-11 both had a claim on
`artifact-schemas.md`: the requirements' § 8 puts the § 3/§ 4/§ 5 skeletons under "grammar
definition" but puts FR-010 under the emitter. The file was given entirely to CDR-10 — the
skeleton text is grammar, the behaviour that emits against it is CDR-11's `SKILL.md` change.

**No sub-issues were needed.** Each of the five tracked units is one component at one
architectural boundary, matching implementation grain one-to-one.

---

## Phase 3 — Code Specs (2026-08-27)

Six specs written to `specs/`, 1,450 lines. No new questions were put to the user; the
following were found by direct inspection of the kit repository and are recorded as findings.

### Phase 3 findings

**The file CDR-13 edits contains the defect CDR-13 exists to prevent.** `setup/SKILL.md`'s
re-run staleness table currently reads: *"Artifact `schema_version` vs current → Regenerate
skeletons, carry confirmed content forward, **refresh dates**."* Refreshing dates is exactly
what FR-013 forbids — it would advance every date without any source being re-read, which is
the original defect performed at scale by the fix for it. Changing that row is now the single
most important edit in CDR-13.

**"owner ruling" is a source class the design did not anticipate.** The § 4 Linear Conventions
skeleton holds 16 bullets, counted 2026-08-27: 7 carry no annotation, 4 carry
`source: kit design`, and 5 carry `source: owner ruling` — all nine annotated ones mis-tiered
`1-docs` with a source that is neither a path nor a URL. ADR-003's `1-kit` tier covers "kit
design" cleanly. It does not obviously cover a maintainer's ruling, because no tier describes
a human decision recorded nowhere.

The specs resolve it this way: the rulings *are* recorded — a search on 2026-08-27 found the
initiative-binding rulings discussed across the kit's plan and run-record documents — so each
bullet cites the document carrying its ruling, tier `1-kit`. **Where no record exists, the
honest fix is to record the decision and then cite it**, not to annotate it `3-model` (which
would claim model knowledge for a human decision) and not to leave it bare (which would claim
human authorship of a kit-written line). That is an action for the kit maintainer, carried in
CDR-10's spec.

**`reference-output/` contradicts the specification it illustrates.** All three sample files
carry `schema_version: 1` and `verified:` dates from 2026-08-02, while `artifact-schemas.md`
§ 1 already states rubrics carries 2. Live artifacts generated 2026-08-12 carry 1, 1, 2 —
matching FR-011. The samples are stale, not a second opinion; refreshing them is folded into
CDR-13 rather than raised as a separate defect.

**The conversion is larger than it reads.** A typical generated repository carries roughly 65
annotations — 41 in `conventions.md`, 22 in `rubrics.md`, 2 in `gates.md`, counted 2026-08-27.
CDR-13's spec therefore requires the proposal be grouped by artifact and conversion kind with
counts: a proposal a user cannot read is a proposal they accept without reading, which would
defeat the diff-and-propose guarantee that is the conversion's only safety property.
