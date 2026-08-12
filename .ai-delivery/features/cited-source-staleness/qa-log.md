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
