# Design discovery: Pull request checklist

This design covers a written pull request checklist for this repository: a
`CONTRIBUTING.md` at the root holding five items, and one sentence at the end of the README
pointing to it. It matters because two to five outside contributors, the ai-delivery
kit's first users, start opening pull requests by 2026-10-05. Without the checklist they
meet this repository's standard only at review, after their work is done.

**Profile:** software (of config: software)
**Date:** 2026-09-22
**Feature directory:** `.ai-delivery/features/pull-request-checklist/`
**Linear project:** P-MAX-12 Pull request checklist —
https://linear.app/max-test-workspace/project/pull-request-checklist-08fae13de2f4
**Work issues:** MAX-45 (the checklist file) and MAX-46 (the README sentence)
**Requirements:** `requirements.md` in the feature directory, approved 2026-09-22
**Discovery brief:** `brief.md` in the feature directory

> **Terms used here.** MAX-45 and MAX-46 are the Linear issues that track the two units of
> work. FR-001 to FR-007 are the requirement labels in `requirements.md`, and "open
> question N" refers to the numbered list at its end. The *setup check* is the kit's
> staleness check: every kit skill runs it first, and stops when it reads STALE instead of
> FRESH. The *setup record* is `.ai-delivery/stack-fingerprint`, the file of hashes that
> check compares against. *Ship* is the kit's commit-and-pull-request skill.

## Executive summary

Two Markdown files carry the whole feature: a new `CONTRIBUTING.md` of about 30 lines,
and a one-sentence addition to `README.md`. Three small pytest modules prove both files
meet their acceptance criteria. They live in the feature directory, where pytest's
default run does not look, so checklist item 3 stays true. The README edit makes the
setup check read STALE, so integration ends with a setup re-run that returns it to FRESH.

## Codebase conventions

### Detected stack

From `.ai-delivery/config.md` § Stack; nothing here is re-detected.

- **Language:** Python
- **Framework:** none (`primary_framework: null`)
- **Build tool:** uv
- **Cloud provider:** none (`cloud_provider: null`)
- **Test framework:** pytest, with coverage by pytest-cov
- **Quality and security tools:** ruff, mypy, bandit, pip-audit, gitleaks

### Project structure

- The repository tracks six top-level entries: `.ai-delivery/`, `.gitignore`,
  `README.md`, `docs/`, `pyproject.toml` and `uv.lock` (read 2026-09-22).
- It has no Python modules, no tests, no CI configuration, no pull request template, no
  licence and no `CONTRIBUTING.md`.

### Established patterns

No code module exists to follow, so two precedents were analyzed instead:

1. **`README.md`**, the only document at the root written for a newcomer. It has a
   level-1 heading and prose paragraphs hard-wrapped near 90 columns, and ends with a
   single newline. `CONTRIBUTING.md` follows the same Markdown style.
2. **`.ai-delivery/features/cited-source-staleness/fr-015-harness/`**, the only
   executable code in the repository. It is a verification harness kept inside its
   feature directory rather than in a product path. The acceptance checks follow it in
   location, not in language: the harness is JavaScript, and the checks are Python, the
   project's language.

### Test conventions

- pytest is declared in `pyproject.toml`'s dev group and pinned by `uv.lock`. No pytest
  configuration section exists.
- `uv run pytest` from the root collects nothing. It prints "no tests ran" and exits with
  code 5 (verified 2026-09-22, pytest 9.1.1).
- pytest's default run skips directories whose names begin with a dot. A test module
  under `.ai-delivery/` is collected only when its directory is named on the command line
  (verified 2026-09-22 in a scratch copy of the repository).
- `.ai-delivery/conventions.md` asks for test functions named `test_…`, the importlib
  import mode, annotated public signatures, and docstrings on public functions and
  modules.

### Quality gates as recorded

`.ai-delivery/gates.md` records the ruff, ruff format, mypy and pytest commands scoped to
`src/` and `tests/`. Neither directory exists, so on 2026-09-22 the lint, format and
type-check commands exited with errors before checking anything. This feature adds
neither directory, so its verification runs the same tools on its checks directory by
name. `gates.md` itself is setup's record and is not changed here.

### Migrations

None. The repository has no database or schema.

## Use case and business value

**Who it serves.**
- **Outside contributors, two to five people:** the kit's first users. They know the
  kit from its README and have never worked in this repository.
- **The maintainer, Max Adamsky:** today the only author and reviewer. The maintainer
  will hold the standard and keep the success count.

**What changes for them.** A contributor reads the five things every pull request here
must include before naming a branch or writing a commit. GitHub shows a root
`CONTRIBUTING.md` as the repository's Contributing tab and sidebar link, and links it
from the new-issue and new-pull-request pages. The README sentence reaches it in one
step from the first page the kit's users read.

**Happy path.** The contributor opens the repository, follows the Contributing link or the
README sentence, and reads the five items. They name the branch, shape the commits and
run the tests as the items say. They open a pull request whose description says why and
links a GitHub issue, and review asks for none of the five.

**Success measures** (requirements § 1). Across the first ten outside pull requests,
count those that needed a comment asking for item 1, 2, 4 or 5. At most one means it
worked, exactly two is inconclusive, and three or more means it did not work. The
checklist is in place, and linked from the README, before the first outside pull request.

**Out of scope** (requirements § 2): automated enforcement, a pull request template, a
code of conduct, a release process, anything about how the kit works, a Contributing
section inside the README, a licence, branch protection, rewriting item 3, adopting a
published contributing template, and any change to the kit.

## Discovery answers

| Area | Answer | Source |
|---|---|---|
| Problem | The standard for a pull request lives only in the maintainer's head, so newcomers meet it at review. | requirements § 1 |
| Scale | Two to five contributors now, six people at most; the success window is ten pull requests. At ten times that, both documents hold unchanged; the maintainer's manual count is what stops scaling (open question 7). | brief § 2 |
| Load | None. The feature is two static documents with no runtime. | — |
| Integration | GitHub renders both files and surfaces `CONTRIBUTING.md` from the default branch. The setup check hashes `README.md`. Three README issues in another project, MAX-16 to MAX-18, edit the same file. | brief § 4 and § 12 |
| Compliance | No personal data. Branch names carry contributors' public GitHub handles; the example uses GitHub's own sample account, `octocat`. Licensing is open question 10. | requirements § 2 |
| Timeline | Fixed: contributors arrive by 2026-10-05. | requirements § 4 |

## Decisions settled in this phase

Max Adamsky settled four open questions on 2026-09-22. They are recorded in the Q&A log
as exchange 38 and in `docs/decisions.md`.

1. **Question 1, tool defaults.** A pull request made exactly as ship makes it misses
   items 1, 4 and 5. The checklist's one introductory sentence says the five items apply
   whichever tool opens the pull request. It does not name the kit, so the out-of-scope
   line on the kit holds.
2. **Question 2, commits.** One commit per logical change, so a pull request may hold
   several commits.
3. **Question 5, the linked issue.** The contributor files a GitHub issue, or picks an
   existing one, before starting work. Max Adamsky triages GitHub issues and adds any
   Linear link at review.
4. **Question 4, the README sentence.** The sentence is appended to this branch's
   README, after the MAX-16 rewrite. A setup re-run at integration returns the setup
   check to FRESH in the same change.

## Architecture decision

### Chosen approach

Discovery settled the direction (brief § 4 to § 6): one root `CONTRIBUTING.md` and a
one-sentence README pointer, with no pull request template. This design adds two
things: how the documents are proven, and how the README edit keeps the setup check
FRESH. It has four parts:

1. **`CONTRIBUTING.md` (MAX-45).** A title, the tool-neutral introductory sentence, and
   five numbered items, each one rule sentence followed by one example.
2. **The README sentence (MAX-46).** One new last paragraph in `README.md`: one sentence
   holding a relative link to `CONTRIBUTING.md`.
3. **The acceptance checks.** Three pytest modules in
   `.ai-delivery/features/pull-request-checklist/checks/`, one per unit and one for
   integration, run by naming that directory.
4. **The setup record refresh (integration).** A setup re-run in the main session after
   the README edit, so the setup check reads FRESH.

### Architecture diagram

```
 Outside contributor
      │
      ├──► GitHub repository page ── Contributing tab, sidebar link ──────┐
      │    (the new-issue and new-pull-request pages link it too)         │
      │                                                                   ▼
      └──► README.md ── last sentence, relative link ──────────►  CONTRIBUTING.md
            (MAX-46)                                               (MAX-45)
                │                                                  title
                │ its sha256 is recorded in                        one tool-neutral sentence
                ▼                                                  items 1 to 5, rule + example
      .ai-delivery/stack-fingerprint  ◄── setup re-run (integration, main session)
                │
                ▼
      kit setup check: FRESH or STALE

      .ai-delivery/features/pull-request-checklist/checks/   (outside pytest's default run)
        test_contributing.py ─────────► reads CONTRIBUTING.md
        test_readme_link.py ──────────► reads README.md
        test_checklist_reachable.py ──► follows the README link into CONTRIBUTING.md
```

### ADR-001: Keep the acceptance checks out of pytest's default run

**Status:** Accepted, proposed by the orchestrator; Max Adamsky approves it with the
implementation plan.
**Date:** 2026-09-22
**Deciders:** Max Adamsky, the prototype orchestrator

**Context.** The software profile proves work with a test suite written before the
implementation. This feature's own item 3 tells contributors that "no tests ran" (exit
code 5) is the expected result until the first test module lands, and FR-004 checks
exactly that. Any test module in pytest's default collection makes item 3 false the
moment it lands.

**Decision.** The checks are pytest modules in
`.ai-delivery/features/pull-request-checklist/checks/`, run with that directory named on
the command line. A plain `uv run pytest` still collects nothing.

**Consequences.**
- **Positive:** the proof is repeatable, it is written before the documents, and item 3
  stays true on the day the feature lands.
- **Negative:** the recorded lint and type-check gates do not cover the checks, so ruff
  and mypy run on the directory by name. The layout departs from the conventions'
  tests-directory rule, for the reason above. It also departs from the project rubric's
  blocking item that anything added be reachable from the test command in
  `.ai-delivery/gates.md`. FR-004 outranks that item under config's `nfr_precedence`,
  which puts requirements first, and the specs name the departure so that verification
  treats it as a named exception, not a silent one.
- **Risks:** a reader could mistake the checks for enforcement on contributors. They
  check this feature's two files and nothing a contributor submits.

**Alternatives considered.**

| Dimension | A: checks in `tests/` | B: checks in the feature directory | C: no checks, read only |
|---|---|---|---|
| Replaceability | Adequate: ordinary test modules | Strong: the same modules move into `tests/` unchanged | Weak: nothing to replace |
| Cognitive load | Strong: the usual place | Adequate: the command must name the directory | Strong: nothing to learn |
| Risk isolation | Weak: makes item 3 false on landing | Strong: the default run is unchanged | Adequate: no side effects, but no repeatable proof |
| Future flexibility | Weak: forces open question 8's rewrite now | Strong: moves to `tests/` when item 3 is rewritten | Weak: every later check is manual |
| **Verdict** | Rejected | **Chosen** | Rejected |

## Core data model

The feature stores no data. Its entities are the structures the two documents must hold,
which the checks read.

```
ChecklistDocument: CONTRIBUTING.md at the repository root
├── title: one level-1 heading
├── introduction: exactly one sentence; says the five items apply whichever tool opens
│   the pull request (question 1)
└── items: an ordered list of exactly five ChecklistItem entries

ChecklistItem
├── position: 1 to 5, fixed order: branch name, commits, tests, description, issue link
├── rule: one sentence led by an imperative verb; any required note joins that sentence
│   rather than becoming a second one
└── example: exactly one, introduced by "Example:"

ReadmePointer: the last paragraph of README.md
├── sentence: exactly one
└── link: one relative Markdown link whose target is exactly CONTRIBUTING.md

SetupRecordEntry: README.md's entry in .ai-delivery/stack-fingerprint (setup-owned)
└── sha256: equals README.md's current hash when the setup check reads FRESH
```

**Relationships:**
- ReadmePointer relates to ChecklistDocument (N:1, by relative path).
- SetupRecordEntry relates to `README.md` (1:1, by hash).

**Integrity rules:**
- Exactly five items, in the order FR-002 to FR-006, and exactly one example each.
- Paths are case-sensitive on GitHub, so the filename and the link target are both
  exactly `CONTRIBUTING.md`.
- Every README line before the pointer stays as it was.
- The setup record changes only through setup.

## Open questions this design carries

Max Adamsky owns each of these. None blocks the design or the build.

- **Question 3, the route to `main`. Needed before 2026-10-05.** Prototype builds on
  this branch. GitHub's Contributing tab reads `main`, and item 3's command works there
  only once `pyproject.toml` and `uv.lock` arrive. The deployment strategy in
  `1c-operations.md` states that constraint.
- **Question 6, contributor changes to `.ai-delivery/` and `docs/decisions.md`. Needed
  before 2026-10-05.** The checklist says nothing about it.
- **Question 7, running the count. Needed before the first outside pull request.** The
  count is kept outside both documents.
- **Question 8, when item 3 is rewritten. Needed by the first test module.** ADR-001
  keeps item 3 true until then.
- **Question 9, forks or pushed branches, and branch protection. Needed before
  2026-10-05.**
- **Question 10, a licence. Needed before the first outside pull request.**

## Next steps

- `1b-contracts.md` defines each document's contract, the checks' behaviour, and the
  testing strategy.
- `1c-operations.md` covers security, deployment to `main`, rollback and risks.

Max Adamsky owns the six open questions above. Question 3 decides whether the timing
measure can pass at all, and it is needed before 2026-10-05.
