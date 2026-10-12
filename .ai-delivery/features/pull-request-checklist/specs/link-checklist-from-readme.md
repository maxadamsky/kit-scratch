# Code Spec: Link the pull request checklist from the README

- issue: MAX-46
- size: S
- depends_on: NONE (fully parallel)

This unit adds one sentence at the end of `README.md` linking to the pull request
checklist, plus a check module that proves the sentence keeps to its contract. It
matters because the README is the first thing the kit's users read, and the sentence
takes them to the checklist in one step.

**Unit:** MAX-46, Link the pull request checklist from the README
**Design reference:** `design/1b-contracts.md` "Contract C2: the README pointer" and
"Contract C4: the acceptance checks"
**Date:** 2026-09-22

> **Terms used here.** MAX-46 is this unit's Linear issue. MAX-45 is the unit writing
> `CONTRIBUTING.md`, and MAX-47 is the integration unit. FR-007 is a requirement label in
> `requirements.md`. C2 and C4 are contracts in `design/1b-contracts.md`, and a
> condition name such as LinkTargetMismatch comes from C4's error taxonomy. The *setup
> check* is the kit's staleness check, which reads FRESH or STALE.

## Implementation Summary

- **Files to Create:** 1
  - `.ai-delivery/features/pull-request-checklist/checks/test_readme_link.py`
- **Files to Modify:** 1
  - `README.md`
- **Verification to Add:** 1 test module, about 11 test functions: 6 against the real
  file and 5 against inline sample text
- **Estimated Complexity:** S

## Codebase Conventions

- **File naming:** the check module is `test_readme_link.py`, a name pytest discovers.
- **Import order:** standard library only, in one block, as ruff's defaults sort it.
- **Error handling:** every failing assertion's message names its C4 condition and
  quotes the offending text (conventions.md § Error Handling & Logging).
- **Verification framework:** pytest 9.1.1, pinned by `uv.lock`, with no pytest
  configuration. Run it from the repository root:
  `PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib .ai-delivery/features/pull-request-checklist/checks/test_readme_link.py`
- **Type checking and lint:** mypy 2.3.1, and ruff 0.16.8 `check` and `format --check`,
  all clean on the module; every function annotated.
- **Documentation:** a module docstring, and a docstring on every function.
- **Markdown style:** match `README.md`'s existing paragraphs. Wrap at or before 90
  columns, leave no trailing spaces, and end the file with a single newline.

## Technical Context

**Key gotchas:**
- **Change no existing line.** The sentence becomes a new paragraph after the current
  last line, "the kit produces.", separated from it by one blank line. Appending the
  sentence to that line would change it.
- **The link target is exactly `CONTRIBUTING.md`.** Use no `./`, no leading slash and no
  full GitHub URL. GitHub resolves the relative target against the repository root on
  whichever branch is shown.
- **The target need not exist for this unit.** MAX-45 writes it in the same batch, and
  the integration check proves the link resolves. This module must not read
  `CONTRIBUTING.md`.
- **The setup check will read STALE after this edit.** That is expected. Do not run
  setup, and do not write `.ai-delivery/stack-fingerprint`; the kit's write guard
  refuses that write from a subagent. MAX-47 re-runs setup in the main session.
- **The check module's location is deliberate.** As ADR-001 in `design/1a-discovery.md`
  records, it stays outside `.ai-delivery/gates.md`'s test command, so that a plain
  `uv run pytest` still exits with code 5. Do not move it.

**Reusable utilities:** none; use the standard library only (`pathlib`, `re`).

**Integration points:**
- The link consumes C1 by name only.
- MAX-47's integration check follows this link.

## Contract

Implement C2 exactly:

- The file still begins with `# kit-scratch`.
- The last paragraph, meaning the text after the final blank line, is exactly one
  sentence.
- That sentence holds exactly one Markdown inline link, `[text](target)`, whose target is
  exactly `CONTRIBUTING.md`.
- The sentence contains the word "checklist", so a reader knows why to follow the link.
- The file ends with exactly one newline.
- Every line before the new paragraph stays byte-identical to `README.md` at commit
  7133948. A diff at verification proves this, not a test, because the base differs on
  each branch the sentence lands on.

A sentence of this shape satisfies the contract: "Before you open a pull request, read
the [pull request checklist](CONTRIBUTING.md)." The wording is the implementer's to
choose within the contract.

## Task Breakdown

### Task 1: Write the check module first

**Dependencies:** None
**Files:** `.ai-delivery/features/pull-request-checklist/checks/test_readme_link.py`
(create)
**Pattern:** no test module exists in this repository to imitate. Follow
conventions.md § Testing Conventions.
**Implementation:**
- Resolve the repository root from the module's own path: the directory four levels
  above the checks directory. Never touch `sys.path` or read the environment.
- Keep the parsing in pure functions that take README text. The real-file tests read
  `README.md` once, and the adverse tests pass inline samples to the same functions.
- Split paragraphs on blank lines, and take the last non-empty one with its whitespace
  collapsed.
- Count sentences by C4's rule, ignoring full stops inside backtick code spans and link
  targets. The target `CONTRIBUTING.md` must not count as a sentence end.
- Find links with a linear pattern for `[text](target)`, with no nested quantifiers, and
  compare the target by exact string equality.

**Cases against the real file** (each names its C4 condition on failure):
- `README.md` exists at the root → MissingDocument.
- The first line is `# kit-scratch` → TitleMissing.
- The last paragraph is exactly one sentence → PointerSentenceCount.
- That paragraph holds exactly one inline link, whose target is exactly
  `CONTRIBUTING.md` → LinkTargetMismatch.
- The sentence contains "checklist" → PointerUnlabelled.
- The file ends with exactly one newline → FileEnding.

**Adverse cases against inline sample text:**
- A last paragraph of two sentences is reported as PointerSentenceCount.
- A sentence appended to the previous paragraph's last line, with no blank line between,
  is reported as PointerSentenceCount. The last paragraph then holds more than one
  sentence.
- A link target of `https://github.com/maxadamsky/kit-scratch/blob/main/CONTRIBUTING.md`
  is reported as LinkTargetMismatch, and so is `./CONTRIBUTING.md`.
- A last paragraph with no link is reported as LinkTargetMismatch.
- A sample whose sentence lacks "checklist" is reported as PointerUnlabelled.

**Expected state after Task 1:** the real-file tests for the pointer fail. Today's last
paragraph is the three-sentence purpose statement, with no link, so the module reports
PointerSentenceCount, LinkTargetMismatch and PointerUnlabelled. The title, file-ending
and adverse tests pass.

---

### Task 2: Append the sentence to `README.md`

**Dependencies:** Task 1
**Files:** `README.md` (modify)
**Modification note:** `README.md` gets one blank line, then the new one-sentence
paragraph, after its current last line ("the kit produces."). The file keeps its single
trailing newline, and no other byte changes.
**Verification:** every Task 1 case passes against the real file.

---

### Task 3: Quality pass

**Dependencies:** Task 2
**Files:** no new files.
**Implementation:** run, from the repository root:
- `uv run ruff check .ai-delivery/features/pull-request-checklist/checks/test_readme_link.py`
- `uv run ruff format --check .ai-delivery/features/pull-request-checklist/checks/test_readme_link.py`
- `uv run mypy .ai-delivery/features/pull-request-checklist/checks/test_readme_link.py`
- a plain `uv run pytest`, which must still exit with code 5
- `git diff 7133948 -- README.md`

**Verification:**
- ruff and mypy exit 0.
- The plain pytest run exits with code 5.
- The diff shows only added lines at the end of the file: one blank line and the
  sentence.
- `git status --short` shows `README.md` modified and this unit's module new, with no
  `__pycache__`.

## Task Dependency Graph

```
Task 1: check module, written first; its pointer tests fail
    │
    └─→ Task 2: append the sentence to README.md; the module then passes
            │
            └─→ Task 3: ruff, mypy, the plain pytest run exits 5, README diff
```

## Pattern References

- **Document pattern:** `README.md` itself: its paragraph style and its wrapping at or
  before 90 columns.
- **Verification pattern:** none exists in this repository. Follow conventions.md
  § Testing Conventions.

## Implementation Notes

- **Security:** the module reads one repository file and inline strings, and makes no
  network, subprocess or git calls. The link is relative and points inside the
  repository.
- **Deployment:** none in this unit. Nothing is committed, and the setup check stays
  STALE until MAX-47.
- **Rubric notes:**
  - No code crosses a unit boundary; the contract is C2's shape and link target.
  - The module has no `conftest.py`, since one would be a file shared with MAX-45.

## Final Verification

**Functionality:**
- [ ] Every C2 criterion passes against the real `README.md`, covering FR-007's
  sentence-and-link criterion.
- [ ] The diff against commit 7133948 shows only the new blank line and the sentence.

**Code quality:**
- [ ] The module is clean under ruff check, ruff format and mypy, and is fully annotated
  and documented.
- [ ] It has no debug leftovers and no commented-out code.

**Testing:**
- [ ] The module was written first, and failed before the sentence existed.
- [ ] Adverse cases prove that each check can fail.
- [ ] A plain `uv run pytest` still exits with code 5.

**Build:**
- [ ] Only `README.md` and this unit's module change, and the setup record is untouched.
