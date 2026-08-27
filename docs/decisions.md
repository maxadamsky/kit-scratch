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
