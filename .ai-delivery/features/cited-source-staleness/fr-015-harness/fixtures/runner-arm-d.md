---
# Consumer: runner.js
schema_version: 1
generated_on: 2026-08-12
regenerated_on: null
---

# Delivery Conventions

## About This File

How this project actually does things — read from the code first, researched only where the
code is silent. Every convention names its source and date. Edit freely; your edits are
team decisions and survive re-runs. H2 headings are fixed.

This project is greenfield: there is no code to read, so almost every convention below is
grounded in fetched official documentation (tier 1-docs) rather than in this repository.
The first real modules to land here outrank all of it — when the code disagrees with a line
below, the code is the convention and this file gets corrected, not the code.

## Project Structure & Naming

- [C01] Application code lives under a top-level src directory, one package per deliverable;
  tests live in a separate top-level tests directory outside that package. This is the
  layout pytest recommends for new projects because it forces tests to exercise the
  installed package rather than a loose working copy.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · retrieved: 2023-09-14]
- [C02] Test modules mirror the path of the module they exercise, so a reader can find the tests
  for a module without searching.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · retrieved: 2026-08-14]
- [C03] Modules and packages take short, all-lowercase names. Underscores are acceptable in
  module names where they aid readability, and discouraged in package names.
  [source: none · tier: 3-model · ungrounded]
- [C04] The repository exists to verify the ai-delivery kit at version 1.7.0, so anything added
  here is a harness for that purpose unless stated otherwise.
  [source: README.md · tier: 1-code · retrieved: 2024-01-23]

## Code Style

- [C05] Classes use CapWords. Acronyms inside a CapWords name are fully capitalized rather than
  title-cased.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · retrieved: 2026-08-18]
- [C06] Functions, methods, variables, and arguments use lowercase words separated by
  underscores. Module-level constants use all capitals with underscores.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · unreachable: 2024-04-08]
- [C07] A single leading underscore marks a non-public method or attribute. Double leading
  underscores are reserved for the case where subclass name mangling is genuinely wanted,
  not used as a general privacy marker.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · retrieved: 2023-11-30]
- [C08] Imports are grouped in three blocks separated by blank lines: standard library, then
  third-party, then local application imports. Ruff enforces the mechanics; the convention
  is stated here because the grouping is what a reader relies on.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · retrieved: 2026-08-21]
- [C09] Departing from PEP 8 is allowed for the four reasons PEP 8 itself gives — the guideline
  would hurt readability here, surrounding code already departs, the code predates the
  guideline, or an older Python version requires it. A departure for any other reason is a
  review finding.
- [C10] Formatting and line length are settled by the format gate in gates.md, not by review.
  [source: .ai-delivery/gates.md · tier: 1-code · retrieved: 2023-09-14]

## Error Handling & Logging

- [C11] Exception classes end in the word Error.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · retrieved: 2026-08-25]
- [C12] Invalid input raises rather than returning a sentinel or a partial result, and the
  application continues safely after rejecting the malformed data.
  [source: none · tier: 3-model · ungrounded]
- [C13] Validation failures are logged and monitored, because a run of them is an attack signal
  rather than a user mistake.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · retrieved: 2024-01-23]
- [C14] Log records never carry secrets, credentials, or tokens.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · retrieved: 2026-08-14]
- [C15] Error messages crossing a module boundary name the failing condition or input, not only
  the operation that failed, so the caller can act on them. This is model guidance with no
  external grounding and is advisory until the first real error path here settles it.

## Testing Conventions

- [C16] pytest is the test framework. Test files match the test underscore prefix or suffix
  patterns pytest discovers, test functions begin with test, and test classes begin with
  Test and define no constructor. A file that misses these patterns is silently not
  collected, so this is a correctness rule rather than a style one.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · retrieved: 2024-04-08]
- [C17] The importlib import mode is preferred so tests do not mutate the interpreter path and
  test module names need not be globally unique.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · retrieved: 2026-08-18]
- [C18] Shared fixtures live in a conftest module at the narrowest scope that serves them.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · unreachable: 2023-11-30]
- [C19] pytest configuration lives in pyproject.toml alongside package metadata, in strict mode.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · retrieved: 2023-09-14]
- [C20] Tests are written before the implementation they cover, and the suite that runs at
  verification is the same suite those tests joined.
  [source: ai-delivery/skills/setup/profiles/software.md § Test-first meaning · tier: 1-profile · retrieved: 2026-08-21]
- [C21] External dependencies are mocked at the boundary; real objects are preferred wherever
  practical, and integration tests isolate shared state per test.
  [source: none · tier: 3-model · ungrounded]

## Interface & API Conventions

- [C22] A contract consumed across a unit boundary is defined as an interface or protocol rather
  than a concrete class, so an implementation can be replaced without touching consumers.
  [source: ai-delivery/skills/setup/profiles/software.md § Spec contents · tier: 1-profile · retrieved: 2024-01-23]
- [C23] Every component must be testable with mock dependencies alone — needing a live database,
  network, filesystem, or a particular environment to test is a design defect, not a
  testing inconvenience.
  [source: ai-delivery/skills/setup/profiles/software.md § Spec contents · tier: 1-profile · retrieved: 2026-08-25]
- [C24] Public function signatures carry type annotations, because the type-check gate has
  nothing to check without them.

## Data Conventions

Not applicable — software profile, no data-pipeline surface detected.

## Security Conventions

- [C25] Untrusted input is validated on arrival, server-side, before any processing, and as early
  in the flow as the value can be reached.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · retrieved: 2024-04-08]
- [C26] Validation is allowlist-based: state what is permitted rather than what is forbidden. A
  denylist is supplementary only and is never the primary defense.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · retrieved: 2026-08-14]
- [C27] Strings carry explicit minimum and maximum lengths; numbers carry explicit ranges; file
  uploads carry an enforced maximum size.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · unreachable: 2023-11-30]
- [C28] Regular expressions applied to untrusted input anchor the whole value and are built to
  avoid catastrophic backtracking.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · retrieved: 2023-09-14]
- [C29] Uploaded files are stored under server-generated random names; a client-supplied path or
  filename is never trusted.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · retrieved: 2026-08-18]
- [C30] Secrets never appear in source, configuration files, container images, logs, or version
  control history. They reach the process by runtime injection or a secrets manager.
  [source: none · tier: 3-model · ungrounded]
- [C31] Secret detection runs both before commit and in the pipeline. The secret-detection gate
  in gates.md is the pipeline half; a pre-commit hook is the developer half and is not yet
  installed here.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · retrieved: 2024-01-23]
- [C32] Access to secrets follows least privilege, and a compromised secret is revoked
  immediately rather than rotated on the normal schedule.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · retrieved: 2026-08-21]
- [C33] The kit's own source catalog points at an OWASP Python cheat sheet that now returns 404.
  Python-specific security guidance here is therefore grounded in the OWASP input
  validation and secrets management cheat sheets instead. Correcting the catalog entry is
  an ai-delivery kit change, not a change to this repository.
  [source: https://cheatsheetseries.owasp.org/ · tier: 1-docs · unreachable: 2024-04-08]

## Documentation Conventions

- [C34] Public functions, classes, and modules carry docstrings stating what the surface does,
  what it takes, and what it raises.
  [source: ai-delivery/skills/setup/profiles/software.md § Verification method · tier: 1-profile · retrieved: 2023-11-30]
- [C35] Engineering decisions are recorded in docs/decisions.md at the point the decision is
  made — what was chosen, what else was considered, and why. Not a transcript.
  [source: .ai-delivery/config.md § Preferences · tier: 1-code · retrieved: 2026-08-25]
- [C36] Stakeholder documents live in this repository, under the feature directory, because
  Notion is not connected for this project.

## Linear Conventions

- [C37] Hierarchy: a Linear project is one feature; milestones are its delivery stages (MVP
  first); issues are units of work with plain-language titles and acceptance criteria as
  prose in the description; sub-issues are implementation units when finer decomposition
  is needed — always created with the project set explicitly (sub-issues do not inherit
  the parent's project, and project-scoped listing misses unprojected ones). Exactly one
  build-created integration issue per project (label integration, final milestone).
  [source: kit design · tier: 1-docs · retrieved: 2023-09-14]
- [C38] Work for this project lives in team CDR (Cdrun-metrics).
  [source: .ai-delivery/config.md § Linear · tier: 1-code · retrieved: 2026-08-14]
- Priority is Linear's native field (Urgent/High/Medium/Low/None). Out-of-scope items are
  never created as issues — they belong in the requirements document.
- [C39] Statuses: address states by the names recorded in config.md ## Linear; branch on state
  type, never on name. For this team those names are Backlog, Todo, In Progress, Done,
  Canceled, and Duplicate. New issues are created in Backlog or Todo. This team has no
  second in-progress state, so there is no separate review state to move through.
  [source: none · tier: 3-model · ungrounded]
- Titles: short imperative phrases naming the outcome, no story grammar, no ticket-style
  prefixes.
- Labels: search before creating; creating a label requires user approval. Issue label
  writes REPLACE the full set — always read the issue's current labels and write back the
  merged list. This read-modify-write rule is a convention, not an enforced hook: a hook
  must be decidable from the tool call's arguments plus files on disk, and the current
  label set exists only in Linear, so there is nothing on disk to diff against.
- [C40] Kit-reserved labels are defined by the skills, not by this file, and are never renamed
  here. Three already exist on this team — awaiting-verification, verified, and
  integration. Two do not — escalated and rework — so the first skill that needs one will
  ask before creating it.
  [source: Linear list_issue_labels for team CDR · tier: 1-code · retrieved: 2024-01-23]
- [C41] This team's own taxonomy is Feature, Bug, and Improvement. Reuse these rather than
  introducing parallel names for the same distinction.
  [source: Linear list_issue_labels for team CDR · tier: 1-code · retrieved: 2026-08-18]
- Search before create, always: list existing projects and issues before creating; after
  every successful create, record the returned identifier in the feature's tracker.md
  immediately — resume matches by identifier, never by title.
- Search-before-create, the transactional-gate rule, and rework-time state transitions are
  likewise conventions, not hooks, for the same platform reason: each requires a
  Linear-side read that no check decidable from the tool call's arguments plus files on
  disk can perform.
- Required on every kit-created issue: description with acceptance criteria, priority,
  milestone (when milestones exist), and the project.
- Linear Documents are not used — the repo owns specs, design docs, and (because Notion is
  absent here) stakeholder documents too. Attach links, not documents.
- Descriptions are annotated, never rewritten: use anchored patch edits; never anchor a
  patch across an issue identifier, because Linear rewrites identifiers into mention markup
  on save.
