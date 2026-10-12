## Evidence note (read before the council cross-reference)

This was not a fresh-context pass, and no match below should count as an independent re-find. The kit's `02b-risk-challenge.md` says this pass works from the brief alone. I read that file only after I had already read this feature's `framing.md`, `exploration-synthesis.md` (which summarises the council's findings) and `qa-log.md`. I also read `README.md`, `pyproject.toml`, `.ai-delivery/{config,conventions,gates}.md`, `.ai-delivery/stack-fingerprint` and parts of `docs/decisions.md`, and saw a truncated preview of the constraint member's response.

I also ran read-only checks. I queried GitHub (settings, issues, pull requests, branch protection), read `main` with git, and ran `uv run pytest` and a rebase test on scratch copies. I read the kit 3.0.0 ship and setup skills and fetched GitHub's contributor-guidelines page. Nothing was written to the workspace. Paths are relative to `/Users/maxdamsky/Projects/kit-scratch`.

Where the risks overlap the council:
- Risk 3 overlaps STR-2 and OPR-3.
- Risk 5 overlaps STR-4, NUL-3, NUL-5 and OPR-5.
- Risk 6 builds on OPR-1 and OPR-4.
- Assumption D builds on STR-3, and the agent-branch point in Risk 1 touches PRE-2.
- Risk 2 extends a remark the synthesis made only about the template: it takes effect once merged to the default branch.

Risks 1, 2 and 4 and Assumptions A to C otherwise rest on checks the synthesis did not make. For an unanchored pass, re-dispatch with an explicit instruction not to read the workspace.

---

## Risk Challenge Output

### Risks

**Risk 1: The kit's own output breaks the checklist**
- **Category:** Assumption
- **Description:** The checklist assumes contributors write their own branch names, commits and descriptions. The brief doesn't say how contributors will produce pull requests. But they are the kit's first users, and the README says this repository's branches and pull requests exist to show what the kit produces. The kit 3.0.0 ship skill's defaults conflict with the checklist:
  - **Branch:** it suggests `feat/{feature-name}` whenever Linear is unavailable, which is always the case for contributors. It never suggests `<GitHub handle>/<short topic>`.
  - **Commits:** it splits work into several conventional commits: one per unit, plus docs and chore commits. Whether that meets item 2 depends on how "one commit per change" is settled.
  - **Description:** it writes a multi-section body, not one paragraph.
  - **Issue link:** it links Linear issue IDs, not a GitHub issue.

  The three pull requests already here, which the README calls worked examples, show the same pattern. All were generated with Claude Code. Each is 2,896 to 4,118 characters long with 4 to 6 sections, links one Linear issue and references no GitHub issue. No kit skill reads CONTRIBUTING.md when opening a pull request; only setup reads contributing guides. The repository has no CLAUDE.md or AGENTS.md. The direction also rules out both levers that could reconcile the guide and the kit: it makes no kit changes and says nothing about how the kit works. "Reserved for agent branches" is also undefined for people who drive an agent, which describes everyone arriving.
- **Likelihood:** High
- **Impact if realized:** High
- **Mitigation signal:** Decide before writing whether a pull request exactly as ship produces it meets the standard. If it does not, decide whether the guide may say how to override ship's branch suggestion and body. To check, run ship once on a throwaway change from an account without access to team MAX, and compare its branch, commits, body and link with the five items.

**Risk 2: The guide has to be on `main`, and nothing here reaches `main`**
- **Category:** Timing
- **Description:** The rationale depends on the default branch. The repository page, where the Contributing tab and sidebar link appear, shows `main`. GitHub's docs don't say which branch the file must be on. But `main` on GitHub hasn't changed since 2026-08-28:
  - `live-proof-2026-09-21` is 19 commits ahead of `main` and has not been pushed.
  - No pull request has ever been merged, and `main` has no merge commits.
  - All three open pull requests are drafts that target other `codex/` branches, not `main`.
  - Ship's handoff workflow states that a handoff "does not authorize merging".

  If the guide ships the way work usually ships here, GitHub shows it nowhere. Copying only the two files onto `main` doesn't work either:
  - `main` has no `pyproject.toml` or `uv.lock`. On a clean copy of `main`, `uv run pytest` fails with "Failed to spawn: `pytest`" and exit code 2, not the exit 5 that item 3 promises.
  - `main`'s README still says "Scratch repository for verifying ai-delivery at 1.7.0."
  - `main`'s kit config still records a greenfield project and Linear team CDR.

  Fast-forwarding `main` instead lands 19 commits of unreviewed test-bed state. That is a decision about what `main` is for, and the MVP scope doesn't cover it.
- **Likelihood:** Medium
- **Impact if realized:** High
- **Mitigation signal:** Define "in place" in the timing criterion as "on `main` on GitHub, with `pyproject.toml` and `uv.lock` also there". Choose how `main` catches up before writing. To check, open the repository page and the new-issue page while signed out, and run item 3 on a fresh clone of `main`.

**Risk 3: Item 5 asks for a GitHub issue this repository has never had**
- **Category:** Organizational
- **Description:** Issues are enabled, but no GitHub issue has ever been filed; the three open items GitHub counts are the pull requests. All work is tracked in Linear team MAX. A contributor reaching item 5 therefore has nothing to link until they file an issue at pull request time. That satisfies the checklist but not the framing's actual need, a link to "the issue the work came from". The maintainer then runs two trackers, matching each contributor's GitHub issue to Linear by hand at review. That is a new chore on every pull request, for the one person the guide is meant to relieve. The GitHub issues also build up where the kit's triage never looks, because triage works from Linear's Triage inbox. The branch rule is justified as "the guide describes what is done in this repository", but item 5 describes something never done here.
- **Likelihood:** High
- **Impact if realized:** Medium
- **Mitigation signal:** Decide who files the GitHub issue for a contributor's work, and whether that happens before the branch exists rather than at pull request time. Decide who triages GitHub issues. Filing issues in advance for the work contributors will pick up shows whether two trackers are sustainable.

**Risk 4: Kit runs change shared files that the five items don't cover**
- **Category:** Scope
- **Description:** Twelve kit skills refuse to run until setup has run. Setup runs here rewrite shared, committed files (commits 9dfa787, 501e468 and 711a402):
  - `.ai-delivery/config.md`, which names Linear team MAX
  - `.ai-delivery/conventions.md`
  - `.ai-delivery/gates.md`
  - `.ai-delivery/rubrics.md`
  - `.ai-delivery/stack-fingerprint`
  - `docs/decisions.md`, which each run appends to

  A contributor who uses the kit here, whether in their own Linear workspace or without one, opens a pull request that also rewrites shared configuration. That is several unrelated changes in one pull request, the very problem item 2 addresses. With two to five contributors working in parallel, those pull requests will conflict on `config.md` and `docs/decisions.md`. None of the five items covers this, and the direction excludes "anything about how the kit itself works". So "which files may my pull request touch?" becomes a sixth repeated review comment, answered one contributor at a time. Alternatively, the guide grows past five items within the first few pull requests. The repository is also public with no LICENSE file, so the first outside contribution raises a question about contribution terms that the guide doesn't answer.
- **Likelihood:** High
- **Impact if realized:** Medium
- **Mitigation signal:** Decide before writing whether contributor pull requests may change `.ai-delivery/` and `docs/decisions.md`, and whether saying so counts as describing the kit. To check, have someone without access to team MAX clone the repository, run setup, and inspect `git status`.

**Risk 5: The threshold can pass or fail for reasons unrelated to the guide**
- **Category:** Assumption
- **Description:** The threshold can mislead in three ways:
  - **Learning:** with two to five contributors, ten pull requests means two to five each. A contributor stops repeating a mistake after one review comment. Only each contributor's first pull request tests the guide, at most two to five of the ten; the rest measure what review taught them.
  - **Silent fixes:** the count is of comments. The direction already has the maintainer adding links at review, and squash merge is enabled. A fixed commit history or a description edited in place is a miss that produces no comment.
  - **Self-judging:** one person writes the guide, reviews every pull request, decides what counts as a comment asking for an item, keeps the count and reads the verdict.

  "The first ten outside pull requests" has no end date, so the verdict may arrive long after the decisions that depend on it.
- **Likelihood:** High
- **Impact if realized:** Medium
- **Mitigation signal:** Before the first outside pull request, decide three things. Is each contributor's first pull request reported separately? Does a miss fixed without a comment still count as a miss? By what date is the verdict read, even if fewer than ten pull requests have arrived?

**Risk 6: Item 3 teaches contributors that a failing result is expected**
- **Category:** Technical
- **Description:** The guide tells contributors that "no tests ran" (exit code 5) is the expected result. Once tests exist, exit code 5 means pytest collected nothing. `.ai-delivery/conventions.md` itself calls test-file naming a correctness rule, because files outside the `test_*.py` and `*_test.py` patterns are silently skipped. The first contributor to add a test can misname the file, see "no tests ran", and take it as the result the guide promised. The shaped features, such as folder summary and text preview, are the likely source of that first test. The sentence also goes stale when the first test module merges, and nothing ties its rewrite to that event.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** Make rewriting item 3 an acceptance criterion of whichever feature lands the first test module. Decide how a contributor can tell "no tests exist yet" from "my tests weren't collected".

### Top Concern

**What is the single biggest risk in this direction?**
The guide is written for people who put together their own pull requests by hand. The people arriving are the kit's first users, and the README says this repository's branches and pull requests exist to show what the kit produces. Ship's defaults conflict with three of the four items the threshold counts: a `feat/…` branch name, a multi-section description, and a Linear link instead of a GitHub issue. A fourth depends on how "one commit per change" is settled, since ship makes several conventional commits. The three pull requests already here, all generated with Claude Code, have multi-section bodies and Linear links. The direction rules out both ways to reconcile the guide and the kit, since it changes nothing in the kit and says nothing about how the kit works. The likely result is that contributors follow the tool they came to test and the same review comments return. The threshold will then say the guide failed, when it has really measured a disagreement between the guide and the kit that no contributor could resolve. Until someone decides whether a pull request exactly as ship produces it meets the standard, the guide makes the kit's first users choose between the guide and the kit.

### Unstated Assumptions

- **Assumption:** Newcomers visit GitHub's web pages before they start work.
  **Why it matters if wrong:** Kit users work in a terminal. They clone, run setup, and let ship open the pull request with `gh pr create`, which never loads the new-pull-request page. The Contributing tab, the sidebar link and the new-issue page are all off that path. That leaves one sentence at the end of the README, and nothing in the repository points an agent at the guide.
- **Assumption:** A one-line edit to README.md has no side effects.
  **Why it matters if wrong:** README.md's SHA-256 is recorded in `.ai-delivery/stack-fingerprint`, and it matches today's file. After the edit, setup's check reports the setup as stale, and twelve kit skills refuse to run until setup runs again. That happens during the kit's release window, and in front of contributors if the refreshed fingerprint isn't committed together with the pointer. Setup also reads contributing guides as tier-`1-code` conventions, so a later run may copy the five items into `.ai-delivery/conventions.md`. That would be a second, generated copy that has to stay in step with the guide.
- **Assumption:** The three README edits are still queued behind the pointer.
  **Why it matters if wrong:** MAX-16's rewrite is already built. It is commit 890dea8 on the working branch and the only commit in draft pull request #3, so "ahead of the queue" means rebasing finished work. On `main`, the pointer would go under the three-line README ending "…verifying ai-delivery at 1.7.0.", which is the line MAX-16 replaces. A scratch rebase of the pointer onto MAX-16's commit conflicts on README.md.
- **Assumption:** Outside contributors can reach `main` only through a reviewed pull request.
  **Why it matters if wrong:** A handle prefix separates branch names, which only matters if contributors push to this repository, and that needs write access. `main` has no branch protection or rulesets, and the maintainer is currently the only collaborator. Any contributor given write access can push straight to `main`. Ship only warns before committing on `main`, and all nine commits on `main` were pushed directly, with no merges. A direct push skips all five items, and the threshold never counts it.
