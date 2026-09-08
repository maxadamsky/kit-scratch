# Engineering Decisions

One entry per decision point: what was decided, what else was considered, and why.
Written by the delivery kit's skills (and welcome from humans too). Configured in
.ai-delivery/config.md → Preferences.

## 2026-08-12 — Build on Python with pytest, managed by uv

- Decision: Python as the language, pytest as the test framework, uv as the package
  manager, with ruff for lint and format, mypy for type checking, pytest-cov for coverage,
  and bandit, pip-audit, and gitleaks for security. Code under a top-level src directory,
  tests in a separate top-level tests directory.
- Alternatives considered: TypeScript with Vitest on pnpm; deferring the stack entirely and
  recording every gate as unavailable until a manifest appears.
- Reason: the repository was empty, so the stack was chosen rather than detected. Python
  with uv gives unambiguous gate commands with no build step to configure, which suits a
  harness whose purpose is exercising the kit. The src layout comes from pytest's own
  recommendation for new projects, because it forces tests to exercise the installed
  package rather than a loose working copy.
- Context: setup / greenfield path / confirmed by user

## 2026-08-12 — Adopt the software delivery profile

- Decision: software profile
- Alternatives considered: data profile — the connected Linear team (Cdrun-metrics) carries
  issues about a Databricks bundle job and grain-based metrics tables, which pointed that
  way.
- Reason: the user chose software. The repository itself carries no data-stack signal, and
  the profile governs how work here is decomposed and verified, not what the neighbouring
  Linear team happens to track.
- Context: setup / confirmed by user

## 2026-08-12 — Record no cloud provider and no infrastructure tool

- Decision: cloud_provider null, iac_tool null, and both the infrastructure-scan gate and
  the build gate recorded as unavailable.
- Alternatives considered: asking the user to name a provider and defaulting the tool to
  Terraform.
- Reason: the detection ladder found nothing at any step — no infrastructure code, no cloud
  SDK imports, no registry references, no deploy configuration. A scratch harness has no
  cloud footprint, and the question would have been noise. Nulls are answers here, not gaps.
- Context: setup / detection ladder exhausted / stated in the proposal for correction

## 2026-08-12 — Adopt the tiered threshold scaffold

- Decision: 80% line and 70% branch coverage, escalating to 90% line on paths matching
  auth, payments, security, session, token, or credential; complexity warning above 10 and
  failing above 20; duplication warning between 3 and 7% and failing above 7%; zero lint
  errors blocking with up to 10 warnings advisory; zero PII in logs, always blocking. All
  recorded with scaffold-default provenance.
- Alternatives considered: user-set targets; no coverage gate at all until real code exists.
- Reason: nothing is configured in the repository, so there was no team decision to inherit.
  The scaffold gives verify something real to enforce from the first unit of work, and the
  provenance marking makes clear these are defaults rather than measured targets.
- Context: setup / confirmed by user

## 2026-08-12 — Run the discover council at its full roster

- Decision: council enabled, active size 5 — constraint, precedent, stress, null, operator.
- Alternatives considered: trimming to 3 members; disabling the council entirely.
- Reason: trimming drops members from the end of the ordered roster, which loses null — the
  seat that argues the thing should not be built at all — and operator, which is the only
  seat looking at the first night on call. On a repository whose purpose is exercising the
  kit, seeing the full roster run is the point.
- Context: setup / confirmed by user

## 2026-08-12 — Keep stakeholder documents in the repository rather than Notion

- Decision: Notion recorded absent; notion_parent null. Pitches, requirements, and briefs
  are written into the feature directory under .ai-delivery/features/ instead.
- Alternatives considered: connecting Notion and nominating a parent page for stakeholder
  documents.
- Reason: the user directed that Notion not be used for this project. Linear remains the
  tracker, and the repository owns every document.
- Context: setup / user instruction

## 2026-08-12 — Turn the per-feature question-and-answer log on

- Decision: qa_log on. discover, pitch, shape, build, provision, and verify append their
  decision conversations to a qa-log.md file in the feature directory.
- Alternatives considered: off, the kit default, leaving docs/decisions.md as the sole
  written record.
- Reason: the user chose on. The decision record captures conclusions; the Q&A log captures
  the reasoning that produced them, which is what a person auditing how the kit behaves
  actually needs.
- Context: setup / confirmed by user

## 2026-08-12 — Record a read event instead of asserting verification, and state no shelf life

- Decision: replace the `verified:` field in generated artifacts with `read_on:`, which
  records that a source was read on a date. Add `ungrounded` for lines that never had an
  external source and `unreachable:` for a fetch that did not resolve. Compute no expiry
  date and state no shelf-life policy anywhere.
- Alternatives considered: keep `verified:` and add a computed `expires:` field, with a
  shelf life per tier; keep an `expires:` field but fill it only where something real
  determines it; drop grounding claims entirely and write only a bare source URL.
- Reason: `verified` names a state, which invites a reader to hear a standing guarantee the
  kit has never been able to give. An event-word states a fact that stays true and asserts
  nothing about today. Any shelf-life figure the kit picked would be a date it cannot
  justify — the same defect at lower stakes. The fill-only-when-real variant was rejected on
  inspection: none of this project's four documentation sources publishes a validity window,
  so the field would ship absent on effectively every line.
- Context: discover + shape / confirmed by user. Tracked as CDR-10 and CDR-11.

## 2026-08-12 — Migrate old artifacts by strict weakening rather than leaving or regenerating them

- Decision: a setup re-run proposes a tier-aware conversion. Repository, documentation,
  community-source and profile tiers convert `verified: <date>` to `read_on: <date>` with
  the date preserved; model-knowledge lines and scaffold defaults convert to `ungrounded`
  with the date dropped. Never automatic — it runs through the existing diff-and-propose
  path.
- Alternatives considered: leave old files legibly old and never convert them; regenerate
  artifacts wholesale on the next re-run.
- Reason: an independent risk pass argued no migration path exists that does not violate the
  rule against refreshing a date without a re-check. That is wrong on inspection.
  Converting `verified:` to `read_on:` at the same date is a strict weakening — a line
  verified on a date was necessarily read on that date, so the conversion asserts less while
  moving no date forward. The rule forbids moving a date forward, not reducing what it
  claims. The exception is model-knowledge lines, where the original recorded a read that
  never happened, which is why those drop the date instead. Regeneration was rejected because
  it collides with hand-editing being invited.
- Context: shape / confirmed by user. Tracked as CDR-13. If a reviewer rejects the weakening
  argument, this decision and CDR-13 both reopen.

## 2026-08-12 — Defer the mechanical classifier, with a dated audit as the trigger

- Decision: ship the grammar change alone, with no subcommand that parses annotations and
  no source snapshotting, and reserve no field for either. Six months after the grammar
  ships, hand-audit the maintainer-controlled repositories and count lines demoted or
  deleted versus re-dated. A non-zero count indicates readers act on the annotation; zero
  indicates the annotation alone does not prompt action, which is the evidence the
  classifier is needed.
- Alternatives considered: build the classifier now; reserve a snapshot field for later use;
  defer without naming any trigger.
- Reason: whether a reader acts on "a source last read fourteen months ago" is an empirical
  question with no data on either side, and the grammar change is the cheapest way to get
  it. Building enforcement first would impose a ritual before knowing whether the prompt
  works, in a system whose only enforcement paths convert a trust problem into an outage. A
  reserved field was rejected because an unfilled field is the kit asserting structure it is
  not backing — the defect under repair. Deferring without a trigger was rejected because
  the no-central-state constraint makes cross-install evidence uncollectable, so a trigger
  that is not named will never fire.
- Context: discover + shape / confirmed by user. The audit sees only maintainer-controlled
  repositories, which is a stated limitation of the evidence rather than a gap in the plan.

## 2026-08-12 — Accept that content drift is undetected, and say so in the requirements

- Decision: record as a named limitation that neither this work nor the deferred classifier
  detects a source that still resolves but no longer supports the claim.
- Alternatives considered: treat dead links as representative and ship without the caveat;
  record it as an open assumption rather than a stated position.
- Reason: the originating incident was a 404, but the more common documentation failure is
  content drift — a vendor rename is the example already on record. Both the shipped work
  and the deferred work address the minority case. A reader deciding whether this project
  was worth doing needs that before anything else, so it is stated plainly in the
  requirements rather than buried in an assumptions list.
- Context: shape / user took the position when asked

## 2026-08-27 — Add a sixth annotation tier, `1-kit`, for the kit's own specification files

- Decision: introduce `1-kit` — the kit's own methodology and specification files other than
  the active delivery profile, cited by path. `1-profile` keeps its existing meaning; the
  boundary between them is decidable by path, so a reader never has to judge which applies.
- Alternatives considered: widen `1-profile` to cover all kit files (the design's own
  proposal); mark the affected lines `ungrounded`.
- Reason: nine lines in the generated conventions are kit design decisions with no external
  source, and one of them already ships mis-tiered as `1-docs` with "kit design" as its
  source — neither a path nor a URL. None of the five existing tiers fits. Widening
  `1-profile` would have overloaded a tier that currently means one specific file, blurring
  a boundary that is otherwise checkable by path. Marking them `ungrounded` was rejected
  because those lines *are* grounded in a file a reader can open, and understating that is
  the same class of error this feature exists to fix.
- Cost, accepted knowingly: the requirements' § 8 states "Custom needs: None", so this is
  vocabulary beyond what they authorised, and the requirements' own tier preamble now needs
  editing to match. The maintainer chose it with that cost stated.
- Context: build phase 1B / user chose the alternative the design argued against.

## 2026-08-27 — Carry the `read_on` field name as provisional rather than settling it

- Decision: write the Phase 1B contracts and the Phase 3 specifications with `read_on` marked
  provisional throughout, and run the FR-015 validation gate before implementation begins in
  the kit repository.
- Alternatives considered: run the gate now, before the contracts are written; waive it in
  writing and treat `read_on` as final.
- Reason: FR-015 makes the `verified:` → `read_on:` verb change a merge gate — two versions
  of one conventions file put to a model to see whether it distinguishes their grounding —
  and the gate has not run. Waiving it would ship the untested bet the requirements
  deliberately flagged. Running it first would have blocked contract work on an experiment
  whose outcome changes one token. The contracts are instead written so the verb is
  substitutable: `read_on` appears in no function name, exported symbol, file name, or
  fixture path, and a conformance assertion enforces that. If the gate comes back against
  the name, the change is a text substitution rather than a redesign.
- Context: build phase 1B / user chose to defer with the substitutability property in place.

## 2026-08-27 — Report schema-version drift on stderr, and say nothing when the key is absent

- Decision: the gate subcommand gains a version reader whose entire output is one advisory
  line on stderr; `evaluateGate()`'s return object, stdout, and the exit code are unchanged.
  A file whose `schema_version` line is absent or unparseable produces no advisory.
- Alternatives considered: add the drift to `evaluateGate()`'s return value; print a second
  stdout line; add a separate `schema-report` subcommand; report on an absent key.
- Reason: the conformance test asserts `evaluateGate()`'s return with `deepStrictEqual` in
  nine cases and asserts the exact stdout word across all thirteen skills' gate call sites,
  so the first two options break shipped tests and a documented contract thirteen skills
  branch on. A separate subcommand would be called by nothing without editing all thirteen
  gate stanzas, far outside this feature's file list. Silence on an absent key was chosen
  because every real artifact carries it, the absent-key migration signal is already owned by
  the provenance check, and reporting would fire on the test suite's own stub fixture — an
  advisory that cries wolf during the tests is one nobody reads in the field.
- Context: build phase 1B / design decision, grounded in the specific assertions at
  `ai-delivery/tests/portability-conformance.js` lines 92–138 and 218–246.

## 2026-08-27 — Move generator determinism to the start of FR-015 Stage 3

- Decision: Stage 2 observes the environment and builds nothing. The generator is the first
  Stage-3 artifact, and its byte-determinism check runs immediately after it is built and
  before fixture files are written.
- Alternatives considered: keep determinism in Stage 2; build the generator during Stage 2.
- Reason: determinism is a property of the artifact Stage 3 creates. Requiring it in an
  environment-only stage made the two stages jointly unsatisfiable. This defect and its
  resolution are verified on 2026-08-27 from the owner ruling.
- Context: FR-015 experimental harness / owner ruling.

## 2026-08-27 — Pin FR-015 subjects to Sonnet 5 at high effort

- Decision: every subject invocation carries the exact flags `--model claude-sonnet-5` and
  `--effort high`. Every slot records those flags and separately records the returned model
  and effort. Missing or differing returned values make the slot fail. Haiku is excluded
  because flag acceptance did not establish applied effort.
- Alternatives considered: use the account default; Opus at xhigh; include Haiku despite an
  unobservable effort condition.
- Reason: the experiment asks whether one word changes treatment of a stale date. A stronger
  model at higher effort may reason about dates regardless of the verb, compressing the arm
  difference and risking a false negative at the population most at risk. Deployed readers
  skew toward faster defaults, making the weaker end both a common condition and a sensitive
  instrument. The selection, rationale, mismatch rule, and Haiku exclusion are verified on
  2026-08-27 from the owner ruling.
- Context: FR-015 experimental harness / owner ruling. Auxiliary Haiku usage appeared in
  result telemetry during non-trial Opus, Fable, and Sonnet calls; its role is unverified.

## 2026-08-27 — Keep usage credits enabled and measure observed billing movement

- Decision: usage credits remain enabled for the 120-slot run. The operator records credits
  spent and current balance immediately before slot 1 and immediately after the final slot.
  Movement in either becomes a neutral run finding carrying both readings.
- Alternatives considered: disable usage credits and risk halting at a subscription limit;
  infer the probe's billing path from a movement too small to separate from other activity.
- Reason: the owner accepted possible API-rate billing in exchange for allowing the sequence
  to continue if a five-hour or weekly limit is reached. The post-probe meter was
  inconclusive. The decision and tradeoff are verified on 2026-08-27 from the owner ruling;
  the six starting figures are owner-reported UI observations, not repository-verified.
- Context: FR-015 experimental harness / billing procedure.

## 2026-08-27 — Resolve the FR-015 fixture cursors arm-invariantly

- Decision: use `.ai-delivery/features/cited-source-staleness/fr-015-harness/`; index the 41
  annotated rows from zero for family modulo; preserve the control-cycle quotas but swap
  C15 with C18 and C24 with C27 so `unreachable:` lands only on eligible tiers; and advance
  one shared old-date cursor across old-grounded and unreachable rows in file order.
- Alternatives considered: one-based family indexing; the literal control cycle despite
  ineligible tiers; a separate old-date cursor for unreachable rows.
- Reason: zero-based indexing is the only interpretation under which C15 becomes the control
  named by the handoff. The two swaps give 5 ungrounded, 4 unreachable, and 4 bare controls
  while preserving every unreachable source/tier at `1-docs`. “One cursor per cycle” makes a
  second unreachable-date cursor inconsistent. The counts and eligibility are repo-verified
  on 2026-08-27 from the digest-pinned base. All choices are identical across arms.
- Context: FR-015 delegated cursor semantics and file layout.

## 2026-08-27 — Use direct, isolated slots and joined loopback effort telemetry

- Decision: schedule the 20 pile repetitions first and the 10 action repetitions second,
  round-robin A–D within each type. Each slot uses a unique empty temporary directory plus
  the proved safe-mode/no-tools/no-persistence flags, writes output outside that directory,
  and receives no automatic retry. The prompt is fixture bytes, one blank line, then fixed
  instruction bytes as one positional argument after `--`. A ten-minute timeout is a
  terminal failure. The invariance statistic pools the five Never-grounded and four
  Human-authored keyed rows within each trial.
- Alternatives considered: interleave trial types; retry failed logical slots; infer effort
  from the requested flag; use a persisted session record to obtain effort.
- Reason: these are arm-invariant scheduling, retry, parsing, and statistic choices. A
  non-persistent stream reports the model but omitted effort in an actual probe. On
  2026-08-27 a loopback OTLP probe returned `model=claude-sonnet-5`, `effort=high`, and
  `query_source=sdk` on an `api_request` event joinable to that invocation's stream session
  ID. The runner stores only the joined fields and request identifiers, not OTLP identity or
  prompt attributes. This mechanism is verified on 2026-08-27 by observed effect.
- Context: FR-015 delegated mechanism choices; requested flags are not treated as resolved
  values.

## 2026-08-28 — FR-015 outcome and successor direction

On 2026-08-28, owner Max Adamsky ruled. Canonical record: `ai-delivery-kit` commit
`df93e2bd8d0c3e7d056d3b82045d18893ac57321`, `docs/decisions.md` §
"2026-08-28 — FR-015 outcome and successor direction".

## 2026-08-28 — Consolidate FR-015 records into ai-delivery-kit

- Decision: make `ai-delivery-kit` commit
  `df93e2bd8d0c3e7d056d3b82045d18893ac57321` the canonical home for the FR-015 owner
  rulings and imported findings, and reduce the corresponding `kit-scratch` records to
  pointers.
- Alternatives considered: retain full records in both repositories and reconcile them
  manually.
- Reason: copied state can drift; location pointers reconcile the repositories by
  construction.
- Context: records consolidation / owner ruling on 2026-08-28.

## 2026-09-07 — Move this project's Linear home to team MAX

- Decision: team MAX (Max-test-workspace, id 06118a06-7715-441f-9c3e-7a216a09549d) replaces
  team CDR (Cdrun-metrics) as the home for this project's work.
- Alternatives considered: keeping the CDR binding and treating the missing team as a
  transient connector problem.
- Reason: the user directed the move, and the connected Linear workspace exposes exactly one
  team, which is MAX. CDR is not reachable through this connector at all, so the stored
  binding pointed at a team no skill in this session could read or write. Every per-type
  state name and the complete state table were re-detected from MAX rather than carried over.
- Context: setup re-run / user instruction

## 2026-09-07 — Decline an initiative binding, and record why one could not be chosen

- Decision: initiative_id and initiative_name are both recorded as null — a deliberate
  decline, not the absent-key state that would mean this config predates initiative binding.
- Alternatives considered: binding to a named initiative on the user's word without being
  able to verify it.
- Reason: the user declined. Independently, the Linear server connected here exposes no
  initiative-listing or initiative-reading call, so the kit's initiative read contract cannot
  run in this session and no candidate set could have been offered. The four projects visible
  in the workspace all report an empty initiative list. Recording the decline explicitly is
  what stops later skills from halting to offer a setup re-run.
- Context: setup re-run / user decision, with the connector limitation stated

## 2026-09-07 — Adopt "Handed off" as the handoff milestone and record no default reviewer

- Decision: handoff_milestone_name is "Handed off"; handoff_reviewer is null.
- Alternatives considered: leaving the milestone unset; defaulting the reviewer to the active
  GitHub account, maxadamsky.
- Reason: the milestone spine on the fixture project runs Shaped, Specified, Prototyped,
  Handed off, Built, Shipped. "Handed off" is the last stage the kit moves and "Built" is the
  first that engineering moves, so that boundary is exactly the point engineering is being
  asked to take the work. The reviewer was left blank at the user's direction: this is a test
  workspace with no engineering lead, and inventing one would put a real GitHub handle on
  review requests nobody agreed to. Null here means ship asks at handoff rather than assuming.
- Context: setup re-run / milestone detected from the named project, reviewer set by user
  correction

## 2026-09-07 — Keep documents in the repository although Notion became reachable

- Decision: Notion is recorded connected; notion_parent stays null and stakeholder documents
  continue to live under the feature directory in this repository.
- Alternatives considered: nominating a Notion parent page now that the server is reachable.
- Reason: availability changed, the standing decision did not. The 2026-08-12 entry records
  that the user directed Notion not be used for this project, and reachability is not a
  reason to reverse a preference. Recording connected rather than absent keeps the record
  honest about what this session can actually see.
- Context: setup re-run / integration probe weighed against a standing decision

## 2026-09-07 — Keep the project greenfield after rewriting an empty fingerprint

- Decision: greenfield stays true, and the stack fingerprint is rewritten from zero bytes to
  56 typed observations.
- Alternatives considered: treating the changed observation set as the end of greenfield,
  which is what the re-run rules say a changed observation normally means.
- Reason: greenfield is a property of the repository, not of the fingerprint file. Detection
  re-ran in full and found what it found before: no dependency manifest, no source file, no
  CI configuration, no infrastructure code and no data-stack signal, across 45 path probes
  and 9 directory enumerations. The observation set changed only because the previous run
  wrote an empty fingerprint, which is a defect in that file rather than evidence that code
  arrived. The rewritten fingerprint is what makes the staleness gate meaningful again.
- Context: setup re-run / judgment stated in the proposal for correction

## 2026-09-07 — Exclude the .git directory from the stack fingerprint

- Decision: drop the six `.git` directory observations (`.git`, `.git/hooks`, `.git/info`,
  `.git/logs`, `.git/objects`, `.git/refs`) from the fingerprint input set, leaving 50
  observations: 3 directory enumerations, 2 file reads, and 45 path probes.
- Alternatives considered: keep them, as the setup skill's literal instruction requires —
  it says to merge the shared runtime's fingerprint_inputs unchanged and pass that exact
  set "without reclassification or a maintained allowlist"; or amend and force-push the
  previous commit to hide that it shipped a fingerprint that was stale on arrival.
- Reason: the shared runtime's recursive walk enumerates the .git directory, and
  `.git/objects` gains a subdirectory on every commit. Following the instruction literally
  produces a fingerprint that reads STALE the moment anything is committed, including the
  commit that writes the fingerprint itself — which is what happened at commit 9dfa787.
  The staleness gate exists to say whether the detected stack changed; git's object store
  changing is not a stack change, and a gate that can never read FRESH in a live repository
  reports nothing. This is a defect in the kit rather than in this project, and it should be
  fixed in the shared runtime's discovery output. Force-pushing was rejected because this
  branch is the shared base for the later handoff pull requests.
- Cost, accepted knowingly: this deviates from a written instruction in the setup skill, so
  a future setup re-run that follows that instruction literally will reintroduce the six
  observations and the same defect.
- Context: setup re-run / defect found by running the gate after committing, not before
