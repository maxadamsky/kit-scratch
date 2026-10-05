# Discovery Brief: pull-request-checklist

*A discovery brief — the discover skill's handoff artifact.*

**Created:** 2026-09-22
**Topic:** pull-request-checklist
**Discover Session Status:** Completed
**Project:** P-MAX-12 Pull request checklist — https://linear.app/max-test-workspace/project/pull-request-checklist-08fae13de2f4
**Council:** constraint, precedent, stress, null, operator
**Discovery issues:** research: MAX-44 https://linear.app/max-test-workspace/issue/MAX-44/explore-directions-for-a-written-pull-request-standard

This brief hands requirements a written pull request standard for this repository: one
CONTRIBUTING.md at the root and a one-line pointer to it in the README. It matters because
two to five outside contributors, the delivery kit's first users, arrive within two weeks.
Without the standard, their first pull requests meet it only at review, after the work is
done. The decisions below are settled. The risks and open questions are not, and shape
should resolve them before requirements are final.

**Reading the finding codes in this document.** Claims below carry a short code naming the
exploration member that produced them:
- `CON` argued for the smallest change and read this repository.
- `PRE` searched the live web for things to adopt and could not see the repository.
- `STR` looked for how any direction breaks at 100 times the stated scale or under hostile
  input. It reasoned from the problem framing alone, with no tools.
- `NUL` argued that this should not be built. It also reasoned from the framing alone, with
  no tools.
- `OPR` read the repository's operational setup, meaning its CI, deployment and logging.
- `risk-pass` is a separate reviewer that examined the chosen direction.

The code matters because a claim from a member that could read the repository is a different
kind of statement from one made by a member that could not.

---

## 1. Problem Statement

Nobody opening a pull request against this repository has a written standard for what the
pull request must include. The conventions for branch names, commit scope, running the tests,
descriptions and issue links exist only in the maintainer's head. So far that has cost
little, because the maintainer is the only author and the only reviewer, and the five basics
that keep coming up come from a year of the maintainer's own review comments. Within two
weeks, when the kit ships, two to five outside contributors start opening pull requests here
without that context. The standard surfaces only at review, after the branch is named, the
commits are shaped and the description is written, so every miss means redoing finished
work, and the maintainer answers the same questions one contributor at a time. If nothing
changes, the kit's first users meet this repository through avoidable rework on their first
pull requests.

---

## 2. Who Is Affected

**Primary users:** the outside contributors. They are two to five people, the delivery kit's
first users. They know the kit from its README, have never worked in this repository, and do
not know its conventions. As the kit's first users, they are likely to open pull requests
through the kit itself. That is an assumption; see sections 10 and 13.

**Secondary stakeholders:** the maintainer, Max Adamsky. Today the maintainer is the only
person who opens and reviews pull requests here. Once the contributors arrive, the
maintainer holds the standard, answers the same questions, and keeps the count behind the
success measure. Nobody downstream reads the history yet.

**Scale:** one person now, up to six once the outside contributors arrive.

---

## 3. The Opportunity

A newcomer can open a pull request that meets the standard without asking the maintainer
first, because the standard is written where they will look before they start. The
maintainer stops writing the same five review comments and stops explaining conventions one
contributor at a time. The outcome that matters most is newcomers getting it right the first
time, because that is what removes the rework. Less review time follows from it.

---

## 4. Chosen Direction

**Direction:** One root CONTRIBUTING.md plus a one-line README pointer.

**What it is:**
A file of about 30 lines at the repository root. It states the five items, each as one
imperative sentence plus one example. A single sentence at the end of README.md points to
it. GitHub surfaces a root CONTRIBUTING.md without any configuration. It shows the file as a
Contributing tab and a sidebar link on the repository page, and links it from the new-issue
and new-pull-request pages. This repository is on GitHub.

**Why this direction:**
It puts the standard where GitHub already shows it to a newcomer. The repository page's
Contributing tab and sidebar link, and the link on the new-issue page, can all come before
work starts. The link on the new-pull-request page repeats it. A README section gets none of
those links. It is also the smallest change that fully answers the request: one file and one
pointer. No part of it first appears only after the branch and commits exist, as a pull
request template would.

---

## 5. What Was Considered and Not Chosen

Exploration surfaced the following directions. They were considered and not selected, for
the reasons noted.

| Direction | Why Not Selected |
|-----------|-----------------|
| A "Contributing" section inside README.md, no new file (CON-2) | GitHub gives only a CONTRIBUTING file the Contributing tab, the sidebar link, and the links from the new-issue and new-pull-request pages, so a README section gets none of them. It would also join the README edits already queued for the file |
| CONTRIBUTING.md plus a GitHub pull request template (PRE-1) | A template appears only after the branch and commits exist, and the problem arises before that moment. It is also a second file beyond the literal request |
| The published Conventional Branch standard for branch names (PRE-2) | The guide describes what is done in this repository, so the local pattern was chosen instead |
| A published contributing-guide skeleton as the starting point (PRE-3) | A weak fit. It covers none of the five items specifically and produces far more than a checklist, so it is kept only as a reference for shape |
| Do not build — wait until the first three outside pull requests have been reviewed, then decide from the record (NUL-6) | Declined. Waiting would put the timing failure on the kit's first users, and the five items come from a year of the maintainer's own review comments. Null's baseline point was adopted as the count criterion (section 8) |

*Note: "Not chosen" does not mean "wrong". Any of these may be a valid future phase, or worth
revisiting if constraints change.*

---

## 6. Key Trade-offs Resolved

The following product decisions were made during direction setting:

### Act now or wait for evidence

**Options considered:**
- Act now (CON-1, PRE-1): write the guide before the contributors arrive.
- Wait (NUL-6): review the first three outside pull requests, then decide from what actually
  went wrong.

**Decision:** Act now.

**Rationale:** Waiting would put the timing failure on the kit's first users, and the five
items come from a year of review comments. Counting from the first outside pull request
answers the concern that there is no baseline.

### One file or a second prompt at pull request time

**Options considered:**
- One file (CON-1): CONTRIBUTING.md plus a README pointer.
- A second prompt (PRE-1): add a pull request template, so that three items appear in every
  pull request body.

**Decision:** One file, with no pull request template.

**Rationale:** A template appears after the branch and commits exist, and the problem arises
before that moment.

### Published branch standard or the local pattern

**Options considered:**
- Published standard (PRE-2): Conventional Branch, `<type>/<description>`.
- Local pattern (CON-1): the repository's own branch pattern.

**Decision:** `<GitHub handle>/<short topic>`. The `codex/` prefix stays reserved for agent
branches.

**Rationale:** The guide describes what is done in this repository.

### Where the issue link points

**Options considered:**
- A GitHub issue on this repository.
- A Linear issue in team MAX, which would mean inviting contributors to the workspace. CON-1
  and OPR-3 raised this option, noting that contributors may be unable to open Linear.

**Decision:** A GitHub issue on this repository. The maintainer adds any Linear link at
review.

**Rationale:** Outside contributors have no Linear access.

### What item three says while no tests exist

**Options considered:**
- Keep `uv run pytest` and explain the expected result.
- Say the item applies only once tests exist.

CON-1 and OPR-1 found that there are no tests to run.

**Decision:** Keep the command. The guide says that "no tests ran" (exit code 5) is the
expected result until the first test module lands.

**Rationale:** The item teaches the habit of running the tests before opening a pull request.

### Item three in the success threshold

**Options considered:**
- Count all five items.
- Count only the four items a reviewer can see from the pull request. STR-4 and OPR-1 showed
  that item three cannot be observed.

**Decision:** Count the four. Item three stays in the guide and out of the threshold until
tests exist.

**Rationale:** It is a habit the guide teaches, and nobody can measure it from a pull request
until tests exist.

### When the README pointer lands

**Options considered:**
- Wait in README.md's queue behind MAX-16 to MAX-18.
- Go ahead of that queue.

**Decision:** Ahead of the queue. Those issues rebase on it.

**Rationale:** The pointer is one line, and the arrival date is fixed. The risk pass later
found that MAX-16's rewrite is already built (see sections 10 and 13).

---

## 7. Scope Sketch

**MVP — what the first release must include:**
- `CONTRIBUTING.md` at the repository root, with five items. Each item is one imperative
  sentence plus one example:
  1. Name the branch `<GitHub handle>/<short topic>`. The `codex/` prefix is reserved for
     agent branches.
  2. Make one commit per change. What this means exactly is open; see section 13.
  3. Run `uv run pytest` before opening a pull request. Until the first test module lands,
     "no tests ran" (exit code 5) is the expected result. The item teaches the habit.
  4. Write a one-paragraph description that says why the change was made.
  5. Link a GitHub issue on this repository. The maintainer adds any Linear link at review.
- One sentence at the end of README.md that points to the guide. It lands ahead of MAX-16 to
  MAX-18.
- An ordinary open-source contributing guide serves as a reference for shape only.

This is a new file plus a one-line edit to an existing one.

**Explicitly excluded from this phase:**
- automated enforcement of any kind
- a pull request template
- a code of conduct
- a release process
- anything about how the kit itself works

*Note: exclusions are not permanent. They are the scope boundaries for this phase.*

---

## 8. Success Criteria

How we will know this was solved:

- **Threshold.** Across the first ten pull requests from outside contributors, count the
  pull requests that needed a comment asking for one of the four items a reviewer can see.
  Those are item 1 (branch name), item 2 (one commit per change), item 4 (a description that
  says why) and item 5 (a linked issue).
  - At most one such pull request: it worked.
  - Exactly two: inconclusive.
  - Three or more: it did not work.

  Item three stays out of the threshold until tests exist.
- **Count.** From the first outside pull request onward, the maintainer records which items
  needed a comment.
- **Timing.** The guide is in place and linked from the README before the first outside
  contributor opens a pull request. Where "in place" means is open; see section 13.

---

## 9. Constraints

- **Timeline:** the outside contributors arrive within two weeks of 2026-09-21. The date is
  fixed by when the kit ships.
- **Technical:** the repository is managed with uv and declares pytest. Anything proposed
  must fit that and need no new tooling. The repository currently has no Python modules and
  no tests.
- **Organizational:** the repository is the kit's test bed. Changes stay small and ordinary,
  and nothing may make it unrepresentative of a real project.
- **Effort:** a few hours at most.
- **Must not:** add automated enforcement, or anything beyond a document, at this stage.
- **Must not:** change the kit itself.
- **Sequencing:** the README pointer lands ahead of the README edits queued as MAX-16 to
  MAX-18, which rebase on it.

---

## 10. Risks Acknowledged

These are the top risks from the risk pass. The pass was a single perspective, and it was
**not fresh-context**: the reviewer read this feature's exploration synthesis before writing,
so its overlaps with council findings are not independent. The orchestrator re-verified its
load-bearing claims. For the full inventory, see
`.ai-delivery/features/pull-request-checklist/risk-challenge.md`.

| Risk | Category | Likelihood | Impact | Mitigation Signal | Found By |
|------|----------|-----------|--------|------------------|----------|
| The kit's own pull request workflow contradicts the checklist. Without Linear access, the kit's ship skill suggests a `feat/…` branch, writes a multi-section body, and links Linear, not a GitHub issue | Assumption | High | High | Decide whether a pull request exactly as ship produces it meets the standard. If it does not, decide whether the guide may say how to override ship | risk-pass (verified against ship's skill text and the three existing pull requests) |
| The guide must reach `main`, and nothing here reaches `main`. `main` is unchanged since 2026-08-28, this branch is 19 commits ahead and unpushed, and no pull request has ever merged | Timing | Medium | High | Define "in place" as on `main` on GitHub, and decide how `main` catches up before writing | risk-pass (verified with git) |
| Item five asks for a GitHub issue this repository has never had. The maintainer would run two trackers | Organizational | High | Medium | Decide who files the contributor's GitHub issue, and when, and who triages GitHub issues | risk-pass (overlaps STR-2 and OPR-3; not independent) |
| Using the kit here changes shared files the five items do not cover, such as `.ai-delivery/` and `docs/decisions.md` | Scope | High | Medium | Decide whether contributor pull requests may change those files | risk-pass |
| The threshold can pass or fail for reasons unrelated to the guide: learning after the first pull request, silent fixes, a self-judged count, no end date | Assumption | High | Medium | Decide whether first pull requests are reported separately, whether silent fixes count, and a date for the verdict | risk-pass (overlaps STR-4, NUL-3, NUL-5 and OPR-5; not independent) |
| Item three teaches that "no tests ran" is fine, which later hides uncollected tests | Technical | Medium | Medium | Tie the rewrite of item three to the first test module landing | risk-pass (builds on OPR-1 and OPR-4; not independent) |

**Verified unstated assumptions:**
- **A one-line README edit is not side-effect free.** README.md's hash is recorded in the
  kit's setup fingerprint. On a local clone, the edit turns the setup gate from FRESH to
  STALE, and every kit skill that checks setup stops until setup re-runs.
- **`main` has no branch protection.** A contributor given write access could push to it
  directly.
- **MAX-16's README rewrite is already built.** It is commit 890dea8 in draft pull request
  #3, so going ahead of the queue means rebasing finished work.

---

## 11. Council Insights Summary

**Exploration roster:** constraint, precedent, stress, null and operator, out of a configured
roster of the same five. Stress and null carried a degraded flag: their framing-only diet is
not tool-enforced, because an empty tool list inherits all tools. It held in practice, since
neither made a tool call.
**Synthesis basis:** 5 of 5 mandates examined

**Coverage gaps:** None. Every configured mandate was examined.

**Premise challenge:** NUL-1 argued that no outside contributor has opened a pull request
here, so the five items are a forecast, not a record. It was declined. Waiting would put the
timing failure on the kit's first users, and the five items come from a year of the
maintainer's own review comments.

**Convergences** (cross-diet only; these raise attention, never confidence):
- **Item three, "tests run locally", is the weakest item as written.** STR-4 (framing-only)
  found it self-attested. OPR-1 (codebase) found that there are no tests to run.
- **The success measure, as written, will not reliably show whether the document worked.**
  NUL-3 and STR-4 (framing-only) found it has no baseline. OPR-5 (codebase) found that
  nothing records the count. The count criterion in section 8 answers part of this.

**Worth remembering:**
- **The kit's conventions record covers none of the five items.** The framing had described
  it as "close to what is needed", and NUL-4's discoverability argument rested on that
  description. A read of the record refuted it.
- **The repository has no Python modules or tests.** "Tested with pytest" describes the
  declared toolchain, not a test suite. `pytest` exits with code 5.
- **Precedent's findings were all fetched this session, but PRE-2 went beyond the web.** It
  named the current branch, which the brief never mentions. The agent runner gives every
  member the session's git status, so no member's evidence diet is fully closed to the
  repository.

---

## 12. Prior Art and Context

- The repository has never had written contribution guidance, and nothing in it covers the
  five basics. The kit's conventions record, `.ai-delivery/conventions.md`, is written for
  the kit's skills and has no rule for any of the five items.
- The requester drew on the ordinary shape of open-source contributing guides. The
  references the exploration found are below. All were fetched on 2026-09-22.
  - GitHub, "Setting guidelines for repository contributors", which covers where
    CONTRIBUTING.md lives and where GitHub links it:
    https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors
  - GitHub, "Creating a pull request template for your repository" (not chosen):
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository
  - Conventional Branch v1.1.0 (not chosen; lists `codex/` as an AI-agent prefix):
    https://conventionalbranch.org/
  - nayafia/contributing-template (CC0), the reference for shape:
    https://github.com/nayafia/contributing-template
- This repository's existing branches are the agent-made `codex/<topic>-<number>` branches,
  plus `live-proof-2026-09-21`. Its three open draft pull requests (#1 to #3) are examples of
  what the kit's ship skill produces.
- The original request is recorded as Linear issue MAX-43. The README work that shares
  README.md is MAX-16 to MAX-18, in the Repository usage documentation project.
- Ruled out at framing: automated enforcement and changes to the kit.

---

## 13. Open Questions

These questions remain unresolved at the end of discovery. Address them during shape
requirements generation.

| Question | Why It Matters | Owner (if known) |
|----------|---------------|-----------------|
| Does a pull request exactly as the kit's ship skill produces it meet the standard? If not, may the guide say how to override ship's branch suggestion and body, given that "anything about how the kit works" is excluded? | This is the top risk. Contributors would otherwise have to choose between the guide and the kit, and the threshold would measure that conflict instead of the guide | Max Adamsky |
| What does "one commit per change" mean: one squashed commit per pull request, or one commit per logical change within it? | Contributors and ship read it differently (STR-5; ship commits one unit at a time), and the threshold counts it | Max Adamsky |
| How and when does `main` receive the guide? Does "in place" in the timing criterion mean on `main` on GitHub? | GitHub's Contributing tab reads `main`, which is unchanged since 2026-08-28 and has no `pyproject.toml` or `uv.lock` | Max Adamsky |
| How do the README pointer and a refreshed setup fingerprint land together, and how does the pointer relate to MAX-16's already-built rewrite (commit 890dea8, draft pull request #3)? | The README edit makes setup stale, and every kit skill stops until setup re-runs | Max Adamsky |
| Who files the GitHub issue a contributor links, and when (before the branch exists?)? Who triages GitHub issues? | No GitHub issue has ever been filed here, and the maintainer would run two trackers | Max Adamsky |
| May contributor pull requests change `.ai-delivery/` and `docs/decisions.md`? Does saying so count as describing the kit? | Kit setup rewrites shared files. That puts unrelated changes in one pull request and causes conflicts between contributors working in parallel | Max Adamsky |
| Is each contributor's first pull request reported separately? Does a miss fixed without a comment count? By what date is the verdict read? | Without these, the threshold can pass or fail for reasons unrelated to the guide | Max Adamsky |
| What triggers the rewrite of item three once the first test module lands, and how does a contributor tell "no tests yet" from "tests not collected"? | Exit code 5 will later mean a silent collection failure | Max Adamsky |
| Will contributors push branches to this repository or work from forks? Does `main` need protection before they arrive? | The handle prefix only matters when branches are pushed here, and a direct push to an unprotected `main` skips all five items | Max Adamsky |
| Does the repository need a LICENSE before the first outside contribution? | The repository is public with no license, so contribution terms are unanswered | Max Adamsky |

**Next action:** Max Adamsky runs the shape skill for pull-request-checklist, which reads
this brief in place. Every open question above is for Max Adamsky to settle, in shape or
before it. Max Adamsky also closes MAX-44 (the research issue) and MAX-38 (the Discovery
review gate); the kit closes neither.

---

*Generated by the discover skill. See `.ai-delivery/features/pull-request-checklist/` for all
session artifacts including raw council responses.*
