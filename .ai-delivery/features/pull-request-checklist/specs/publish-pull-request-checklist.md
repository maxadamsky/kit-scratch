# Code Spec: Publish the pull request checklist in CONTRIBUTING.md

- issue: MAX-45
- size: S
- depends_on: NONE (fully parallel)

This unit writes `CONTRIBUTING.md` at the repository root: the five things every pull
request here must include, and a check module that proves the file keeps to its
contract. It matters because outside contributors start by 2026-10-05, and this file is
what GitHub shows them before they name a branch.

**Unit:** MAX-45, Publish the pull request checklist in CONTRIBUTING.md
**Design reference:** `design/1b-contracts.md` "Contract C1: the checklist document" and
"Contract C4: the acceptance checks"; `design/1a-discovery.md` "ADR-001"
**Date:** 2026-09-22

> **Terms used here.** MAX-45 is this unit's Linear issue, and MAX-46 and MAX-47 are the
> README-sentence and integration units. FR-001 to FR-006 are requirement labels in
> `requirements.md`. C1 and C4 are the contracts in `design/1b-contracts.md`, and a
> condition name such as ItemCount comes from C4's error taxonomy.

## Implementation Summary

- **Files to Create:** 2
  - `CONTRIBUTING.md`
  - `.ai-delivery/features/pull-request-checklist/checks/test_contributing.py`
- **Files to Modify:** 0
- **Verification to Add:** 1 test module, about 20 test functions: 15 against the real
  file and 5 against inline sample text
- **Estimated Complexity:** S

## Codebase Conventions

- **File naming:** `CONTRIBUTING.md`, the exact name GitHub recognises; the check module
  is `test_contributing.py`, a name pytest discovers.
- **Import order:** standard library only, in one block, as ruff's defaults sort it.
- **Error handling:** every failing assertion's message names its C4 condition and
  quotes the offending line or text (conventions.md § Error Handling & Logging).
- **Verification framework:** pytest 9.1.1, pinned by `uv.lock`, with no pytest
  configuration. Run it from the repository root:
  `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib .ai-delivery/features/pull-request-checklist/checks/test_contributing.py`
- **Type checking:** mypy 2.3.1, clean on the module; every function annotated.
- **Lint and format:** ruff 0.16.8 `check` and `format --check`, clean on the module,
  with default rules.
- **Documentation:** a module docstring, and a docstring on every function
  (conventions.md § Documentation Conventions).
- **Markdown style for `CONTRIBUTING.md`:** follow `README.md`. Use an ATX `#` heading,
  wrap lines at or before 90 columns, put a blank line between blocks, leave no trailing
  spaces, and end the file with a single newline.

## Technical Context

**Key gotchas:**
- **The words the file may not use apply to its examples too.** No whole-word `kit` or
  `ship`, and no `ai-delivery` or `Claude`. The repository name `kit-scratch` is allowed.
  None of FR-001's excluded topics may appear either: a code of conduct, a release
  process, a pull request template, enforcement, CI or licence terms. Item 4's example
  paragraph is where this is easiest to break, so give it a reason that needs none of
  these words.
- **Item 3 must be literally true here.** A plain `uv run pytest` prints "no tests ran"
  and exits with code 5. Do not create `tests/`, a root `conftest.py` or any pytest
  configuration.
- **The check module's location is deliberate.** ADR-001 puts it outside
  `.ai-delivery/gates.md`'s test command, departing from the project rubric's
  reachability item because FR-004 outranks that item under config's `nfr_precedence`.
  Do not move the module to satisfy the rubric.
- **One sentence per rule.** Leave no abbreviation with a full stop in a rule, such as
  "e.g." or "i.e.". Join any required note to the rule with a semicolon, and end the
  rule with a full stop.
- **Item 5's example carries no closing keyword**, such as `Closes #12` or `Fixes #12`.
  GitHub would close the linked issue on merge, which nobody asked for.
- **Line count.** 24 to 36 lines including blank lines, aiming for about 30.

**Reusable utilities:** none exist, because the repository has no source modules. Use
the standard library only: `pathlib` and `re`, and `dataclasses` if it helps.

**Integration points:**
- MAX-46's README sentence links to this file by its exact name.
- MAX-47's integration check follows that link and reads this file's title and five
  items.

## Contract

Implement C1 exactly. Two things in it come from settled decisions and are not in the
issue's original text:

- **The introduction** is exactly one sentence. It says the five items apply to every
  pull request here whichever tool opens it, and it contains the word "tool". It names
  no tool (question 1).
- **Leading verbs and required phrases, per item.** Phrases are matched without regard
  to case.

| Item | Rule begins with | The rule contains | The example shows |
|---|---|---|---|
| 1 | Name | `<GitHub handle>/<short topic>`, `codex/`, agent | a backticked branch name in `handle/topic` form, not starting with `codex/`, such as `octocat/fix-readme-typo` |
| 2 | Make | logical change, several | what one logical change is, for instance a typo fix and a new section as two commits |
| 3 | Run | `uv run pytest`, no tests ran, exit code 5 | the command and the result it gives today |
| 4 | Write | one-paragraph, why | one paragraph of two or three sentences giving a reason for a change |
| 5 | Link | GitHub issue, before, Linear, review | one `#<number>` issue reference with no closing keyword |

Item 2 settles question 2: one commit per logical change, so a pull request may hold
several commits. Item 5 settles question 5: the contributor files the issue, or picks an
existing one, before starting work, and the maintainer adds any Linear link at review.

## Task Breakdown

### Task 1: Write the check module first

**Dependencies:** None
**Files:** `.ai-delivery/features/pull-request-checklist/checks/test_contributing.py`
(create)
**Pattern:** no test module exists in this repository to imitate. Follow
conventions.md § Testing Conventions and pytest's documented good practices.
**Implementation:**
- Resolve the repository root from the module's own path: the directory four levels
  above the checks directory. Read no environment variables, and never touch
  `sys.path`.
- Keep the parsing and checking in small pure functions that take text and return
  findings. The real-file tests then read `CONTRIBUTING.md` once, and the adverse tests
  pass inline sample text to the same functions.
- Parse items from lines beginning with a digit, a full stop and a space, at column 0.
  An item runs until the next such line or the end of the file. The rule is the text
  before `Example:`, and the example is the text after it, both with whitespace
  collapsed.
- Count sentences by C4's rule: a sentence ends at `.`, `?` or `!` followed by
  whitespace or the end of the text, ignoring full stops inside backtick code spans and
  inside link targets.
- Keep every regular expression linear, with no nested quantifiers, and compare whole
  values by equality rather than by pattern where you can.

**Cases against the real file** (each names its C4 condition on failure):
- The file exists at the root → MissingDocument.
- The first line is the only level-1 heading → TitleMissing.
- Exactly one sentence stands between the title and item 1, and it contains "tool" →
  IntroductionCount or IntroductionNotToolNeutral.
- Exactly five items exist, numbered 1 to 5 in order → ItemCount.
- Each item's rule begins with its leading verb → ItemContent.
- Each rule contains its required phrases → ItemContent, naming the item and the missing
  phrase.
- Each rule is exactly one sentence → RuleSentenceCount.
- Each item has exactly one `Example:` → ExampleCount.
- Item 1's example is a `handle/topic` code span not starting with `codex/` →
  ItemContent.
- Item 4's example is one paragraph of two or three sentences → ItemContent.
- Item 5's example holds a `#<number>` reference and no closing keyword (close, closes,
  closed, fix, fixes, fixed, resolve, resolves or resolved) → ItemContent.
- The file has 24 to 36 lines → LengthOutOfRange.
- No excluded word or topic appears → ExcludedTopic, naming the word and its line.
- No line after item 5 starts at column 0 → TrailingContent.
- The file ends with exactly one newline → FileEnding.

**Adverse cases against inline sample text** (each shows its check can fail):
- A sample with four items is reported as ItemCount.
- A sample item with no `Example:` is reported as ExampleCount, and so is one with two.
- A sample rule of two sentences is reported as RuleSentenceCount.
- A sample naming "the kit" is reported as ExcludedTopic, and a sample naming only
  `kit-scratch` is not.
- A sample item 5 whose example reads `Closes #12` is reported as ItemContent.

**Expected state after Task 1:** the real-file tests fail with MissingDocument, and the
adverse tests pass.

---

### Task 2: Write `CONTRIBUTING.md`

**Dependencies:** Task 1
**Files:** `CONTRIBUTING.md` (create)
**Pattern:** `README.md`, for Markdown style
**Implementation:**
- Write the title, the one tool-neutral sentence, then items 1 to 5 as C1 and the table
  above require.
- Write each item's rule on its numbered line, wrapped with a three-space indent, then a
  blank line, then its `Example:` line or lines at the same indent.
- Keep the whole file to 24 to 36 lines.
- Run the Task 1 module after each change until every test passes.

**Verification:** every case in Task 1 passes against the real file.

---

### Task 3: Quality pass

**Dependencies:** Task 2
**Files:** no new files.
**Implementation:** run, from the repository root:
- `uv run ruff check .ai-delivery/features/pull-request-checklist/checks/test_contributing.py`
- `uv run ruff format --check .ai-delivery/features/pull-request-checklist/checks/test_contributing.py`
- `uv run mypy .ai-delivery/features/pull-request-checklist/checks/test_contributing.py`
- a plain `uv run pytest`, which must still print "no tests ran" and exit with code 5
- a check that no line of `CONTRIBUTING.md` is longer than 90 columns

Fix whatever fails, then run the Task 1 command once more.

**Verification:**
- ruff and mypy exit 0.
- The plain pytest run exits with code 5.
- The module passes in full.
- `git status --short` shows only this unit's two files as new, with no `__pycache__`.

## Task Dependency Graph

```
Task 1: check module, written first; it fails on MissingDocument
    │
    └─→ Task 2: CONTRIBUTING.md; the module then passes
            │
            └─→ Task 3: ruff, mypy, the plain pytest run exits 5, line widths
```

## Pattern References

- **Document pattern:** `README.md`: its heading style, its wrapping at or before 90
  columns, and its single trailing newline.
- **Verification pattern:** none exists in this repository. Use conventions.md
  § Testing Conventions: `test_` names, the importlib import mode, annotated functions
  and docstrings.

## Implementation Notes

- **Security:** the module reads one repository file and inline strings, and makes no
  network, subprocess or git calls. `CONTRIBUTING.md` links nothing outside the
  repository and asks contributors for nothing secret.
- **Performance:** not applicable; one small file is read once per test run.
- **Deployment:** none in this unit. Nothing is committed, because the user handles
  commits at handoff.
- **Rubric notes:**
  - No code crosses a unit boundary, so the interface-or-protocol item has nothing to
    apply to. The contract between units is C1's file name and structure.
  - The module deliberately has no `conftest.py`, since one would be a file shared with
    MAX-46.

## Final Verification

**Functionality:**
- [ ] Every C1 criterion passes against the real `CONTRIBUTING.md`, and FR-001 to FR-006
  are each covered.
- [ ] The introduction is tool-neutral, item 2 says one commit per logical change, and
  item 5 says to file or pick the issue before starting work.

**Code quality:**
- [ ] The module is clean under ruff check, ruff format and mypy, and is fully annotated
  and documented.
- [ ] It has no debug leftovers and no commented-out code.

**Testing:**
- [ ] The module was written first and failed with MissingDocument before the file
  existed.
- [ ] Adverse cases prove that each major check can fail.
- [ ] A plain `uv run pytest` still exits with code 5.

**Build:**
- [ ] Only the two files named above are created, and nothing else in the working tree
  changes.
