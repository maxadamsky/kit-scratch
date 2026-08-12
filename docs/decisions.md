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
