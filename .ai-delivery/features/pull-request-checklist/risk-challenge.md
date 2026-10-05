# Risk Challenge: pull-request-checklist — One root CONTRIBUTING.md plus a one-line README pointer

**Created:** 2026-09-22
**Source:** single-perspective risk pass (one subagent), **not fresh-context** (see Independence below)
**Direction assessed:** One root CONTRIBUTING.md plus a one-line README pointer (Direction A in exploration-synthesis.md)

> One careful pass, one perspective. The issues surfaced here are real signals, but this is
> not complete coverage.

This document records what one reviewer found could go wrong with the chosen direction: a
root CONTRIBUTING.md and a one-line README pointer for the repository's first outside
contributors. Its purpose is to have requirements written with these risks in view. Several
of them go to the heart of the direction.

**Independence.** The kit requires this pass to see the risk brief and nothing else. The
reviewer ran as a general-purpose agent with every tool, and it used 33 tool calls before
writing. It read this feature's framing, exploration synthesis and Q&A log, the repository's
kit configuration, and the kit's ship and setup skills. It also queried GitHub's settings
for this repository, and its response says all this itself. As a result, its overlaps with
council findings are **not** independent re-finds, and no risk below carries the
"independently re-found" signal. On the other hand, most of its claims rest on checks
rather than opinion. The orchestrator re-verified the load-bearing ones, as noted under each
risk, and found the workspace unchanged afterwards.

**Reading the codes.** Codes name exploration findings recorded in exploration-synthesis.md:
- `STR`: the stress member, which reasoned from the framing only.
- `NUL`: the null member, which also reasoned from the framing only.
- `OPR`: the operator member, which read the repository.
- `PRE`: the precedent member, which searched the web.

---

## Critical Risks (High Likelihood × High Impact)

### The kit's own pull request workflow contradicts the checklist
- **Category:** Assumption
- **Description:** The outside contributors are the kit's first users. This repository
  exists so that its branches and pull requests show what the kit produces, so these
  contributors will likely open pull requests with the kit's ship skill. Ship's defaults
  contradict three of the four items the threshold counts:
  - **Branch:** without Linear access, which these contributors lack, it suggests a
    `feat/{feature-name}` branch, not `<GitHub handle>/<short topic>`.
  - **Description:** it writes a multi-section pull request body, not one paragraph.
  - **Issue link:** it links Linear issues, not a GitHub issue.

  A fourth item is unsettled. Ship makes one commit per unit, and whether that meets "one
  commit per change" depends on what that phrase means. The direction excludes both ways to
  reconcile the guide with the kit: it changes nothing in the kit, and the guide says
  nothing about how the kit works. So contributors must choose between the guide and the
  tool they came to test. The threshold would then measure that conflict, not the guide.
- **Likelihood:** High
- **Impact:** High
- **Mitigation signal:** Before writing, decide whether a pull request exactly as ship
  produces it meets the standard. If it does not, decide whether the guide may say how to
  override ship's branch suggestion and pull request body. To check, run ship once on a
  throwaway change from an account without access to team MAX.
- **Verified by the orchestrator:**
  - Ship's SKILL.md suggests `feat/{feature-name}` when Linear is unavailable (line 98).
  - It groups commits one per unit.
  - It opens the pull request with `gh pr create` and a body divided into sections.
  - This repository's three existing pull requests have bodies of 2,886 to 4,114
    characters in 4 to 6 sections. They reference Linear and reference no GitHub issue.
- **Found by:** risk-pass. It is not independent, and it touches PRE-2 on agent branch
  prefixes.

---

## Significant Risks

*(Medium likelihood or impact. Worth addressing before requirements.)*

### The guide must reach `main`, and nothing here reaches `main`
- **Category:** Timing
- **Description:** GitHub's repository page, Contributing tab and sidebar show the default
  branch, `main`. `main` has not changed since 2026-08-28:
  - The working branch is 19 commits ahead and has never been pushed.
  - No pull request has ever merged.
  - The three open pull requests are drafts aimed at other branches.

  Copying only the guide onto `main` does not work either:
  - `main` has no `pyproject.toml` or `uv.lock`, so item three's command fails there in a
    different way. The pass reports "Failed to spawn: pytest" with exit code 2.
  - `main`'s README still describes a scratch repository for kit 1.7.0.
  - `main`'s kit configuration names a different Linear team.

  Fast-forwarding `main` would land 19 unreviewed commits. That is a decision about what
  `main` is for, and the scope does not cover it.
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation signal:** Define "in place" in the timing criterion as "on `main` on GitHub,
  with `pyproject.toml` and `uv.lock` there too". Decide how `main` catches up before
  writing.
- **Verified by the orchestrator:**
  - `main` and `origin/main` are both at 1932d82, from 2026-08-28.
  - The working branch is 19 commits ahead and has no upstream.
  - `main` has 0 merge commits.
  - `main` holds only `.ai-delivery`, `.gitignore`, `README.md` and `docs`.
  - `main`'s README says "Scratch repository for verifying ai-delivery at 1.7.0", and its
    config records `greenfield: true` and team CDR.

  The exit-code-2 result on a clean copy of `main` was not re-run.
- **Found by:** risk-pass. It extends the synthesis's note that a pull request template
  takes effect only on the default branch.

### Item five asks for a GitHub issue this repository has never had
- **Category:** Organizational
- **Description:** No GitHub issue has ever been filed here, and all work lives in Linear
  team MAX. A contributor who reaches item five has nothing to link until they file an
  issue at pull request time. That satisfies the item but not the need behind it, which is
  a link to "the issue the work came from". The maintainer then runs two trackers and
  matches each GitHub issue to Linear by hand at review. That is a new chore on every pull
  request, for the person the guide is meant to relieve. Meanwhile, GitHub issues pile up
  where the kit's triage never looks.
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation signal:** Decide who files the GitHub issue for a contributor's work, and
  whether that happens before the branch exists. Decide who triages GitHub issues.
- **Verified by the orchestrator:** issues are enabled, and `gh issue list --state all`
  returns none.
- **Found by:** risk-pass. It overlaps STR-2 and OPR-3, and the overlap is not independent.

### Using the kit here changes shared files that the five items do not cover
- **Category:** Scope
- **Description:** Kit skills refuse to run until setup has run. Setup rewrites shared,
  committed files and appends to `docs/decisions.md`. The rewritten files are:
  - `.ai-delivery/config.md`, which names Linear team MAX
  - the conventions file
  - the gates file
  - the rubrics file
  - the stack fingerprint

  A contributor who uses the kit here therefore opens a pull request that also rewrites
  shared configuration. That puts several unrelated changes in one pull request, which is
  exactly what item two exists to stop. Contributors working in parallel will also conflict
  on `config.md` and `docs/decisions.md`. None of the five items says which files a pull
  request may touch. So either that becomes a sixth review comment repeated to every
  contributor, or the guide grows past five items. The repository is also public and has
  no LICENSE file, and the first outside contribution will raise that.
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation signal:** Before writing, decide whether contributor pull requests may
  change `.ai-delivery/` and `docs/decisions.md`, and whether saying so counts as
  describing the kit.
- **Verified by the orchestrator:** the repository is public, and it has no LICENSE,
  CLAUDE.md or AGENTS.md. The claim that setup runs rewrite these files rests on the pass's
  reading of commits 9dfa787, 501e468 and 711a402. Commit 501e468 was confirmed earlier to
  touch config.md, conventions.md and docs/decisions.md.
- **Found by:** risk-pass.

### The threshold can pass or fail for reasons unrelated to the guide
- **Category:** Assumption
- **Description:** The threshold can mislead in four ways:
  - **Learning:** with two to five contributors, only each contributor's first pull
    request tests the guide. Later pull requests measure what review has taught them.
  - **Silent fixes:** the count is of comments, so a miss that is fixed without a comment
    never registers. That covers a squash merge, which is enabled here, a description
    edited in place, and a link the maintainer adds at review.
  - **Self-judging:** one person writes the guide, reviews every pull request, decides
    what counts, keeps the count and reads the verdict.
  - **No end date:** "the first ten" pull requests may take an unknown time to arrive.
- **Likelihood:** High
- **Impact:** Medium
- **Mitigation signal:** Before the first outside pull request, decide three things:
  - whether each contributor's first pull request is reported separately
  - whether a miss fixed without a comment still counts
  - by what date the verdict is read, even if fewer than ten pull requests have arrived
- **Verified by the orchestrator:** squash merge is allowed on the repository.
- **Found by:** risk-pass. It overlaps STR-4, NUL-3, NUL-5 and OPR-5, and the overlap is
  not independent.

### Item three teaches that "no tests ran" is fine
- **Category:** Technical
- **Description:** Once tests exist, exit code 5 means pytest collected nothing. That is
  the silent failure the kit's own conventions record treats as a correctness problem,
  because misnamed test files are skipped. The first contributor to add a test can misname
  it, see "no tests ran", and take it as the result the guide promised. The sentence also
  goes stale when the first test module lands, and nothing ties its rewrite to that event.
- **Likelihood:** Medium
- **Impact:** Medium
- **Mitigation signal:** Make rewriting item three an acceptance criterion of whichever
  feature lands the first test module. Decide how a contributor can tell "no tests exist
  yet" apart from "my tests weren't collected".
- **Verified by the orchestrator:** the Testing Conventions in conventions.md state that a
  test file missing the discovery patterns "is silently not collected".
- **Found by:** risk-pass. It builds on OPR-1 and OPR-4, and the overlap is not
  independent.

---

## Watch Items

None. The pass rated no risk Low on likelihood or impact.

---

## Unstated Assumptions

| Assumption | Consequence if Wrong | Checked by the orchestrator |
|------------|---------------------|-----------------------------|
| Newcomers visit GitHub's web pages before they start work | Kit users work in a terminal, and ship opens pull requests with `gh pr create`, which never loads the new-pull-request page. The Contributing tab, the sidebar link and the new-issue page are all off that path. That leaves one README sentence, and nothing points an agent at the guide | Ship's use of `gh pr create` is verified. How the contributors will actually work is not |
| A one-line README edit has no side effects | README.md's hash is recorded in the kit's setup fingerprint, so the edit makes setup stale. Every kit skill that checks setup then stops until setup re-runs. That lands during the kit's release window, and in front of contributors unless the refreshed fingerprint is committed with the pointer. Setup also reads contributing guides as a source of conventions, so a later setup run may copy the five items into the kit's conventions record | **Verified.** On a local clone, the setup gate reads FRESH before the edit and STALE ("file changed README.md") after it, committed or not. Setup's SKILL.md lists contributing guides among the project documents it reads |
| The three README edits are still queued behind the pointer | MAX-16's README rewrite is already built. It is commit 890dea8 on the working branch and the only commit in draft pull request #3, so going "ahead of the queue" means rebasing finished work. On `main`, the pointer would sit under the old 1.7.0 README that MAX-16 replaces. The pass's scratch rebase conflicted on README.md | Commit 890dea8 is verified on this branch and on PR #3's branch, while Linear still shows MAX-16 as Backlog. The rebase conflict was not re-run |
| Outside contributors can reach `main` only through a reviewed pull request | `main` has no branch protection and no rulesets, and the maintainer is the only collaborator. A contributor given write access could push straight to `main`, which skips all five items and the count | **Verified.** The branch-protection query returns 404, there are 0 rulesets, and there is one collaborator |

---

## Top Concern

This is a close paraphrase of the pass's top concern. The guide is written for people who
assemble their own pull requests. The people arriving are the kit's first users, in a
repository whose branches and pull requests exist to show what the kit produces. Ship's
defaults contradict three of the four counted items: they produce a `feat/…` branch name, a
multi-section description, and a Linear link instead of a GitHub issue. A fourth depends on
how "one commit per change" is settled. The direction rules out both ways to reconcile the
guide with the kit. So contributors will likely follow the tool they came to test, and the
same review comments will return. The threshold would then call the guide a failure, when
what it measured was a disagreement between the guide and the kit that no contributor could
resolve. Until someone decides whether a pull request exactly as ship produces it meets the
standard, the guide forces the kit's first users to choose between the two.

---

## Decisions This Surfaces

Max Adamsky owns all of these, as maintainer and project lead:
- Decide whether a pull request exactly as ship produces it meets the standard. If it does
  not, decide whether the guide may say how to override ship.
- Decide how and when `main` receives the guide, and what "in place" means in the timing
  criterion.
- Decide who files the GitHub issue a contributor links, and who triages GitHub issues.
- Decide whether contributor pull requests may change `.ai-delivery/` and
  `docs/decisions.md`.
- Decide how the README pointer and the refreshed setup fingerprint land together, and how
  the pointer relates to MAX-16's already-built rewrite.
- Settle three threshold details: whether first pull requests are reported separately,
  whether silent fixes count, and a date for the verdict.
- Decide what triggers the rewrite of item three once tests exist.
