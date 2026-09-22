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

## 2026-09-09 — Keep the decision record out of the stack fingerprint's read journal

- Decision: the fingerprint's read journal carries README.md and .gitignore only.
  docs/decisions.md is excluded although setup read it during detection.
- Alternatives considered: journalling it too, on the grounds that it is this project's
  own documentation and setup genuinely read it during the detection pass.
- Reason: the kit's own skills append entries to docs/decisions.md, so its hash moves
  whenever a skill records a decision. Fingerprinting it would make the staleness gate
  fire on work that changed no stack fact — the same shape as the .git enumeration defect
  recorded on 2026-09-07. A file the kit writes is not a stack input even when setup read
  it, which is the rule that already keeps setup's other outputs out of the fingerprint.
  The cost accepted is that a rewrite of the standing decisions will not itself make the
  gate stale.
- Context: setup re-run / user correction to setup's proposal

## 2026-09-12 — Keep three README units that share one file, built one after another

- Decision: decompose repository usage documentation into three Linear issues: MAX-16
  (the README purpose statement), MAX-17 (the evidence branch table) and MAX-18 (the kit
  version line). MAX-17 and MAX-18 are each blocked by MAX-16, and because all three edit
  README.md they are built one after another rather than in parallel.
- Alternatives considered: merging the three units into one issue covering all three
  functional requirements, which would honour the software profile's rule that units touch
  separate files.
- Reason: each unit gives a reader something new on its own (what the repository is for,
  which branches are evidence, which kit version it reflects), which is the profile's test
  for a unit at requirements time. The approved scope limits the work to the single
  README, so the shared file cannot be restructured away; build serializes the two later
  units instead.
- Cost, accepted knowingly: there is no parallel batch after the foundation, so build runs
  the three units in sequence.
- Context: shape decomposition / approved by Max as proposed

## 2026-09-13 — Export notebook text outputs first, then images and notes for undisplayable outputs

- Decision: decompose notebook export into three Linear issues in the Notebook export
  project: MAX-19 (export a notebook and its text outputs to one shareable file, Urgent),
  MAX-20 (include image and chart outputs, High) and MAX-21 (show a note where an output
  cannot be displayed, Medium). MAX-20 and MAX-21 are each blocked by MAX-19 and can be
  built in parallel once it is done.
- Alternatives considered: one issue covering all five functional requirements, or folding
  image and chart outputs into the first unit.
- Reason: text outputs alone already let an author hand a colleague a readable file, so the
  first unit delivers value soonest; images and the note for undisplayable outputs each add
  a new capability on top of that export, so neither can start before it.
- Cost, accepted knowingly: the software profile asks for units that touch separate files
  with no dependencies between them. MAX-20 and MAX-21 depend on MAX-19, and if build finds
  that both edit the same output-writing files it will run them one after another.
- Context: shape decomposition / approved by Max as proposed

## 2026-09-13 — Keep the Notebook export project's own milestones, with four delivery stages absent

- Decision: the Notebook export project keeps its existing milestones, Shaped, Editorial
  review and Specified, untouched. Its Shaped and Specified milestones stand for the kit's
  Shaped and Specified stages; Prototyped, Handed off, Built and Shipped have no milestone in
  this project, and Editorial review stands for no stage. The mapping is recorded under
  milestone_names, the per-project milestone mapping in .ai-delivery/config.md.
- Alternatives considered: creating the four missing stages after the existing milestones,
  or reusing Shaped and Specified by exact name while adding the missing names and leaving
  Editorial review unused.
- Reason: Max chose to keep the project's milestone set as it is and create nothing.
- Cost, accepted knowingly: issues in this project cannot be moved to a Prototyped, Handed
  off, Built or Shipped milestone, and at handoff the kit finds no Handed off milestone here
  and must use its choice for a missing milestone.
- Context: shape decomposition / milestone set chosen and approved by Max

## 2026-09-13 — Build folder summary as three independent units, with no blocked-by links

- Decision: decompose folder summary into three Linear issues in the Folder summary
  project, each at the Shaped milestone and with no blocked-by links: MAX-22 (show a
  folder's file count and total size, Urgent), MAX-23 (break a folder's files down by file
  type, Urgent) and MAX-24 (say plainly when a folder cannot be summarized, Medium). MAX-22
  owns reading the folder and offers its file list through an agreed interface; MAX-23 and
  MAX-24 work against that interface with stand-ins in their tests, and build connects them.
- Alternatives considered: making MAX-23 and MAX-24 blocked by MAX-22, because the type
  breakdown and the path message only reach a person through MAX-22's summary; or folding
  the path message into MAX-22's acceptance criteria.
- Reason: the software profile asks for units that can be built independently, with
  interfaces agreed up front and dependencies removed by restructuring rather than recorded
  as links. The plain path message was not raised at intake; it was added because the
  goals require correct figures, and a failed read must not produce figures.
- Cost, accepted knowingly: a person sees the type breakdown and the path message only
  after build connects them to MAX-22's summary, and five of the six requirements are
  Urgent, above the kit's guideline that no more than 60% be Urgent or High.
- Context: shape decomposition / approved by Max as proposed

## 2026-09-13 — Add the four missing delivery stages to the Folder summary project's milestones

- Decision: the Folder summary project keeps its existing milestones, Shaped, Editorial
  review and Specified, unchanged, and gains four new milestones after them, in this order:
  Prototyped, Handed off, Built and Shipped, each described with the stage it marks and who
  moves issues into it. Shaped and Specified stand for the kit's Shaped and Specified
  stages; Editorial review stands for no stage and stays unused. The mapping is recorded
  under milestone_names, the per-project milestone mapping in .ai-delivery/config.md.
- Alternatives considered: keeping the existing three and creating nothing, which leaves
  four stages without a milestone; or replacing with the kit's stage names by exact match,
  which reaches the same seven milestones without Max mapping the existing names himself.
- Reason: Max chose to adopt the delta — map the existing names himself and create only the
  stages the project lacked.
- Cost, accepted knowingly: the project carries an Editorial review milestone, between
  Shaped and Specified, that no kit stage uses.
- Context: shape decomposition / milestone set chosen and approved by Max

## 2026-09-13 — Build text preview as two independent units, with no blocked-by links

- Decision: decompose text preview into two Linear issues in the Text preview project,
  each Urgent, at the Shaped milestone and with no blocked-by links: MAX-25 (preview the
  opening lines of a text file, covering FR-001 to FR-003) and MAX-26 (say plainly when a
  file is empty or not text, covering FR-004 and FR-005). FR means functional requirement
  in .ai-delivery/features/text-preview/requirements.md. MAX-25 reads and shows a file's
  lines; MAX-26 decides whether a file is empty or not text and words the note. Each agrees
  its interface up front and uses a stand-in for the other in its tests, and build
  connects them.
- Alternatives considered: splitting the empty-file note and the not-text note into
  separate issues, which would reach the software profile's typical range of three to nine
  units; or folding both notes into MAX-25's acceptance criteria.
- Reason: each issue gives a person something new on its own. The empty-file check has a
  single trivial acceptance criterion, so it stays with the not-text note rather than
  standing alone.
- Cost, accepted knowingly: two units is below the profile's typical range, and all five
  requirements and both units are Urgent, above the kit's guideline that no more than 60%
  be Urgent or High; Max approved the priorities as drafted because intake named every item
  a must-include. Four decisions stay open for the maintainer to settle before build: how
  many lines a preview shows, how a file is judged to be text, how a preview is requested
  and shown, and what a person sees when a file cannot be read.
- Context: shape decomposition / approved by Max as proposed

## 2026-09-13 — Use the kit's stage names for the Text preview project's milestones, leaving Editorial review unused

- Decision: the Text preview project reuses its existing Shaped and Specified milestones,
  by exact name, for the kit's Shaped and Specified stages, and gains four new milestones
  after them, in this order: Prototyped, Handed off, Built and Shipped, each described with
  the stage it marks and who moves issues into it. Editorial review stays untouched and
  stands for no stage. The mapping is recorded under milestone_names, the per-project
  milestone mapping in .ai-delivery/config.md.
- Alternatives considered: keeping the existing three and creating nothing, which leaves
  four stages without a milestone; or adopting the delta, with Max mapping the existing
  names before only the missing stages are created.
- Reason: Max chose to replace — use the kit's stage names without mapping, reuse exact
  matches, and create the missing names.
- Cost, accepted knowingly: the project carries an Editorial review milestone, between
  Shaped and Specified, that no kit stage uses. Two stored milestone descriptions differ
  from the text Max approved: Handed off adds the clause "asking engineering to take the
  work", and Prototyped words the same meaning as a fuller sentence. Max chose to continue
  with both as created; restoring the approved wording is an edit in Linear that Max owns.
- Context: shape decomposition / milestone set chosen and approved by Max

## 2026-09-15 — Shape the reading list export from one group of four requests, keeping dates and links in a single delivery unit

- Decision: MAX-27 and MAX-28, which ask for the same Markdown export in different words,
  and two requests brought into the sitting by hand — saved dates, and a link back to each
  article — were shaped as one feature with three delivery issues: MAX-31 for the export
  itself, MAX-32 for the saved date and link on each entry, and MAX-33 for the plain
  message when there is nothing to export. The two brought-in requests became request
  issues MAX-34 and MAX-35, which record the original requests and are not units of work.
- Alternatives considered: splitting the saved date and the article link into two delivery
  issues, one per brought-in request; or shaping MAX-27 and MAX-28 as separate features.
- Reason: the saved date and the link both change what a single entry shows, so splitting
  them would have put two units in the same file, which the software profile's strict
  independence rule rejects. MAX-27 and MAX-28 describe one capability.
- Cost, accepted knowingly: two of the three delivery issues are Urgent or High, which is
  67 percent and above the kit's 60 percent guideline. Max was shown that ratio at the
  decomposition review and approved the priorities unchanged. Five questions the intake
  could not answer stay open in the requirements document, all owned by Max: whether the
  export covers the week or the whole list, what else an entry shows, what starts the
  export and where the file goes, entry ordering, and the success measure.
- Context: triage grouping approved by Max, then shape decomposition approved by Max

## 2026-09-15 — Create the full kit milestone spine on the new Reading list export project

- Decision: the Reading list export project, which had no milestones, gained all six kit
  stages in order: Shaped, Specified, Prototyped, Handed off, Built and Shipped. Each
  carries a description naming the stage it marks and who moves issues into it — the kit
  for the first four, engineering by hand for Built and Shipped. The mapping is recorded
  under milestone_names, the per-project milestone mapping in .ai-delivery/config.md.
- Alternatives considered: keeping the project without milestones, which would leave every
  stage absent and every issue without one; or replacing, which on an empty project has
  the same result as adopting the delta.
- Reason: Max chose to adopt the delta on an empty project, so every role was unmapped and
  all six names were created.
- Cost, accepted knowingly: none identified. No existing milestone was renamed, reordered
  or deleted, because the project had none.
- Context: shape decomposition / milestone set chosen and approved by Max

## 2026-09-17 — End greenfield now that a real manifest exists, and keep the gates adopted

- Decision: greenfield flips from true to false, package_manifests records pyproject.toml,
  and the toolchain the manifest declares — pytest, pytest-cov, ruff, mypy, bandit,
  pip-audit, with uv as the package manager from uv.lock — is now manifest-grounded rather
  than chosen. Every gate command keeps its existing uv invocation and its `adopted` status;
  only each command's source line changes, from "no repo config found — greenfield" to the
  manifest that declares the tool. rubrics.md, the thresholds, and every answered preference
  including the null default reviewer are left exactly as they stand.
- Alternatives considered: marking the gates `detected` now that the tools are declared in
  the repository; regenerating rubrics.md from the current catalog at the same time.
- Reason: a manifest naming a tool is not the project defining how it runs. pyproject.toml
  declares the dev group and nothing else — no [tool.ruff], [tool.mypy],
  [tool.pytest.ini_options] or [tool.coverage] section, no scripts, no Makefile, no CI — so
  the commands in gates.md are still setup's invocation, which is what `adopted` means. This
  supersedes the 2026-09-07 entry that kept greenfield true: the reason given there was that
  the repository held no dependency manifest, and it now holds one. Rubrics were left alone
  because the profile is unchanged and existing artifacts are standing decisions.
- Cost, accepted knowingly: the coverage and lint commands point at src/ and tests/, which do
  not exist yet, so the first verify run in this repository will be the first time any of
  these commands is proved.
- Context: setup re-run / proposal confirmed by Max as proposed

## 2026-09-21 — Retire the per-project milestone map and the handoff milestone for the five fixed stages

- Decision: milestone_names, the per-project map from each kit stage to that project's
  milestone name, and handoff_milestone_name ("Handed off") are removed from
  .ai-delivery/config.md. The Linear lines in .ai-delivery/conventions.md that described
  the six-stage model now carry the kit's current text. The null default handoff reviewer
  recorded on 2026-09-07 stands.
- Alternatives considered: keeping both keys, which kit 3.0.0 accepts but ignores; moving
  the existing projects' milestones to the stage names as part of setup.
- Reason: kit 3.0.0 gives every project the same five stage milestones — Discovery,
  Prototype, Build, Validate and Release — so there is no per-project name to map and no
  handoff milestone to resolve. Keys that nothing reads would only mislead a person reading
  the config, and setup never writes Linear projects or milestones. This supersedes the
  2026-09-07 entry that adopted "Handed off" as the handoff milestone, and it retires the
  milestone_names mappings that earlier entries recorded for five projects; the milestones
  themselves remain in Linear.
- Cost, accepted knowingly: no project on team MAX carries a stage milestone yet. Seven
  still carry the earlier six-stage names, so a skill looking up a stage milestone in any
  of them by exact name finds nothing. Whether and when to move them is Max's decision.
- Context: setup re-run after the kit update to 3.0.0 / proposal confirmed by Max

## 2026-09-21 — Record all eleven project statuses by the kit's names, on Max's word

- Decision: the eleven project_status_* keys in .ai-delivery/config.md record Idea,
  Proposal, Discovery, Ready, Paused, Prototype, Build, Validate, Release, Completed and
  Canceled, exactly as the kit names them.
- Alternatives considered: recording only Completed and Canceled, the two of the eleven that
  Linear provides by default, and leaving the nine custom statuses null until one could be
  seen; asking for each name separately.
- Reason: Max confirmed that a workspace administrator created all nine custom statuses
  with exactly these names. No Linear call lists a workspace's project statuses, so this
  session could not confirm it: the eleven projects on team MAX currently hold only
  Backlog, Planned and Canceled.
- Cost, accepted knowingly: if a recorded name does not match the workspace, the first
  write that sets it is refused after its project already exists, where a null would have
  stopped the skill before any write.
- Context: setup re-run / interview answer from Max

## 2026-09-22 — Build the pull request checklist as two independent units, with no blocked-by links

- Decision: decompose the pull request checklist into two Linear issues in project P-MAX-12,
  Pull request checklist. Both sit in the Prototype milestone, with no blocked-by links
  between them:
  - MAX-45 (Urgent) publishes the five-item checklist in CONTRIBUTING.md, covering FR-001
    to FR-006.
  - MAX-46 (High) links the checklist from the README, covering FR-007.

  FR means functional requirement in
  .ai-delivery/features/pull-request-checklist/requirements.md. MAX-46's link target is
  fixed as CONTRIBUTING.md at the repository root. Both can therefore be built at once, and
  the link resolves once both land.
- Alternatives considered: one issue covering both the file and the README sentence, or
  one issue per checklist item.
- Reason: the README sentence carries two things open question 4 has not settled: the
  setup-record refresh, and its ordering against the MAX-16 README rewrite. Keeping it
  apart lets the checklist file go ahead while that question is open. Splitting the five
  items apart would put several issues in one file, which the software profile forbids.
- Cost, accepted knowingly: two units is below the software profile's typical range of
  three to nine. All seven requirements and both units are Urgent or High, above the kit's
  guideline that no more than 60% be. Max approved the priorities as drafted, because
  discovery had already cut everything that could wait. Ten decisions stay open for
  Max Adamsky, listed in the requirements document. Questions 1, 2 and 5 must be settled
  before the checklist is written, and question 4 before the README sentence.
- Context: shape decomposition / approved by Max as proposed

## 2026-09-22 — Settle how the pull request checklist treats tool defaults, commits and the linked issue

- Decision: three of the checklist's open questions are settled. The questions are
  numbered as in `.ai-delivery/features/pull-request-checklist/requirements.md`.
  - Question 1: a pull request made exactly as the kit's ship skill makes it misses
    items 1, 4 and 5. Ship is the kit's commit-and-pull-request workflow. For anyone
    without Linear it suggests a `feat/…` branch, writes a multi-section description and
    links Linear instead of a GitHub issue. The checklist's one introductory sentence
    says the five items apply whichever tool opens the pull request, without naming the
    kit.
  - Question 2: "one commit per change" means one commit per logical change, so a pull
    request may hold several commits.
  - Question 5: the contributor files a GitHub issue, or picks an existing one, before
    starting work. Max triages GitHub issues and adds any Linear link at review.
- Alternatives considered: for question 1, a sentence naming ship and saying how to
  override it, or saying nothing about tools. For question 2, one squashed commit per pull
  request. For question 5, letting the issue be filed at any point before the pull
  request opens.
- Reason: naming ship would move the requirements' line that the guide says nothing
  about how the kit works, and would tie the guide to ship's current behaviour. Saying
  nothing would let the success count measure the conflict between ship and the guide
  instead of the guide. A tool-neutral introductory sentence answers the conflict inside
  the one sentence the requirements already allow. One commit per logical change matches
  how ship commits one unit at a time. Filing the issue before the work keeps item 5's
  purpose, which is to record the intent before the branch exists.
- Context: prototype design discovery / answered by Max

## 2026-09-22 — Append the README sentence on this branch and refresh the setup record by a setup re-run

- Decision: the README sentence, tracked as Linear issue MAX-46, is appended to README.md
  as it stands on the live-proof-2026-09-21 branch. That README already holds the
  purpose-statement rewrite built for MAX-16 (commit 890dea8). At integration, prototype
  re-runs setup in the same session, so the kit's setup check reads FRESH again in the
  same change. This settles the checklist requirements' open question 4.
- Alternatives considered: leaving the setup check STALE for Max to refresh by hand;
  holding MAX-46 until the route to main is settled.
- Reason: the setup record, `.ai-delivery/stack-fingerprint`, stores a hash of
  README.md, so any README edit makes every kit skill's setup check read STALE and stop
  until setup re-runs. The kit's write guard refuses a subagent's write to that record,
  so the refresh belongs to the main session, and a setup re-run is the kit's own way to
  make it. Running it at integration confines the STALE window to this one session.
- Cost, accepted knowingly: a setup re-run after a README change runs full detection and
  may also update conventions.md and this file, so the change carries more than one
  sentence and a refreshed record. Discovery decided the sentence reaches main ahead of
  the MAX-16 rewrite. Whether that holds is now settled at handoff, under open question
  3, which Max owns and must settle before 2026-10-05.
- Context: prototype design discovery / answered by Max

## 2026-09-22 — Keep the pull request checklist's acceptance checks out of pytest's default run

- Decision: the feature's acceptance checks are pytest modules in
  `.ai-delivery/features/pull-request-checklist/checks/`, run only by naming that
  directory. A plain `uv run pytest` from the repository root still collects nothing and
  exits with code 5.
- Alternatives considered: checks in a top-level `tests/` directory, where the
  conventions put tests; no checks, with verification done by reading the two files.
- Reason: checklist item 3 tells contributors that "no tests ran" (exit code 5) is the
  expected result until the first test module lands, and requirement FR-004 checks
  exactly that. A module under `tests/` would make item 3 false on the day it landed and
  start the rewrite that the requirements' open question 8 asks about. pytest skips
  directories whose names begin with a dot. On 2026-09-22, with pytest 9.1.1, a plain run
  exited with code 5 and a run naming the directory collected the checks. Reading alone
  would lose a repeatable proof written before the files it checks. The checks verify
  this feature's two files. They are not enforcement on contributors' pull requests,
  which the requirements exclude.
- Cost, accepted knowingly: the checks sit outside the recorded lint and type-check
  gates, which name `src/` and `tests/` only, so ruff and mypy are run on the checks
  directory by name. The checks also depart from the conventions' tests-directory layout,
  for the reason above. They depart as well from the project rubric's blocking item that
  anything added be reachable from the test command in `.ai-delivery/gates.md`. FR-004
  outranks that item under config's `nfr_precedence`, which puts requirements first.
- Context: prototype design discovery / proposed by the orchestrator, for Max's approval
  with the implementation plan

## 2026-09-22 — Mark the Test gate detected, and read CONTRIBUTING.md as a convention source

- Decision: the Test gate in `.ai-delivery/gates.md` keeps its command, `uv run pytest`,
  and moves from `adopted` to `detected`. Its source is now item 3 of CONTRIBUTING.md,
  which names that command as the one every contributor runs before opening a pull
  request. The other gates stay `adopted`. Setup also reads CONTRIBUTING.md as a tier
  1-code source: its five rules join `.ai-delivery/conventions.md`, and the file joins
  the setup record's read journal, `.ai-delivery/stack-fingerprint`.
- Alternatives considered: keeping every gate `adopted`, as the 2026-09-17 entry decided;
  leaving CONTRIBUTING.md unread by setup.
- Reason: the 2026-09-17 entry kept the gates `adopted` because a manifest naming a tool
  is not the project defining how it runs. CONTRIBUTING.md now defines exactly that for
  the tests, so for this one gate the reason no longer holds. It still holds for lint,
  format, type check, coverage and the scans, which nothing in the repository invokes.
  Setup reads contributing guides as written conventions, so leaving the file unread
  would leave the conventions record behind the repository.
- Cost, accepted knowingly: any later edit to CONTRIBUTING.md, including the rewrite of
  item 3 that the pull request checklist's open question 8 anticipates, makes the setup
  check read STALE until setup re-runs, as README edits already do.
- Context: setup re-run invoked from the pull request checklist's integration (MAX-47) /
  proposal confirmed by Max as proposed
