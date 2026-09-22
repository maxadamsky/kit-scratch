# Design contracts: Pull request checklist

This document fixes what `CONTRIBUTING.md`, the README sentence and the setup record must
hold, and what the acceptance checks prove about each. It matters because the two units
are built at the same time by separate workers, and each is verified against these
contracts before the two are joined.

**Date:** 2026-09-22
**Feature directory:** `.ai-delivery/features/pull-request-checklist/`
**Builds on:** `design/1a-discovery.md`
**Units:** MAX-45 builds contract C1, MAX-46 builds C2, and the integration unit builds C3
and proves the join. All three add their checks under C4.

> **Terms used here.** MAX-45 and MAX-46 are the Linear issues for the two units. FR-001
> to FR-007 are the requirement labels in `requirements.md`, and "question N" is that
> document's open question N. The *setup check* is the kit's staleness check, which reads
> FRESH or STALE. The *setup record* is `.ai-delivery/stack-fingerprint`, the hashes that
> check compares against. The *kit's write guard* is a kit hook that refuses a subagent's
> write to files setup owns.

## Contract C1: the checklist document (MAX-45)

**Consumers:** outside contributors reading it; GitHub, which surfaces a file with this
name at this location; and C2's link.

**Location and name:** the repository root, named exactly `CONTRIBUTING.md`. GitHub
matches paths case-sensitively.

**Structure, in order:**

1. **Title:** the first line is the only level-1 heading, in plain words.
2. **Introduction:** exactly one sentence between the title and item 1. It says the five
   items apply to every pull request here, whichever tool opens it (question 1). It does
   not name the kit or any of its parts.
3. **Items:** an ordered list numbered `1.` to `5.`, each number at the start of its
   line, in the order below. Nothing follows item 5.
4. **Each item** holds its rule, then its example:
   - **Rule:** one sentence, beginning with the item's leading verb. A required note,
     such as item 1's reserved prefix, joins that sentence after a semicolon rather
     than becoming a second sentence. No abbreviation with a full stop appears in a
     rule, because a full stop ends the sentence.
   - **Example:** exactly one, introduced by `Example:`, after the rule.

**Length:** about 30 lines, and within 24 to 36 lines inclusive, counting blank lines.
Lines wrap at or before 90 columns, close to `README.md`'s own wrapping; one existing
README line runs to 91. The file ends with a single newline.

**Content per item:**

| Item | Leading verb | The rule must say | The example must show | Requirement |
|---|---|---|---|---|
| 1. Branch name | Name | the branch is named `<GitHub handle>/<short topic>`; the `codex/` prefix is reserved for branches made by agents | one branch name in that form, such as `octocat/fix-readme-typo`, not starting with `codex/` | FR-002 |
| 2. Commits | Make | one commit per logical change, so a pull request may hold several commits (question 2) | what one logical change is, for instance two unrelated edits as two commits | FR-003 |
| 3. Tests | Run | run `uv run pytest` before opening a pull request; until the first test module lands, "no tests ran" (exit code 5) is the expected result | the command and the result it gives today | FR-004 |
| 4. Description | Write | a one-paragraph pull request description saying why the change was made | one paragraph of two or three sentences giving a reason, not a list of changes | FR-005 |
| 5. Issue link | Link | link a GitHub issue on this repository in the description, filed or picked before work starts (question 5); the maintainer adds any Linear link at review | one issue reference in GitHub's `#<number>` form, with no closing keyword | FR-006 |

Item 5's example carries no closing keyword such as `Closes` or `Fixes`. GitHub closes
the linked issue on merge when one is present. Nobody asked for that behaviour, and the
maintainer triages GitHub issues (question 5).

**Excluded content** (FR-001), anywhere in the file:
- a code of conduct, a release process, a pull request template, automated
  enforcement, or licence terms;
- any mention of the kit: the words `kit` and `ship` as words, `ai-delivery` and
  `Claude`. The repository name `kit-scratch` may appear.

**Behaviour once on `main`:** GitHub shows the file as the Contributing tab and the
sidebar link, and links it from the new-issue and new-pull-request pages. This is
observable only on the default branch, so it is proved at handoff, not in prototype.

## Contract C2: the README pointer (MAX-46)

**Consumers:** readers of `README.md`, and C1's file through the link.

**Shape:**
- `README.md` gains one new last paragraph: a blank line, then exactly one sentence.
- The sentence holds exactly one Markdown inline link, `[text](target)`. Its target is
  exactly `CONTRIBUTING.md`: relative, with no scheme, leading slash or `./`.
- The sentence says what the link holds, using the word "checklist", so a reader knows
  why to follow it.
- The file still begins with `# kit-scratch` and ends with a single newline.

**Unchanged lines:** every line before the new paragraph is byte-identical to the base.
On this branch the base is `README.md` at commit 7133948, which is the MAX-16 rewrite.
This is proved by diff at verification, not by a check module, because the base differs
on each branch the sentence lands on.

**Link resolution:** GitHub resolves a relative link in `README.md` against the
repository root, so the link opens `CONTRIBUTING.md` on the same branch. C2 does not
require the target to exist; the integration proof does.

## Contract C3: the setup record (integration)

- **Result:** after the README edit, the setup check prints FRESH and exits 0. The
  command is `node "<kit root>/scripts/setup-runtime.js" gate --root "." --policy
  blocking`.
- **Writer:** only setup writes `.ai-delivery/stack-fingerprint`. The orchestrator runs
  a setup re-run in the main session; the kit's write guard refuses the same write from
  any subagent.
- **Side effects:** a setup re-run after a hash change runs full detection and may also
  update `.ai-delivery/conventions.md`, `.ai-delivery/config.md` dates and
  `docs/decisions.md`. Every change it makes is listed at integration. A change beyond
  README's hash and those records is reported to Max Adamsky rather than accepted
  silently.
- **Unaffected:** adding `CONTRIBUTING.md` and the checks does not change the setup
  record. No detection pattern matches that filename, and detection skips
  `.ai-delivery/` (checked against the kit's runtime, 2026-09-22).

## Contract C4: the acceptance checks

**Location:** `.ai-delivery/features/pull-request-checklist/checks/`, one module per
unit:

| Module | Unit | Reads |
|---|---|---|
| `test_contributing.py` | MAX-45 | `CONTRIBUTING.md` |
| `test_readme_link.py` | MAX-46 | `README.md` |
| `test_checklist_reachable.py` | integration | `README.md`, then the file its link names |

No `__init__.py`, no `conftest.py`, and no shared helper module. A shared file would
join the two units, so each module carries its own small parsing helper.

**Command:** from the repository root,
`PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib .ai-delivery/features/pull-request-checklist/checks/`,
or with one module's path in place of the directory. The two options keep a check run
from writing bytecode or cache files into the tree. A plain `uv run pytest` from the root
still exits with code 5.

**Behaviour:**
- **Inputs:** the repository root, resolved from the module's own location (the
  directory four levels above the checks directory). The checks read no environment
  variables and run no network, subprocess or git calls.
- **Output:** a pass or fail per test function. Each function checks one criterion.
- **Failure messages:** each names the failed criterion and quotes the offending line or
  text, following the conventions' rule that errors name the failing condition.
- **Dependencies:** the standard library only. No new dependency is added.
- **Quality:** every function is annotated and carries a docstring; ruff, ruff format and
  mypy are clean on the directory.

**Error taxonomy.** These are the ways a document can fail its contract. Each check's
failure message names one of them:

| Condition | Meaning | Raised by |
|---|---|---|
| MissingDocument | the file is absent at the root | all three modules |
| TitleMissing | the first line is not the expected level-1 heading, or a second one exists | `test_contributing.py`, `test_readme_link.py` |
| FileEnding | the file does not end with exactly one newline | `test_contributing.py`, `test_readme_link.py` |
| IntroductionCount | not exactly one sentence between the title and item 1 | `test_contributing.py` |
| IntroductionNotToolNeutral | the introduction does not say the items apply whichever tool is used | `test_contributing.py` |
| ItemCount | not exactly five items numbered 1 to 5 in order | `test_contributing.py` |
| ItemContent | an item lacks its leading verb or a phrase its row in C1 requires | `test_contributing.py` |
| RuleSentenceCount | an item's rule is not exactly one sentence | `test_contributing.py` |
| ExampleCount | an item has no example, or more than one | `test_contributing.py` |
| LengthOutOfRange | the file is outside 24 to 36 lines | `test_contributing.py` |
| ExcludedTopic | an out-of-scope topic or a kit reference appears | `test_contributing.py` |
| TrailingContent | anything follows item 5 | `test_contributing.py` |
| PointerSentenceCount | README's last paragraph is not exactly one sentence | `test_readme_link.py` |
| LinkTargetMismatch | no link, several links, or a target other than `CONTRIBUTING.md` | `test_readme_link.py` |
| PointerUnlabelled | the sentence does not say that the link holds the checklist | `test_readme_link.py` |
| UnresolvedLink | the link's target is not a file at the root holding the checklist | `test_checklist_reachable.py` |

StaleSetupRecord, the setup check reading STALE, is proved by the setup check's own
output at integration, not by a module. A module would have to hard-code the kit's
install path or its record format.

**Sentence counting**, used by IntroductionCount, RuleSentenceCount and
PointerSentenceCount: a sentence ends at `.`, `?` or `!` followed by whitespace or the
end of the text. Full stops inside backtick code spans and inside a link's target do
not count, so `CONTRIBUTING.md` and `uv run pytest` never end a sentence.

## Integration points

| System | What it does with this feature | Failure and handling |
|---|---|---|
| GitHub | Renders both files; surfaces `CONTRIBUTING.md` from the default branch | Nothing shows until the files reach `main` (question 3, handled at handoff) |
| The kit's setup check | Hashes `README.md` | Reads STALE after the edit until the setup re-run (C3) |
| Ship, the kit's pull request skill | Suggests a branch, description and link that miss items 1, 4 and 5 | The tool-neutral introduction (question 1); residual misses show in the success count |
| MAX-16 to MAX-18, the README issues in the Repository usage documentation project | Edit the same `README.md` | This branch already carries MAX-16; ordering on `main` is settled at handoff (question 3) |
| The first test module, when it lands | Makes item 3's "exit code 5" false | Item 3 is rewritten then (question 8); the checks stay out of the default run meanwhile |

**This feature depends on:** GitHub's documented handling of a root `CONTRIBUTING.md`,
the kit's setup runtime for the FRESH proof, and uv with pytest for the checks.

**Depending on this feature:** contributors, who follow the checklist; MAX-16 to MAX-18,
which rebase onto the README sentence on `main`; and the success count, which reads
review comments against items 1, 2, 4 and 5.

## Testing strategy

**Test-first order.** Each unit's check module is written first and fails, because its
document or sentence does not yet exist. The document is then written until the module
passes. The integration module is written before the setup re-run, and fails until the
re-run is done and both units have landed.

**Unit checks.** Cases, as bullets; the specs expand them.
- `test_contributing.py`: the file exists at the root; one level-1 title first; exactly
  one introductory sentence, saying the items apply whichever tool is used; exactly five
  items, numbered 1 to 5; each item starts with its leading verb and carries its row's
  required phrases; each rule is one sentence; each item has exactly one example; item
  1's example is a `handle/topic` branch not starting with `codex/`; item 4's example has
  two or three sentences in one paragraph; item 5's example is a `#<number>` reference
  with no closing keyword; 24 to 36 lines; no excluded topic or kit reference; nothing
  after item 5.
- `test_readme_link.py`: the file starts with `# kit-scratch`; its last paragraph is one
  sentence; it holds exactly one link, whose target is exactly `CONTRIBUTING.md`; the
  sentence mentions the checklist; the file ends with one newline.

**Integration checks.** `test_checklist_reachable.py` follows README's last link to a
file at the root, and finds that file's title and five numbered items. Evidence that
runs alongside it, rather than inside a module:
- the setup check prints FRESH;
- `git diff 7133948 -- README.md` shows only added lines at the end;
- a plain `uv run pytest` still prints "no tests ran" and exits with code 5.

**Contract checks.** C2's link target and C1's location are one contract: the
integration module is its consumer-side check.

**Coverage.** It does not apply. The feature adds no source module, and the coverage
gate measures `src/`, which does not exist.

**Load and performance.** They do not apply: static documents, no runtime.

**End-to-end journeys:**
1. A reader of `README.md` follows its last sentence's link and lands on a checklist with
   five items.
2. A contributor runs item 3's command and sees exactly what item 3 says: "no tests ran",
   exit code 5.
3. A kit session opened after integration passes the setup check, which reads FRESH.
4. Once the files are on `main`, the repository page shows the Contributing tab and
   sidebar link. This is proved at handoff or in the Validate stage, not in prototype,
   because it needs question 3's answer.

This document surfaced nothing requiring a decision or an action beyond the open
questions `1a-discovery.md` lists with their owner.
