## Council Response

**Evidence consulted:** /Users/maxdamsky/Projects/kit-scratch/README.md, /Users/maxdamsky/Projects/kit-scratch/pyproject.toml, /Users/maxdamsky/Projects/kit-scratch/.gitignore, /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/conventions.md, /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/gates.md, /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/config.md, /Users/maxdamsky/Projects/kit-scratch/docs/decisions.md, /Users/maxdamsky/Projects/kit-scratch/.ai-delivery/features/pull-request-checklist/qa-log.md (lines 140-237). I also listed the directory tree: there is no `src/`, no `tests/` and no `.github/`, and the local branches are under `.git/refs/heads/`.

### Direction 1: One Root CONTRIBUTING.md Plus a One-Line README Pointer

**Approach Summary**
Add one new file, `/Users/maxdamsky/Projects/kit-scratch/CONTRIBUTING.md`, of about 30 lines. It holds the five items, and each item is one imperative sentence followed by one concrete example. Take the test item's command from `.ai-delivery/gates.md` § Test (`uv run pytest`). Take the branch-name example from the pattern the existing branches already follow, `<prefix>/<topic>-<issue-number>` (for example, `codex/w70-triage-115-001`), rather than inventing a new scheme. Add one sentence to the end of `/Users/maxdamsky/Projects/kit-scratch/README.md` that points to it. GitHub already shows a root CONTRIBUTING.md on the new-pull-request and new-issue pages, so a newcomer sees it before starting, with no new tooling. Do not edit, copy from or link to `.ai-delivery/conventions.md`. It covers none of the five items and is written for the kit's skills.

**Key Trade-offs**

| Gain | Cost |
|------|------|
| This is the ordinary open-source form, so the test bed stays representative | Adds one new file, and someone has to keep it current |
| GitHub shows it with no configuration, before the work starts | Only people who arrive through GitHub are prompted; a local clone gets just the README pointer |
| Reuses the command already recorded in gates.md instead of writing a new one | If gates.md changes, the command in CONTRIBUTING.md goes stale, because nothing links the two |

**Risks**
- **"Tests run locally" has nothing to run:** there is no `tests/` directory, so `uv run pytest` collects nothing and exits with code 5. A newcomer will read that as a broken setup. The file has to say that "no tests collected" is expected until the first test module exists, or the item will create the very questions it is meant to remove.
- **The issue to link may be one contributors cannot see:** work is tracked in the Linear team MAX (`config.md` § Linear), which is a private test workspace. If outside contributors cannot open Linear, the linked-issue item cannot be met. *Assumption:* contributors link a GitHub issue on this repository's origin, and the maintainer mirrors it to Linear. The maintainer must confirm this before the file ships.
- **There is no branch convention to write down yet:** the existing branches mix `codex/...-001` names with `live-proof-2026-09-21`. The document has to state one rule, and only the maintainer can choose it.

**Estimated Complexity**
`Low`: one new file of about 30 lines plus one added sentence, with no code, configuration or dependency changes. Most of the work is the three decisions listed under Risks, not the writing.

### Direction 2: A "Contributing" Section Inside README.md, No New File

**Approach Summary**
Put the same five items and the same `uv run pytest` line in a short section at the end of `/Users/maxdamsky/Projects/kit-scratch/README.md`, instead of in a new file. That adds no files, and the README is the first page anyone opens on GitHub or in a clone.

**Key Trade-offs**

| Gain | Cost |
|------|------|
| No new file | GitHub does not show a README section on the new-pull-request page, so the prompt at the moment of starting is lost |
| Every visitor sees it, including those who clone locally | Makes the README longer, when its current job is to say what the fixture is for |

**Risks**
- **Clash with README work already scoped:** the repository-usage-documentation feature splits README.md into three units (MAX-16, MAX-17, MAX-18) that are built one after another because they share the file (`docs/decisions.md`, 2026-09-12). A fourth section would join that queue.
- **Less representative:** real projects keep contribution rules in CONTRIBUTING.md, and the constraints ask the test bed to stay ordinary.

**Estimated Complexity**
`Low`: one edit to an existing file. The same three decisions are still needed.

## What Already Exists

- `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/gates.md` § Test: `uv run pytest` is the recorded test command, so the test item needs no new command.
- `/Users/maxdamsky/Projects/kit-scratch/pyproject.toml`: pytest is already in the dev group, and uv installs it on first `uv run`, so contributors need no setup step beyond having uv.
- `/Users/maxdamsky/Projects/kit-scratch/.git/refs/heads/`: the existing branches (`codex/handoff-setup-001`, `codex/w70-triage-115-001`) already show an unwritten branch-naming pattern that the document can adopt.
- `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/conventions.md` § Linear Conventions, "Titles: short imperative phrases naming the outcome": the issue-title rule can be reused as the rule for the first line of a pull request description and for the topic part of a branch name.
- `/Users/maxdamsky/Projects/kit-scratch/README.md`: it already tells readers that the repository's branches and pull requests are kept as worked examples, which gives the five items their reason.
- `/Users/maxdamsky/Projects/kit-scratch/.ai-delivery/conventions.md` lines 40-44: this already says that anything added must serve the purpose of exercising the kit, and a contributing guide does.

## Strongest Statement

Writing the file is a 30-minute job. What could make it fail is three decisions that only the maintainer, Max Adamsky, can make: which branch pattern is the rule, which tracker outside contributors link to (Linear team MAX is probably closed to them), and how the document explains that `uv run pytest` currently collects no tests. If those are left open, the document produces exactly the questions it is meant to remove. Settle all three before writing, then ship Direction 1: one root CONTRIBUTING.md and a one-line pointer in README.md.

**END OF RESPONSE. Do not add anything after this line.**
