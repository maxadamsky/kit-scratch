# Exploration Synthesis: pull-request-checklist

**Created:** 2026-09-22
**Synthesis basis:** 5 of 5 mandates examined
**Failed members:** None

This synthesis sets out the realistic ways to give the repository's first outside
contributors a written pull request standard before they arrive, as five exploration members
found them. It shows the evidence behind each claim, so the direction can be chosen knowing
whether a claim was read in the repository, fetched from the web, or reasoned from the
framing alone.

**Reading the finding codes.** Each finding carries a code naming the member that produced it,
plus a number. `CON` argued for the smallest change and read this repository. `PRE` searched
the live web for things to adopt and could not see the repository. `STR` looked for how any
direction breaks at 100 times the stated scale or under hostile input. `NUL` argued against
the premise. `STR` and `NUL` both reasoned from the framing text alone, with no tools. `OPR`
read the repository's operational setup, meaning its CI, deployment and logging, and asked
what fails on the first night after shipping. A claim from a member that could read the
repository is a different kind of statement from one made by a member that could not.

## Coverage

| Mandate question | Examined? |
|---|---|
| Constraint: what is the smallest change to the existing system that solves this framed problem? | examined — response |
| Precedent: what already exists that could be adopted instead of building? | examined — response |
| Stress: for any plausible build, what breaks first at 100x the framing's scale, or under hostile and malformed input? | examined — response |
| Null: what is the strongest honest case that this should not be built? | examined — response |
| Operator: given this repository's operational posture, what is missing for the first night on call? | examined — response |

Every mandate was examined. Every response passed its format check and stayed under the
1,000-word cap.

**Evidence integrity.** Stress and null are meant to run with no tools. Their agent files
declare an empty tool list, and the agent runner treats an empty list as "all tools".
Neither made a tool call this run, so their framing-only evidence held in practice, though
nothing enforced it. Separately, the runner gives every member the session's git status,
meaning the current branch and recent commit subjects, whatever that member's tools are.
That is how PRE-2 named the current branch (see the Blind-Spot Ledger).

## Candidate Directions

This roster deliberately counterweights a builder's bias. It produces smallest-change, adopt
and do-not-build candidates, never an ambitious purpose-built option. Here, the framing
already rules out anything beyond a document. You may also propose a direction the
exploration did not surface.

**Direction-independent findings.** These bear on all three document candidates (A, B and C)
and are listed once, here:
- Item three, "tests run locally", has nothing to run today (OPR-1, CON-1 risk). It is also
  self-attested, so nobody can verify it (STR-4).
- The issue a contributor must link may live where they cannot open it, in Linear team MAX
  (OPR-3, CON-1 risk). At scale, a rule that only asks for a link invites throwaway issues
  and two people claiming the same issue (STR-2).
- Only the maintainer can detect or undo a non-conforming merge (OPR-2, STR-1).
- Nothing records the count that the success threshold needs (OPR-5).
- "One commit per change" is ambiguous and, at scale, causes repeated rebasing (STR-5). If
  contributors push to the main repository rather than to forks, branch names collide at
  scale (STR-3).
- Nothing keeps a hand-written guide in step with the kit's generated records, such as the
  test command in the kit's gates file, `.ai-delivery/gates.md` (OPR-4, CON-1 trade-off,
  STR-6).

### A. One root CONTRIBUTING.md plus a one-line README pointer (CON-1, PRE-1)
A file of about 30 lines at the repository root. Each of the five items is one imperative
sentence plus one example. The test command is taken from the kit's gates file
(`uv run pytest`), and one sentence at the end of README.md points to the new file. GitHub
surfaces a root CONTRIBUTING.md without any configuration. It shows a Contributing tab and a
sidebar link on the repository page, and links the file from the new-issue and
new-pull-request pages (PRE-1, fetched; this repository is on GitHub).
Gains: it is the ordinary open-source form, so the test bed stays representative, and it
needs no configuration. Costs: one more file to keep current, and its test command can go
stale against the gates file. Complexity: Low. Most of the work is the three decisions
listed at the end of this document.

### B. A "Contributing" section inside README.md, no new file (CON-2)
The same five items as a short section at the end of README.md. Gains: no new file, and
anyone who opens the repository page or a clone sees it. Costs: GitHub links only a
CONTRIBUTING file from the new-issue and new-pull-request pages (verified), so this candidate
loses those prompts. README.md is also already queued for three edits recorded as Linear
issues MAX-16 to MAX-18, which must be built one after another, and this would make a fourth.
It is also less representative of where real projects keep contribution rules.
Complexity: Low.

### C. CONTRIBUTING.md plus a GitHub pull request template (PRE-1)
Candidate A's file, plus `pull_request_template.md`. GitHub pre-fills the template into every
new pull request body. It would hold a prompt for why the change was made, a `Closes #` line
for the issue, and a "tests run locally" checkbox. Gains: three items appear while the pull
request is being written, without anyone looking for them. Costs: a second file, which goes
beyond the literal request, though it is still a document and not enforcement. The template
appears only after the branch and commits exist, so it backs up CONTRIBUTING.md rather than
replacing it. It also takes effect only once it is merged to the default branch.
Complexity: Low.

**Parts any document candidate can adopt:**
- **Conventional Branch (PRE-2).** A published branch-naming standard, with names in the form
  `<type>/<description>` and published under the CC BY 4.0 license. It could serve as the
  branch rule instead of writing one. See the branch-rule tension below.
- **A contributing-guide skeleton (PRE-3).** nayafia/contributing-template (CC0) or
  bttger/contributing-gen (MIT). This is a weak fit: neither covers any of the five items
  specifically, and both produce far more than a checklist. They are useful only as a
  reference for shape.

### D. Do not build — wait until the first three outside pull requests have been reviewed (NUL-1 to NUL-7)
Write nothing yet. Review the first three pull requests from outside contributors as
normal. For each one, record which of the five items needed a comment and any other problem
that recurs. Then decide from that record whether to write the five items down, write down
what actually recurred, or do nothing (NUL-6). The premise: no outside contributor has
opened a pull request here, so the five items are a forecast, not an observation (NUL-1).
Null's own steelman: waiting guarantees, for the kit's very first users, the exact timing
failure the framing is about (NUL-7). A finding that bears on this candidate is OPR-5:
nothing in the repository records such a count, so the record NUL-6 relies on depends on
the maintainer keeping it by hand.

## Tensions

### Factual disputes
- **Does a written standard for the five items already exist?** NUL-4 (framing-only) holds
  that the kit's conventions record is a written standard a newcomer cannot find, which
  would make this a discoverability problem. CON-1 (codebase) holds that the record covers
  none of the five items. **Adjudicated: CON-1 is right.** Check: I read
  `.ai-delivery/conventions.md`. Its sections cover structure and naming, code style, errors
  and logging, testing, interfaces, data, security, documentation and Linear. None of them
  states a rule for branch names, commit scope, running tests before a pull request, pull
  request descriptions or issue links. NUL-4 was reasoning from the framing's own phrase,
  "close to what is needed".
- **Are there tests to run?** STR-4 (framing-only) reasons about tests that pass locally and
  fail elsewhere. CON-1 and OPR-1 (codebase) say there are none. **Adjudicated: none exist.**
  Check: `find` located no Python files at all outside the virtual environment, and running
  the project's pytest collected nothing and exited with code 5 ("no tests ran"). The
  framing's "tested with pytest" describes the declared toolchain, not a test suite. STR-4's
  point, that "tests were run" is self-attested, will still stand once tests exist.
- **Does GitHub show CONTRIBUTING.md before a newcomer starts work?** CON-1 (codebase, here
  making a claim about GitHub) says yes. PRE-1 (web, fetched) says the automatic link comes
  when a pull request is opened, after the branch and commits exist. **Adjudicated: both are
  partly right.** Check: I fetched GitHub's contributor-guidelines page. GitHub links the
  file "when someone opens a pull request or creates an issue", and shows it as a
  Contributing tab and a sidebar link on the repository page. A newcomer can meet it on the
  repository page and the new-issue page before starting work, but not through the
  new-pull-request link. `git remote -v` confirms the repository is on GitHub.

### Priority tensions (for you to decide in direction setting)
- **Act now or wait for evidence.** One side writes the standard before the contributors
  arrive (CON-1, codebase; PRE-1, web). The other waits for three outside pull requests and
  decides from what actually went wrong (NUL-6, framing-only). Acting now delivers the
  framing's primary outcome: newcomers meet the standard before their first pull request.
  Waiting yields evidence of the real friction and a baseline for the success measure. The
  cost is rework on the first pull requests of the kit's first users (NUL-7).
- **One file, or a second prompt at pull request time.** One side is the smallest change:
  one file and a README line (CON-1, codebase). The other adds a pull request template so
  that three items appear in every pull request body (PRE-1, web). One file keeps to the
  literal request. The template adds a prompt at the moment of writing, as a second
  document.
- **Published branch standard, or the local pattern.** One side cites Conventional Branch
  (PRE-2, web). The other writes down the pattern the existing branches follow (CON-1,
  codebase). The published rule can be linked to, and some newcomers may already know it.
  The local pattern keeps continuity. Checks:
  - The eight existing `codex/…` branches start with `codex/`, which Conventional Branch
    v1.1.0 lists as an AI-agent prefix (fetched).
  - Their trailing numbers are not consistently issue numbers (`git branch`; for example,
    `codex/handoff-setup-001`).
  - `live-proof-2026-09-21` fits neither pattern.
  - Under the published rule, human contributors would need a type prefix.

## Convergences

- **Item three, "tests run locally", is the weakest item as written.** STR-4 (framing-only)
  finds that the item is self-attested and can report compliance falsely. OPR-1 (codebase)
  finds that there are no tests, so a contributor who follows the item gets an unexplained
  result and has to ask the maintainer. Operator names this its first-night page. The two
  reach the same conclusion by different mechanisms. **Convergent across disjoint evidence:
  raises attention, not confidence.**
- **The success measure, as written, will not reliably show whether the document worked.**
  NUL-3 and STR-4 (framing-only) find that there is no baseline against which to credit a
  clean result to the document, and that an item which looks met may not be. OPR-5
  (codebase) finds that nothing records the count, and that the review threads the count
  depends on live on GitHub, not in the repository. **Convergent across disjoint evidence:
  raises attention, not confidence.**

**Consistent with the framing, not elevated:**
- The maintainer staying the only check on every item (STR-1, OPR-2) follows from the
  framing's ban on automated enforcement.
- "A prompt at pull request time comes too late for branches and commits" (PRE-1) restates
  the framing's own pain point.

The drift finding (STR-6 and NUL-4, framing-only; OPR-4, codebase) is not counted as a
convergence. Its framing-only side assumed the kit's record restates the five items, and the
check above refuted that. The overlap that survives is the test command in the gates file.
CON-1 and OPR-4 make that point, and both have the codebase evidence class, so their evidence
is not disjoint.

## Answers by Mandate

**Constraint (codebase).** Ship A, one root CONTRIBUTING.md and a one-line README pointer,
after the maintainer settles three things: the branch rule, which tracker an outside
contributor links to, and what the tests item says while no tests exist (CON-1). B is the
no-new-file fallback, but it joins the queue of README edits (CON-2). Strongest statement:
writing the file is a 30-minute job, and leaving the three decisions open makes the document
produce the very questions it is meant to remove.

**Precedent (web; every finding fetched this session).** There is no product to adopt. What
is worth adopting is GitHub's convention for where these files live (PRE-1). A pull request
template can only back up CONTRIBUTING.md, because branches and commits are finished before
any pull request exists. Conventional Branch can stand in for the branch rule (PRE-2), and
contributing templates help only with shape (PRE-3). Strongest statement: before the
contributors arrive, decide whether a second template file is in scope and whether to adopt
Conventional Branch prefixes.

**Stress (framing-only).** Every permitted direction relies on voluntary compliance and on
the maintainer checking every pull request. Both hold at six people and give way long before
100x (STR-1). The weakest point is item three, which cannot be verified by design (STR-4).
The other failure modes:
- issues filed only to have something to link (STR-2)
- branch collisions if contributors push to the main repository (STR-3)
- rebase churn and an ambiguous one-commit rule (STR-5)
- a guide that any pull request can edit (STR-6)

Strongest statement: decide now whether the success threshold measures actual compliance or
only the absence of review comments.

**Null (framing-only).** The pain is a forecast. No outside contributor has opened a pull
request here, so the five items are the maintainer's prediction (NUL-1). They come from the
one person who least needs them (NUL-2), and the success measure has no baseline (NUL-3).
Instead, wait for three outside pull requests and decide from the record (NUL-6). Null calls
its own case weaker than usual. Its steelman is that waiting spends the first impression of
the kit's first users (NUL-7). Strongest statement: were these five comments ever written to
anyone other than the maintainer?

**Operator (codebase).** The repository has no run-time machinery: no CI, no pull request
template, no tests and no tool configuration. The maintainer's review is therefore the only
detection and the only recovery for every item (OPR-2). First-night page: the first
contributor to run the tests as told gets "no tests ran", has nothing to diagnose it from,
and has to ask (OPR-1). It also found an issue link contributors cannot open (OPR-3), drift
from the kit's records (OPR-4), and a success count nobody records (OPR-5). Strongest
statement: decide what item three means while there are no tests, and where an outside
contributor's issue link points.

## Blind-Spot Ledger

| Assertion | By | Status |
|---|---|---|
| The repository is hosted on GitHub (stated as an assumption) | PRE-1 (web) | verified — `git remote -v` shows github.com/maxadamsky/kit-scratch |
| The current branch, `live-proof-2026-09-21`, has no type prefix | PRE-2 (web) | verified — `git branch --show-current`. This is outside the web diet: the framing names no branch, so the claim came from the session's git status, which the runner gives every member |
| GitHub shows a root CONTRIBUTING.md on the new-pull-request and new-issue pages | CON-1 (codebase) | verified — fetched GitHub's contributor-guidelines page |
| GitHub does not show a README section on the new-pull-request page | CON-2 (codebase) | verified — the same page names only the CONTRIBUTING file for that link |
| uv installs pytest on the first `uv run`, so contributors need only uv | CON, What Already Exists (codebase) | asserted, unverifiable under diet — this is uv's behaviour, not checked this session |
| Outside contributors probably cannot open issues in Linear team MAX | CON-1, OPR-3 (codebase) | asserted, unverifiable under diet — workspace access is not recorded in the repository; the maintainer can answer it |
| There is no CI (stated as an assumption) | STR-4 (framing-only) | verified — no `.github/`, `.gitlab-ci.yml`, `.circleci` or other pipeline configuration, and the kit's config records `ci_system: null` |
| Tests exist that can pass locally and fail elsewhere | STR-4 (framing-only) | refuted for today — there are no test files, and pytest exits with code 5 |
| Contributors push branches to the main repository, not to forks (an assumption) | STR-3 (framing-only) | asserted, unverifiable under diet — depends on GitHub access settings |
| The kit's conventions record is a written standard close to what is needed | NUL-4 (framing-only) | refuted — the record has no rule for any of the five items (checked by reading its sections) |
| Newcomers' real friction will be something the list does not name | NUL-2 (framing-only) | asserted, unverifiable under diet — no outside pull request exists yet |
| Ten outside pull requests may take a long time to arrive, and each fix takes minutes | NUL-3, NUL-5 (framing-only) | asserted, unverifiable under diet |
| The repository's recent history already bundles several changes per commit | OPR-2 (codebase) | refuted in part — `git show --stat` shows 93a0729 touches one file, and 30b3d94 commits one setup re-run's five output files together, which is one change across several files. Commit contents are beyond what Read, Grep and Glob can show |

**What no member could see:**
- The incoming contributors themselves. Nobody has asked them what they already know or
  where they look first; the stakeholder session was declined.
- GitHub's repository settings: branch protection, whether contributors push branches or
  fork, and whether GitHub issues are enabled.
- Who can open the Linear workspace.
- Any real review history, because no outside pull request has been reviewed here.

All three evidence classes ran: codebase, web and framing-only.

**Decisions this synthesis surfaces.** Max Adamsky, as maintainer and project lead, owns all
of them:
- accept or decline the premise challenge (candidate D)
- choose a direction
- for any document direction, settle what item three says while no tests exist, where an
  outside contributor's issue link points, and which branch rule applies

## Chosen Direction

**Direction:** A. One root CONTRIBUTING.md plus a one-line README pointer (CON-1, PRE-1).
**Rationale:** Direction A puts the standard where GitHub already shows it to a newcomer. The
repository page carries a Contributing tab and a sidebar link, and the new-issue page links
to the guide; both can come before work starts. The new-pull-request page links to it again.
A README section gets none of those links. Direction A is also the smallest change that fully
answers the request: one file and one pointer. No part of it first appears only after the
branch and commits exist, as a pull request template would.

**Scope (MVP):** a new file, plus a one-line edit to an existing one.
- `CONTRIBUTING.md` at the repository root, with five items. Each item is one imperative
  sentence plus one example:
  1. Name the branch `<GitHub handle>/<short topic>`. The `codex/` prefix is reserved for
     agent branches.
  2. Make one commit per change.
  3. Run `uv run pytest` before opening a pull request. Until the first test module lands,
     "no tests ran" (exit code 5) is the expected result; the item teaches the habit.
  4. Write a one-paragraph description that says why the change was made.
  5. Link a GitHub issue on this repository. The maintainer adds any Linear link at review.
- One sentence at the end of README.md that points to the guide. It lands ahead of MAX-16 to
  MAX-18.
- An ordinary open-source contributing guide (PRE-3) serves as a reference for shape only.

**Explicitly excluded:**
- automated enforcement
- a pull request template
- a code of conduct
- a release process
- anything about how the kit itself works

**Success criteria:**
- **Threshold.** Across the first ten pull requests from outside contributors, count the
  pull requests that needed a comment asking for one of the four items a reviewer can see
  (items 1, 2, 4 and 5). At most one such pull request means it worked, exactly two is
  inconclusive, and three or more means it did not work. Item three stays out of the
  threshold until tests exist.
- **Count.** From the first outside pull request onward, the maintainer records which items
  needed a comment.
- **Timing.** The guide is in place and linked from the README before the first outside
  contributor opens a pull request.

**Constraints:**
- The framing's constraints all apply:
  - The contributors arrive within two weeks, a date fixed by when the kit ships.
  - The work takes a few hours at most.
  - It fits uv and pytest and needs no new tooling.
  - It stays small and ordinary, because the repository is the kit's test bed.
  - There is no automated enforcement and nothing beyond a document.
  - There are no changes to the kit.
- The README pointer lands ahead of MAX-16 to MAX-18, which rebase on it.

**Premise challenge:** NUL-1 argues that no outside contributor has opened a pull request
here, so the five items are a forecast rather than a record. **Declined.** Waiting would put
the timing failure on the kit's first users, and the five items come from a year of the
maintainer's own review comments. Null's baseline point (NUL-3) was adopted in part, as the
count criterion.

**Resolved trade-offs:**
- **Act now or wait for evidence:** act now. Waiting would put the timing failure on the
  kit's first users. This was decided when the premise challenge was declined.
- **One file or a second prompt at pull request time:** one file, with no pull request
  template. A template appears after the branch and commits exist, and the problem arises
  before that moment.
- **Published branch standard or the local pattern:** the local pattern,
  `<GitHub handle>/<short topic>`, with `codex/` reserved for agent branches. The guide
  describes what is done in this repository.
- **Where the issue link points:** a GitHub issue on this repository, because outside
  contributors have no Linear access. The maintainer adds any Linear link at review.
- **Item three in the success threshold:** out until tests exist. It is a habit the guide
  teaches, and a reviewer cannot observe it from a pull request.

**Open for shape:** what "one commit per change" means exactly. It could mean a single
squashed commit per pull request, or one commit per logical change within the pull request.
Stress found the wording ambiguous (STR-5). Max Adamsky, as maintainer, decides this during
shape.
