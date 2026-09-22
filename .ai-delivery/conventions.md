---
schema_version: 1
generated_on: 2026-08-12
regenerated_on: 2026-09-21
---

# Delivery Conventions

## About This File

How this project actually does things — read from the code first, researched only where the
code is silent. Every convention names its source and date. Edit freely; your edits are
team decisions and survive re-runs. H2 headings are fixed.

This project is no longer greenfield: pyproject.toml and uv.lock now declare the toolchain,
and the 2026-09-17 re-run read them. There are still no source or test modules, so almost
every convention below remains grounded in fetched official documentation (tier 1-docs)
rather than in this repository. The first real modules to land here outrank all of it — when
the code disagrees with a line below, the code is the convention and this file gets
corrected, not the code.

A date after `verified:` is the day that source was last read. The 2026-09-07 and 2026-09-17
re-runs re-read this repository's own files and the Linear team; neither re-fetched the
external documentation, so those lines keep their original dates rather than borrowing
today's.

## Project Structure & Naming

- Application code lives under a top-level src directory, one package per deliverable;
  tests live in a separate top-level tests directory outside that package. This is the
  layout pytest recommends for new projects because it forces tests to exercise the
  installed package rather than a loose working copy.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- Test modules mirror the path of the module they exercise, so a reader can find the tests
  for a module without searching.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- Modules and packages take short, all-lowercase names. Underscores are acceptable in
  module names where they aid readability, and discouraged in package names.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- The repository is a fixture for exercising the ai-delivery kit, not a product. Its files,
  branches and pull requests exist so the kit can be run against a real repository, and
  they are kept as a worked example of what the kit produces, so anything added here serves
  that purpose unless stated otherwise.
  [source: README.md · tier: 1-code · verified: 2026-09-15]

## Code Style

- Classes use CapWords. Acronyms inside a CapWords name are fully capitalized rather than
  title-cased.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- Functions, methods, variables, and arguments use lowercase words separated by
  underscores. Module-level constants use all capitals with underscores.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- A single leading underscore marks a non-public method or attribute. Double leading
  underscores are reserved for the case where subclass name mangling is genuinely wanted,
  not used as a general privacy marker.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- Imports are grouped in three blocks separated by blank lines: standard library, then
  third-party, then local application imports. Ruff enforces the mechanics; the convention
  is stated here because the grouping is what a reader relies on.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- Departing from PEP 8 is allowed for the four reasons PEP 8 itself gives — the guideline
  would hurt readability here, surrounding code already departs, the code predates the
  guideline, or an older Python version requires it. A departure for any other reason is a
  review finding.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- Formatting and line length are settled by the format gate in gates.md, not by review.
  [source: .ai-delivery/gates.md · tier: 1-code · verified: 2026-09-07]

## Error Handling & Logging

- Exception classes end in the word Error.
  [source: https://peps.python.org/pep-0008/ · tier: 1-docs · verified: 2026-08-12]
- Invalid input raises rather than returning a sentinel or a partial result, and the
  application continues safely after rejecting the malformed data.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Validation failures are logged and monitored, because a run of them is an attack signal
  rather than a user mistake.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Log records never carry secrets, credentials, or tokens.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Error messages crossing a module boundary name the failing condition or input, not only
  the operation that failed, so the caller can act on them. This is model guidance with no
  external grounding and is advisory until the first real error path here settles it.
  [source: model knowledge · tier: 3-model · verified: 2026-08-12]

## Testing Conventions

- pytest is the test framework. Test files match the test underscore prefix or suffix
  patterns pytest discovers, test functions begin with test, and test classes begin with
  Test and define no constructor. A file that misses these patterns is silently not
  collected, so this is a correctness rule rather than a style one.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- The importlib import mode is preferred so tests do not mutate the interpreter path and
  test module names need not be globally unique.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- Shared fixtures live in a conftest module at the narrowest scope that serves them.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- pytest configuration lives in pyproject.toml alongside package metadata, in strict mode.
  [source: https://docs.pytest.org/en/stable/explanation/goodpractices.html · tier: 1-docs · verified: 2026-08-12]
- The toolchain is declared in pyproject.toml's dev group — pytest, pytest-cov, ruff, mypy,
  bandit and pip-audit — and pinned by uv.lock, but no tool section configures any of them
  yet. Until a pytest configuration section exists, the commands in gates.md are the only
  invocation this project has, and strict mode above is the target rather than the state.
  [source: pyproject.toml · tier: 1-code · verified: 2026-09-17]
- Tests are written before the implementation they cover, and the suite that runs at
  verification is the same suite those tests joined.
  [source: ai-delivery/skills/setup/profiles/software.md § Test-first meaning · tier: 1-profile · verified: 2026-08-12]
- External dependencies are mocked at the boundary; real objects are preferred wherever
  practical, and integration tests isolate shared state per test.
  [source: ai-delivery/skills/setup/profiles/software.md § Test-first meaning · tier: 1-profile · verified: 2026-08-12]

## Interface & API Conventions

- A contract consumed across a unit boundary is defined as an interface or protocol rather
  than a concrete class, so an implementation can be replaced without touching consumers.
  [source: ai-delivery/skills/setup/profiles/software.md § Spec contents · tier: 1-profile · verified: 2026-08-12]
- Every component must be testable with mock dependencies alone — needing a live database,
  network, filesystem, or a particular environment to test is a design defect, not a
  testing inconvenience.
  [source: ai-delivery/skills/setup/profiles/software.md § Spec contents · tier: 1-profile · verified: 2026-08-12]
- Public function signatures carry type annotations, because the type-check gate has
  nothing to check without them.
  [source: .ai-delivery/gates.md · tier: 1-code · verified: 2026-09-07]

## Data Conventions

Not applicable — software profile, no data-pipeline surface detected.

## Security Conventions

- Untrusted input is validated on arrival, server-side, before any processing, and as early
  in the flow as the value can be reached.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Validation is allowlist-based: state what is permitted rather than what is forbidden. A
  denylist is supplementary only and is never the primary defense.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Strings carry explicit minimum and maximum lengths; numbers carry explicit ranges; file
  uploads carry an enforced maximum size.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Regular expressions applied to untrusted input anchor the whole value and are built to
  avoid catastrophic backtracking.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Uploaded files are stored under server-generated random names; a client-supplied path or
  filename is never trusted.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Secrets never appear in source, configuration files, container images, logs, or version
  control history. They reach the process by runtime injection or a secrets manager.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Secret detection runs both before commit and in the pipeline. The secret-detection gate
  in gates.md is the pipeline half; a pre-commit hook is the developer half and is not yet
  installed here.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- Access to secrets follows least privilege, and a compromised secret is revoked
  immediately rather than rotated on the normal schedule.
  [source: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html · tier: 1-docs · verified: 2026-08-12]
- The kit's own source catalog points at an OWASP Python cheat sheet that now returns 404.
  Python-specific security guidance here is therefore grounded in the OWASP input
  validation and secrets management cheat sheets instead. Correcting the catalog entry is
  an ai-delivery kit change, not a change to this repository.
  [source: https://cheatsheetseries.owasp.org/ · tier: 1-docs · verified: 2026-08-12]

## Documentation Conventions

- Public functions, classes, and modules carry docstrings stating what the surface does,
  what it takes, and what it raises.
  [source: ai-delivery/skills/setup/profiles/software.md § Verification method · tier: 1-profile · verified: 2026-08-12]
- Engineering decisions are recorded in docs/decisions.md at the point the decision is
  made — what was chosen, what else was considered, and why. Not a transcript.
  [source: .ai-delivery/config.md § Preferences · tier: 1-code · verified: 2026-09-07]
- Stakeholder documents live in this repository, under the feature directory. Notion is
  reachable again as of this re-run, but the standing decision is that the repository owns
  every document, so no Notion parent is nominated and nothing is written there.
  [source: .ai-delivery/config.md § Integrations · tier: 1-code · verified: 2026-09-07]

## Linear Conventions

- Hierarchy: a Linear project is one accepted group of requests, carrying the five
  stage milestones — Discovery, Prototype, Build, Validate, Release — whose names are
  identical in every project and come from the shared spine. A milestone holds the work
  of its own stage; an issue's own maturity is its issue status, never its milestone.
  Issues are units of work with plain-language titles and acceptance criteria as
  prose in the description; sub-issues are implementation units when finer decomposition
  is needed — **always created with the project set explicitly** (sub-issues do not
  inherit the parent's project, and project-scoped listing misses unprojected ones).
  Exactly one integration issue per project (label `integration`), created by the
  prototype skill in the Prototype milestone, never in an engineering-owned stage.
  [source: kit design · tier: 1-docs · verified: 2026-08-04]
- Work for this project lives in team MAX (Max-test-workspace). This is the only team the
  connected Linear workspace exposes.
  [source: .ai-delivery/config.md § Linear · tier: 1-code · verified: 2026-09-07]
- Priority is Linear's native field (Urgent/High/Medium/Low/None). Out-of-scope ("won't")
  items are never created as issues — they belong in the requirements document.
- Statuses: address states by the names recorded in config.md ## Linear; branch on state
  *type*, never on name. For this team those names are Triage, Backlog, Todo, In Progress,
  Done, Canceled, and Duplicate. New issues are created in the backlog- or unstarted-type
  state, which here means Backlog or Todo. This team has no second started-type state, so
  there is no separate review state to move through.
  [source: .ai-delivery/config.md § Linear · tier: 1-code · verified: 2026-09-15]
- Titles: short imperative phrases naming the outcome ("Add rate limiting to the token
  endpoint"), no story grammar, no ticket-style prefixes.
- Labels: search before creating; creating a label requires user approval. Issue label
  writes REPLACE the full set — always read the issue's current labels and write back the
  merged list. This read-modify-write rule is a convention, not an enforced hook: a hook
  must be decidable from the tool call's arguments plus files on disk, and the current
  label set exists only in Linear (the tracker is references-only by design), so there is
  nothing on disk to diff a proposed labels array against. The kit-reserved labels
  (awaiting-verification, verified, escalated,
  rework, integration) are defined by the skills, not by this file, and are never renamed
  here.
- All five kit-reserved labels already exist on this team, so no skill needs to ask to
  create one. The team's own taxonomy is Bug, Improvement, and Feature; reuse these rather
  than introducing parallel names for the same distinction. A sixth label, kit-e2e-test,
  marks disposable objects created by kit probes and end-to-end tests. The `gate` label,
  which marks the review issue that closes each stage, and the `request` label, which
  marks an issue recording an original request, do not exist on this team yet; the
  search-before-create rule above applies to both.
  [source: Linear list_issue_labels for team MAX · tier: 1-code · verified: 2026-09-21]
- No default handoff reviewer is recorded, so ship asks who the reviewer is at each
  handoff rather than assuming one.
  [source: .ai-delivery/config.md § Linear · tier: 1-code · verified: 2026-09-21]
- Before create: resolve initiative state; read tracker.md; read bound-initiative projects.
  Nothing may be created before the applicable reads finish.
  [source: owner ruling · tier: 1-docs · verified: 2026-08-15]
- A tracker is valid for this gate when it names a project identifier and URL. Under a
  present-null initiative state, a valid tracker is a resume outside an initiative: select
  that project silently, do not ask a project question, and do not create or rebind one.
  No initiative-membership check applies because no initiative is bound.
  [source: owner ruling · tier: 1-docs · verified: 2026-08-15]
- For a bound initiative, read its projects across every team and complete every page.
  If a valid tracker's project identifier appears in that read, select that project
  silently and do not report the read's extent or ask the three-branch project question.
  [source: owner ruling · tier: 1-docs · verified: 2026-08-15]
- If the tracked project identifier does not appear in the bound-initiative read, stop,
  say that it is no longer in the initiative, and show every project the read did find by
  name and identifier plus the count. Do not create or rebind a project.
  [source: owner ruling · tier: 1-docs · verified: 2026-08-15]
- With no tracker, report every project read by name and count, then say a project would
  not appear if its owning team is private and the reader does not belong to it. Offer all
  three branches together: attach to one reported project; create a project whose
  kit-proposed name the human confirms or edits; or create nothing. Never choose a branch.
  A created project is attached beneath the bound initiative.
  [source: kit design · tier: 1-docs · verified: 2026-08-15]
- Initiative binding has three states: a non-null identifier binds new work beneath that
  initiative; present null records a deliberate decline, so read tracker.md before any
  project create and say that new work is outside an initiative and no overlap check ran;
  an absent key identifies a config that predates initiative binding, so the gate stops
  and offers a setup re-run rather than treating it as a decline.
  [source: kit design · tier: 1-docs · verified: 2026-08-15]
- This project records a present-null initiative binding: the decline branch above is the
  live one. Beyond that standing decline, the connected Linear server exposes no
  initiative-listing call at all, so the bound-initiative read cannot be performed here
  even if a binding were later added by hand.
  [source: .ai-delivery/config.md § Linear · tier: 1-code · verified: 2026-09-07]
- After an attach or create, record the selected project's identifier and URL in the
  feature's tracker.md immediately. A valid tracker is retained on resume. After every
  successful issue create, record its returned identifier there too; resume matches by
  identifier, never by title.
  [source: kit design · tier: 1-docs · verified: 2026-08-15]
- Two projects in this workspace share the name "kit-scratch handoff probe". Resolve that
  project by identifier, never by name, because a name lookup picks arbitrarily between
  them.
  [source: Linear list_projects for team MAX · tier: 1-code · verified: 2026-09-07]
- No project on this team carries any of the five stage milestones yet. Seven carry the
  earlier six-stage names instead — Shaped, Specified, Prototyped, Handed off, Built and
  Shipped: Repository usage documentation, Folder summary, Text preview, Reading list
  export and both kit-scratch handoff probe projects carry all six, and Notebook export
  carries only Shaped and Specified. Folder summary, Text preview and Notebook export also
  carry an unused Editorial review milestone. Looking up a stage milestone by exact name
  in any project here therefore finds nothing.
  [source: Linear list_projects for team MAX · tier: 1-code · verified: 2026-09-21]
- Search-before-create, the transactional-gate rule, and rework-time state transitions
  are likewise conventions, not hooks, for the same platform reason: each requires a
  Linear-side read (existing issues, a write's outcome, an issue's current state) that
  no check decidable from the tool call's arguments plus files on disk can perform.
- Required on every kit-created work issue: description with acceptance
  criteria, priority, the milestone of the stage whose outcome its work
  delivers, and the project. A work issue never changes milestone afterwards.
  A request issue records an original request rather than a unit of work, and
  is the exception: it carries the `request` label and **no milestone**.
  Triage creates it when it accepts the group, with the request text,
  requester, channel, date, configured team, backlog state and project, plus
  a comment linking the project, delivery issues and other grouped requests.
- Linear Documents are not used — the repo owns specs and design docs, and (because no
  Notion parent is nominated here) stakeholder documents too. Attach links, not documents.
- Descriptions are annotated, never rewritten: use anchored patch edits; never anchor a
  patch across an issue identifier (Linear rewrites identifiers into mention markup on
  save).

# Anchor rules for tracker descriptions

Read this before editing any tracker issue or project description with an
anchored patch.

Build every patch against a fresh read of the stored description, never against
text this session sent. What the caller submitted and what the tracker stored
are different bytes, and only the stored bytes are a valid patch baseline.

Read the stored description immediately before each patch. One read does not
cover a later patch: a save between the read and the patch moves the text the
anchor depends on, so a second patch needs its own read.

The tracker rewrites markdown on every save. It does not only substitute
characters; it inserts structure, including a blank line between a paragraph
and a list beneath it. Identifiers become mention markup. The stored form is
therefore not the form that was sent.

An anchor built from stale text fails while every character in it still looks
correct. Nothing in review shows the defect, because the anchor is wrong only
against bytes the reviewer is not looking at. The fresh read is the control.
