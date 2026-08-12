# Exploration Synthesis: cited-source-staleness

**Created:** 2026-08-12
**Synthesis basis:** 5 of 5 mandates examined
**Failed members:** None

## Coverage

| Mandate question | Examined? |
|---|---|
| What is the smallest change to the existing system that solves this framed problem? (constraint, codebase) | examined — response |
| What already exists that could be adopted instead of building? (precedent, web) | examined — response |
| What breaks first at 100x scale or under hostile and malformed input? (stress, framing-only) | examined — response |
| Should this be built at all? (null, framing-only) | examined — response |
| What is missing for the first night on call? (operator, codebase) | examined — response |

No gaps. Every active member returned a clean response; no stubs, no retries, no
section-level defects.

## Candidate Directions

**Roster skew, stated because it shapes what you are choosing between.** This roster
deliberately counterweights builder's bias: it generates minimal, adopt, and no-build
candidates, and never an ambitious purpose-built option. If the right answer is a larger
system than anything below, no seat here was assigned to propose it. You may introduce a
direction the exploration did not surface.

### A. Expiry certificate in the annotation grammar (CON-1, vocabulary precedent PRE-1)

Change only the grammar in `artifact-schemas.md` §1 and the §3/§4/§5 skeletons. Three
edits: grounded tiers gain an `expires:` field evaluated by date arithmetic against the
reader's today; `3-model` lines and scaffold-default thresholds drop `verified:` entirely
and read `ungrounded`; and every line the kit writes gains an annotation, so that a bare
line means "a person wrote this" **by construction**. Expiry attaches per source URL, not
per line, so this project's ~30 grounded lines triage as roughly five sources. Bump
`schema_version`; the migration row already exists in setup's re-run table. The agent half
is one clause added to the §8 contract every skill already copies: a finding citing an
expired line must state the expiry rather than cite it as current.

Complexity `Low` — markdown edits only, no code. PRE-1 supplies proven vocabulary for the
same distinctions (`dead link`, `citation needed`, `failed verification`) plus a documented
triage procedure.

Bearing risks: STR-4 and OPR-6 (the cliff and the flood). CON-1's own admission that the
agent half is prose compliance with nothing verifying it. CON-1 also concedes the shelf-life
number would be invented — the kit stamping a date it cannot justify, which is a smaller
instance of the sin being fixed.

### B. Candidate A plus an offline classifier in the existing runtime (CON-2, fetch component PRE-3)

Everything in A, plus an `annotations` subcommand in `scripts/setup-runtime.js` — a fourth
branch beside `gate`, `detection-files`, `fingerprint`. It reads the artifacts, classifies
each line `grounded` / `expired` / `ungrounded` / `unannotated`, and exits non-zero when
anything is expired. It fetches nothing; expiry is date arithmetic, so it behaves
identically offline. It replaces the "offer, never force" re-verification row with one that
offers exactly three moves per expired source. PRE-3 supplies a Node-API link checker
(`linkinator`, or the narrower `markdown-link-check`) for the separate human-triggered fetch
pass — notably, `lychee` is eliminated by the no-shell constraint because it is a Rust
binary requiring exec.

Complexity `Medium` — the kit's first machine reader of the annotation grammar, which the
grammar must then hold still for.

Bearing risks: OPR-1 is the sharpest — routing an expiry verdict into `evaluateGate` makes
thirteen blocking skill preflights fail over a six-month-old date, diagnosed from one word
with recovery only through a conversational setup interview. OPR-4 (a checker throwing
inside `path-guard.js` denies every Write and Edit). OPR-2 (a pass that half-writes
`conventions.md` is silent, leaves no run record, and cannot be repaired by an agent because
`path-guard.js` H5 denies subagent writes to that file). CON-2 independently names the same
wiring temptation as its own risk.

### C. Snapshot at verification time (PRE-2)

Adopt the Robust Links grammar from the Memento project: record `versiondate` and
`versionurl` alongside the source, with an archive snapshot taken when the claim is
verified. This addresses a gap none of the other candidates close — an expired line becomes
*recoverable*, because the reader can see what the source said when the convention was
written rather than only learning it is gone. That converts demotion from a guess into a
decision.

Bearing risks: requires network at write time and adds a third-party runtime dependency
(archive.org availability, ~15 URL/minute rate limit, sites that block archiving). PRE-2
also reports that the spec's canonical host failed DNS resolution this session and that the
spec self-describes as under experimental revision — a spec to copy, not to depend on.
STR-1 and STR-2 both bear here.

### D. Do not build — assert less (NUL-2)

Drop `verified:` and the tier vocabulary entirely. Write the source URL verbatim where one
exists and nothing at all where none does. A bare URL makes no claim about today; it is
self-evidently a pointer, and it goes stale without ever having lied. A line with no URL is
visibly ungrounded. This delivers three of the four piles with zero durable state, zero
network, zero grammar versioning, and nothing to triage. It gives up the expired pile —
which is precisely the pile the framing predicts nobody will act on. Paired with an
authoring-time rule: do not emit a source line for a fetch that returned non-200.

This candidate is presented because the premise-challenge seat ran. You must explicitly
accept or decline it in direction setting.

### Direction-independent findings

These bear on every candidate above and are not repeated per-candidate:

- **STR-3** — malformed annotations fail open. Truncated fields, `verified: 9999-99-99`,
  unicode-lookalike digits, an empty date field: date parsing yields NaN or a far-future
  value, the comparison against now is false, and the line certifies as still-grounded. The
  garbage lines are exactly the ones most likely to be wrong and they are the ones marked
  clean. This directly violates the framing's must-not.
- **STR-5** — verified dates laundered through merges. A pass that re-dates many lines in
  one commit produces whole-file conflicts resolved wholesale, landing a fresh date beside
  claim text from the other branch. The forbidden dishonest act, reached through version
  control rather than code, with no central state able to contradict it.
- **STR-6** — two grammars inside one file. The version marker is per-file but the state is
  per-line; partial hand migration is certain, and the parser then reads minority-grammar
  lines confidently and wrongly.
- **OPR-3** — the fix ships and is not installed. `claude plugin update` against a local
  marketplace compares `plugin.json` versions, so a content-only commit reports "already at
  the latest version" — a false success. Nothing stamps which kit version produced a given
  artifact's annotations.
- **OPR-5** — works on macOS, misbehaves elsewhere. `tests/portability-conformance.js` is
  invoked by no CI, no hook, and no skill preflight; it runs when a human remembers. An
  install where annotations silently stop expiring is indistinguishable from an install
  where nothing is stale.

## Tensions

### Factual disputes

- **Does the kit assert `verified:` on values nobody verified?** CON-1 (codebase) says yes,
  citing `gates.md:83`. **Adjudicated: confirmed.** Direct read of
  `.ai-delivery/gates.md:83-84` shows `- coverage_line: 80 [source: tiered scaffold,
  confirmed by user · tier: 3-model · verified: 2026-08-12]`. The kit stamps a verification
  date on a scaffold default that was never verified against anything.
- **Does a bare line today mean "a human wrote this"?** CON-1 (codebase) says no — the kit
  itself ships unannotated lines. **Adjudicated: confirmed.** Direct read of
  `.ai-delivery/conventions.md` shows kit-written bare lines in the Linear Conventions
  section (the Priority, Titles, and Labels bullets), emitted from the `artifact-schemas.md`
  §4 skeleton, which ships them bare by design. CON-1's cited line numbers drift by about
  two; the substance holds. Pile 4 is therefore unreachable today by any reading of absence.
- **Is `schema_version` read by nothing?** Asserted in the framing and repeated by OPR-3
  (codebase). **Adjudicated: confirmed.** `grep` over the kit's `scripts/` and `hooks/`
  returns no read of `schema_version`. The adjacent precedent CON-1 cites does exist:
  `provenanceMatches()` at `setup-runtime.js:44` reads `generated_under_profile` from
  rubrics frontmatter by exact line match to decide freshness offline — so the mechanism
  works and is simply not applied to `schema_version`.
- **Does this project have any CI, alerting, or logging to hang a check on?** OPR
  (codebase) says none. **Adjudicated: confirmed.** No `.github` directory exists in either
  the workspace or the kit tree, and `config.md` records `ci_system: null`.
- **Is the Robust Links spec depend-able?** PRE-2 (web, fetched) reports its canonical host
  failed DNS this session and the spec self-describes as experimental. **Unadjudicated** —
  evidence that would settle it: a fetch of `robustlinks.mementoweb.org` from a different
  network, plus the spec's stated stability commitment if one exists.

### Priority tensions (for you to decide in direction setting)

- **Assert more versus assert less.** CON-1/CON-2 (codebase) add a field so the artifact can
  say "this expired"; NUL-1/NUL-2 (framing-only) delete the claim so the artifact never
  asserts what it cannot back. Adding gets you the expired pile and a signal the agent can
  act on. Deleting gets you an artifact that cannot lie, at the cost of never telling a
  reader that something changed — which NUL-3 concedes in its own steelman is the one
  asymmetry a passive pointer cannot fix, since the agent never clicks.
- **Machine verdict versus reader judgment.** CON-2 (codebase) wants a check that can
  mechanically fail, because the framing forbids a check that cannot fail. OPR-1 and OPR-4
  (codebase) show this repository has exactly one status channel and one enforcement path,
  and that routing a verdict into either converts a trust problem into an outage with a
  one-word error message. What a machine verdict gets you is enforceability; what it costs
  is that the only places to put it are load-bearing.
- **Recoverability versus zero external dependency.** PRE-2 (web) makes an expired line
  recoverable by snapshotting the source, which is what turns demotion into an informed
  decision rather than a shrug. The framing's constraints push the other way: no service, no
  network dependency, interpretable with nothing but the file.

## Convergences

- **The same-day expiry cliff.** CON-1 (codebase) and STR-4 (framing-only) independently
  derive that because setup writes every line in one run, every line carries one date and
  one shelf life, so expiry arrives as a step function rather than a distribution.
  **Convergent across disjoint evidence — raises attention, not confidence.** Note the
  boundary: the *outcome* (a flood nobody triages) is stated in the shared framing and is an
  echo, not a convergence. The *mechanism* — same-day authorship causing same-day expiry, and
  the per-source grouping that mitigates it — appears in neither the framing nor either
  member's input to the other.
- **Unparseable must not default to fine.** STR-3 (framing-only) derives that malformed
  annotations classify as still-grounded, and CON-2 (codebase) independently states its
  parser must classify anything it cannot parse as `unannotated` and never drop it.
  **Convergent across disjoint evidence — raises attention, not confidence.** Recorded with
  a caveat: the framing's "must not add a check that cannot fail" sits close to this, so part
  of the agreement may be echo.
- PRE-1's Wikipedia-backlog warning reaches the same flood conclusion but its scale claim is
  `recalled`, so it anchors no convergence and goes to the ledger below.

## Answers by Mandate

- **constraint (codebase).** The cheapest honest fix is mostly a deletion: stop writing
  `verified:` on lines never verified, and start annotating the lines currently shipped
  bare. That pair of grammar edits makes three of the four piles readable with no code, no
  network, and no new file. Add `expires:` only to the two tiers that can rot, scope it per
  source URL so triage is five items not thirty, and stop there. The parser is worth buying
  only if its output never gates a skill run.
- **precedent (web).** Adopt two things that are not code: Wikipedia's inline verifiability
  grammar for the four-pile sort, and Robust Links' `versiondate`/`versionurl` pair so an
  expired line points at what the source said when verified. The only thing worth installing
  is a Node link checker for the explicit re-verification pass. Wikipedia is simultaneously
  the best precedent and the loudest warning — its citation-needed backlog is the "forty
  expired lines nobody triages" outcome, already run for twenty years at scale.
- **stress (framing-only).** The failures under load are not slowdowns, they are lies in the
  artifact, and they run in both directions: throttled fetches expire live sources, malformed
  dates certify garbage as grounded, merge resolution stamps fresh dates onto unverified
  text. Any direction must treat unreachable as a third state distinct from dead and alive,
  fail closed on unparseable annotations, and never let one pass re-date thousands of lines
  in one commit.
- **null (framing-only).** The defect is not that verified dates go stale; it is that a
  one-time fetch was ever allowed to print a date at all. A format promising continuous
  grounding from a single check will lie no matter what policy governs its expiry. Every
  candidate adds machinery to manage a claim the toolkit should stop making, and the
  framing's own success bar concedes the likely outcome is annual rubber-stamping of lines
  that were mostly right anyway.
- **operator (codebase).** There is no CI, no logs, no alerts, and no rollback except the
  user's own git — the artifact is the only channel, so whatever the mechanism knows it must
  say in the file, per line, in plain words. Any design routing an expiry verdict into
  `evaluateGate` or `path-guard.js` converts a trust problem into an outage. Give the pass
  its own dated, human-readable run record inside the artifact, because without it "expired"
  and "never checked" are the same string at 3am.

## Blind-Spot Ledger

| Assertion | By | Status |
|---|---|---|
| `gates.md` stamps `verified:` on unverified scaffold defaults | CON-1 (codebase) | verified — direct read of `.ai-delivery/gates.md:83-84` |
| The kit ships unannotated lines, so absence ≠ human authorship | CON-1 (codebase) | verified — direct read of `conventions.md` Linear section; cited line numbers drift ~2, substance holds |
| `schema_version` is read by nothing | OPR-3 (codebase) | verified — `grep` over kit `scripts/` and `hooks/` returns no read |
| `provenanceMatches()` is precedent for offline frontmatter freshness | CON-1 (codebase) | verified — `setup-runtime.js:44,51` reads `generated_under_profile` by exact line match |
| No CI, alerting, or logging exists in either tree | OPR (codebase) | verified — no `.github` in either tree; `ci_system: null` |
| `claude plugin update` false-succeeds on content-only commits | OPR-3 (codebase) | asserted from kit `CLAUDE.md`; not independently reproduced |
| Wikipedia citation-needed backlog runs to hundreds of thousands, many dated years back | PRE-1 (recalled — unverified) | asserted, unverifiable under diet — never anchors a convergence |
| `linkinator` is MIT licensed | PRE-3 (recalled — unverified) | asserted, unverifiable under diet — verify before adopting |
| Wayback Save Page Now is rate-limited to ~15 URLs/minute | PRE-2 (web, searched) | asserted from a search snippet, not a fetched page |
| `robustlinks.mementoweb.org` failed DNS this session | PRE-2 (web) | asserted, unverifiable now — session-local network state |
| A re-verification pass is an SSRF trigger and a durable injection channel into every future agent run | STR-2 (framing-only) | asserted, unverifiable under diet — no implementation exists to inspect |
| Triage economics of an expiry mechanism match the declined six-month offer | NUL-1 (framing-only) | asserted, self-marked as assumption by the member — no triage-rate data exists |

**What no member could see.** Three evidence classes were absent from this roster's run.
Nobody could observe *actual user behaviour* — whether real installs triage or
rubber-stamp is the load-bearing uncertainty in NUL's case and in the framing's own success
metric, and no seat had access to it. Nobody could test *non-macOS behaviour*; OPR flagged
the portability gap but could only read that the conformance test goes unrun. And nobody
read the *W-16 row itself* — its exact proposal is known here only through the framing's
paraphrase, so no member could check whether today's annotation format matches what W-16
specified.

## Chosen Direction

**Direction:** Candidate A now, B or C later — sequenced, not combined. Fix the artifact's
honesty in the annotation grammar alone, with no code, no network, and no new enforcement;
then decide on evidence whether a mechanical classifier (B) is needed.

**Rationale:** The honest fix is mostly a deletion and needs no permission from anything —
stop writing a state-word the kit cannot back, annotate the lines it currently ships bare,
and the artifact stops lying without a line of code, a network call, or a decision anyone
has to be present for. B is the part nobody yet knows they need: whether a reader told "last
read fourteen months ago" ever acts on it is an empirical question with no data on either
side, and A is the cheapest way to get that data. Building B first would enforce a ritual
before knowing whether the prompt works, in a system whose only enforcement paths turn a
trust problem into an outage (OPR-1, OPR-4).

**Scope (MVP):**

1. Replace `verified:` with an event-word field recording that a source was **read on** a
   date. No `expires:`, no computed staleness, no kit-stated policy. The verb change is the
   substance: a state-word invites the reader to hear a standing guarantee (NUL-1), an
   event-word states a fact that stays true and asserts nothing about today.
2. `3-model` lines and scaffold-default thresholds drop the field entirely and read as
   ungrounded — the fix for the confirmed defect at `gates.md:83` (CON-1, adjudicated).
3. Every kit-written line carries an annotation, including the Linear Conventions skeleton
   bullets that currently ship bare, so absence of an annotation means human authorship **by
   construction** (CON-1, adjudicated). This is what makes pile 4 reachable.
4. `schema_version` bumped **and actually read**, following the `provenanceMatches()` pattern
   at `setup-runtime.js:44` that already works offline.
5. Setup never emits a source annotation for a fetch that returned non-200 (NUL-2, the
   accepted half of the premise challenge).
6. The grammar states the **rule** for a run record without emitting an empty one: when a
   pass runs it writes an itemised, dated record distinguishing checked, unreachable, and
   never-grounded (OPR closing statement; STR-1 requires unreachable as a third state
   distinct from dead and alive), and **absence of a record means no pass has ever run**.
   Nothing is emitted until something real fills it. A file-level record is chosen over
   per-line re-dating because it does not have the merge-conflict shape of STR-5. *(Revised
   after the risk challenge — see Revisions below.)*
7. One clause in the §8 contract: a finding citing a line states when its source was last
   read rather than implying currency.

**Explicitly excluded:** the classifier subcommand (B) and snapshotting (C), both deferred
by the sequencing decision; any automated fetching, re-dating, or scheduled job; anything
touching the setup gate, `path-guard.js`, or CI. No reserved snapshot field — adopting C
later costs a second schema bump and migration, accepted knowingly.

**Success criteria:**

1. A person who did not run setup sorts every line in `conventions.md` and `gates.md` into
   grounded / ungrounded / human-authored, offline, without leaving the file. Three piles
   cleanly, the fourth as reader judgment. This is the primary test — it either holds or
   nothing shipped that matters.
2. Zero occurrences of `verified:` in generated output, and every kit-written line carries
   an annotation. Both halves are grep-checkable.
3. `schema_version` is read by something. Today it is written by every artifact and consumed
   by nothing — the same defect in miniature. If A ships a new grammar without wiring it,
   the blast-radius constraint fails on day one.

**Constraints (beyond the framing):**

- **Standing design constraint:** no new field ships that setup cannot fill from something
  real. This is the general form of the `expires:` mistake and applies past this work — it
  would also have caught the reserved snapshot slot.

**Premise challenge:** NUL-1 — the toolkit was never entitled to print a date at all,
because a format promising continuous grounding from a one-shot fetch will lie regardless of
expiry policy — **partly accepted**. Accepted: the authoring-time fix (never emit a source
annotation for a failed fetch), which is the only thing that would have prevented the
originating 404. Declined: the claim that the format should stop asserting grounding
entirely, on the grounds NUL-3's own steelman supplies — demotion needs a tier to demote
into, and a bare URL cannot say "this was grounded and no longer is."

**Resolved trade-offs:**

- *Assert more vs assert less* → both. A adds a field to lines that can rot and deletes the
  claim from lines that never could. Resolved by the direction choice itself, not asked.
- *Machine verdict vs reader judgment* → the eventual check may genuinely fail, but only
  within the human-triggered pass; never at the setup gate, never in a hook. Rationale:
  OPR-1 and OPR-4 show this repository has exactly one status channel and one enforcement
  path, and routing a verdict into either converts a trust problem into an outage diagnosed
  from a single word. CON-2 made buying B conditional on precisely this.
- *Recoverability vs zero external dependency* → no snapshot slot reserved. An unfilled
  field would be the kit asserting structure it is not backing, which is the defect under
  repair.
- *Shelf life* → **no policy at all.** Any figure the kit picked would be a date it cannot
  justify — the same sin at lower stakes (CON-1's own admission). Two options were weighed:
  write no expiry and let the reader judge, or keep `expires:` and fill it only where
  something real determines it. The second was rejected because for this project's actual
  sources — PEP 8, the pytest good-practices page, two OWASP cheat sheets — nothing publishes
  a validity window, so the field would ship absent on effectively every line, which is the
  field-nobody-fills problem already rejected for the snapshot slot. HTTP cache headers were
  considered and rejected as CDN behaviour rather than content validity.
- *Same-day expiry cliff* (CON-1 + STR-4, convergent) → **B's problem, recorded as B's
  problem.** Under this direction the cliff does not merely shrink, it does not arise: there
  is no cliff without a policy converting uniform dates into a uniform expiry event, and A
  has no date-derived behaviour at all. A must bake in no assumption of uniform dates.

**Known cost, accepted:** the agent-side half gets weaker. A verify run can now say only
"grounded in a source last read fourteen months ago" and leaves the inference to the reader,
rather than "this expired on this date." That is a fact rather than a policy verdict, so it
is more honest, but it is a weaker prompt. If nobody acts on it, A alone will not produce a
non-zero demotion count — and that result is itself the evidence that the prompt must come
from B.

### Revisions after the risk challenge

Three changes, made because the risk pass found two internal contradictions and one untested
assumption that the exploration had not reached.

**1. The run record became a rule, not a slot.** As originally scoped, item 6 defined a
grammar slot nothing in A would fill — which is a reserved field under a different name, and
therefore a violation of the standing constraint adopted in the same session, and the same
object already rejected for the snapshot reference. An always-empty record also reads as "no
problems found" to a reader who does not know it is unfillable. Item 6 now states the rule
and emits nothing: a pass writes a record when it runs, and absence means no pass has run.
That preserves the ran-and-fine versus never-ran distinction, which was the whole reason the
item existed, while shipping nothing empty.

**2. An annotation's promise is now explicit: the derivation, with a stated editor
obligation.** The risk pass found a failure no council member reached — hand editing is
*invited*, so a human who rewrites the text of a kit-written line while leaving its
annotation attached produces a line whose annotation vouches for wording the cited source
never contained. That is the original failure re-created inside the new grammar, and worse,
because the reader has been told the metadata is now trustworthy. Decided:

- An annotation claims that **someone read this source on this date and this line follows
  from it** — the derivation, not merely the read event. The read-event-only reading was
  rejected because it stops being evidence for the claim it sits beside, which removes most
  of the reason to carry it.
- The file's own legend states the editor's obligation: **editing the text of an annotated
  line obliges you to update or drop its annotation.** Nothing enforces this; it is a stated
  duty, consistent with how the kit already treats read-modify-write rules it cannot hook.
- The legend also states that the **human-authored pile is heuristic, not guaranteed.**
  Success criterion 1 is amended accordingly — it claims what the mechanism delivers rather
  than certainty it cannot. This weakens the criterion honestly rather than silently, which
  is the only move consistent with the goal.

**3. A validation step was added before the grammar is committed.** The direction declares
the verb change to be its substance while the framing declares the agent the worse-affected
reader, and nothing tested whether a model reads an event-word date differently from a
state-word one. Before committing the grammar: show a model two versions of the same
conventions file and ask it to sort the lines by grounding. If it cannot distinguish them,
the fix is in the surrounding wording, not the field name — and the accepted cost of a
weaker agent-side prompt would otherwise be paid for nothing.

### Open risks carried into the brief

Not resolved here, recorded as live:

- **The deferral has no instrument** (risk-pass top concern; independently re-found as
  OPR-3). No telemetry, no registry, files in other people's repositories — so "decide B on
  evidence" currently has no trigger, no data source, and no owner. Either a specific
  observation gets named (a hand-audit of dogfood repos at a fixed date, a question asked
  during a setup re-run) or the evidence framing should be dropped in favour of admitting
  this is a standing design choice.
- **Old-file behaviour is undefined** (independently re-found as STR-5, STR-6). Every
  migration path available appears to violate a stated must-not; leaving old files legibly
  old is probably the honest answer and needs to be a decision rather than an omission.
- **"No code" is not accurate** — the §8 contract clause lands in every skill file, which is
  the fan-out that priced this direction as cheap. The price should be counted before
  committing.
- **Transient fetch failures become permanent ungrounded lines** (independently re-found as
  STR-1, inverted). A rate-limit during one setup run is indistinguishable in the file from
  a source that never existed.
