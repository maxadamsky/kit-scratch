# Q&A log — Pull request checklist

Questions and answers behind the pull request checklist feature's requirements. The log keeps
each decision traceable to the answer that settled it, so a reader who was not in the
session can see why the requirements say what they say.

- Feature folder: .ai-delivery/features/pull-request-checklist/
- Linear project: Pull request checklist (P-MAX-12,
  https://linear.app/max-test-workspace/project/pull-request-checklist-08fae13de2f4)
- Started: 2026-09-21
- Entry point: triage — this feature arrived as an approved group holding one brought-in
  request, not a guided interview. During triage that request was labelled B1; B1 was only
  a label in that conversation, not a Linear issue ID. Linear records the request as MAX-43.

## Exchanges

### 1. Additional requests to bring in
**Asked:** The Triage inbox is empty. Are there requests to bring in, and for each one, who
asked, how it reached you, and when?
**Answer:** One request: "Add a CONTRIBUTING.md at the repository root with a five-item
checklist for opening a pull request: branch naming, one commit per change, tests run
locally, a one-paragraph description, and a linked issue." Requested by Max Adamsky, via
the planning channel, on 2026-09-21. A Linear member read matched the requester to exactly
one workspace member, who is also the person running the sitting.

### 2. Extraction of the brought-in request, for grouping
**Asked:** Does the extraction look right — suggested name Pull request checklist, an
inferred problem statement, the five checklist items as scope, and four gaps (the rule
behind each item, who the checklist is for and why now, what is excluded, how success is
measured)?
**Answer:** "1" — looks good; carry it into grouping as it is.

### 3. Changes to the proposed grouping
**Asked:** Here is the whole grouping. Move requests between groups, change the primary,
and mark each group shape now or leave. What should change? The grouping was one
standalone group holding B1, with B1 as the primary — the request the group's project is
named after.
**Answer:** "Nothing should change. Group 1 stays as proposed, B1 primary, shape now.
Approve the whole grouping."

### 4. Project lead, problem statement and new labels
**Asked:** Who leads the project; is the one-line problem statement right; and may triage
create the `gate` label, which marks the review issue that closes each stage, and the
`request` label, which marks the issue recording an original request?
**Answer:** Max Adamsky leads it. The problem statement is confirmed as proposed: "Nobody
opening a pull request against this repository has a written checklist of what the pull
request must include." Yes, create both labels.

### 5. Milestone set
**Asked:** The new project has no milestones. Approve creating all five stage milestones —
Discovery, Prototype, Build, Validate and Release — with the kit's standard descriptions?
**Answer:** "Yes, approve all five milestones."

## Notes

- Triage created the project with status Proposal, its five milestones, the five review
  issues MAX-38 to MAX-42, and MAX-43 recording the request. Each write was read back in a
  separate call.
- Source requests for this feature: MAX-43. Shape's intake guide says a group made only of
  brought-in requests has no source request issues yet, but triage now creates one for each
  brought-in request and the artifact schema says to list them, so this feature follows the
  schema. Correcting the intake guide's sentence is a kit change, owned by the kit's
  maintainer, Max Adamsky.

## Discover — 2026-09-21

Discover ran on this feature after triage, tracked on the same Linear project. Its exchanges
continue the numbering above.

### 6. Topic to run discover on
**Asked:** The workspace holds one discover topic, cited-source-staleness, which is complete,
and this folder, which triage created and which has no framing yet. Start
pull-request-checklist tracked on P-MAX-12, revisit cited-source-staleness, or start a
different topic?
**Answer:** "1" — start pull-request-checklist, tracked on the Linear project Pull request
checklist (P-MAX-12).

**Linear:** Discover moved P-MAX-12's status from Proposal to Discovery. The status was read
immediately before the write and read back afterwards in a separate call; both reads agreed
with the write.

### 7. The problem behind the request, in the requester's words
**Asked:** Triage recorded the request as a CONTRIBUTING.md holding a five-item pull request
checklist, and the problem as "Nobody opening a pull request against this repository has a
written checklist of what the pull request must include." In your own words, what problem or
opportunity is behind the request, and what prompted it now?
**Answer:** "This repository exists to exercise the delivery kit, and people opening pull
requests here have no shared standard for what a pull request needs, so review comments
repeat the same basics. What prompted it now is that outside contributors are about to start
using the repository and I want the expectations written down before they arrive."

**Facilitator note:** The pain named is repetition in review: the same basics are raised
again and again. The trigger is a change of audience. Outside contributors will arrive
without the context the current contributors share.

### 8. Who experiences the problem
**Asked:** Who opens pull requests here today and who reviews them; who the coming outside
contributors are and what they already know; whether anyone is affected differently; and
roughly how many people, now and once they arrive.
**Answer:** "Today I open the pull requests and I review them, so it is one person on both
sides. The outside contributors are the first users of the delivery kit, a handful of
people, two to five, who know the kit from its README but have never worked in this
repository and do not know its conventions. As the maintainer I am the one who has to hold
the standard and answer the same questions. Nobody downstream reads the history yet. So it
is one person now, and up to six once they arrive."

**Facilitator note:** Today the author and the reviewer are one person, so the repeated review
comments are a maintainer reviewing their own work. Most of the pain is still ahead of us. It
arrives with two to five newcomers who know the kit from its README but do not know this
repository's conventions.

### 9. What is broken today
**Asked:** Which basics keep coming up in review; what keeps pull requests consistent today
and why that will not hold for newcomers; and the specific moment things fall apart.
**Answer:** "The basics that keep coming up are branch names that say nothing about the
change, several unrelated changes squeezed into one commit, pull requests opened before the
tests were run locally, a one-line description that does not say why, and no link to the
issue the work came from. Today what keeps things consistent is that I know the conventions
because I set them; that lives in my head and nowhere else, so a newcomer has no way to find
it. Things fall apart at the moment a pull request is opened, because by then the branch is
named, the commits are shaped and the description is written, and asking for changes means
redoing work that was already done."

**Facilitator note:** The failure is about timing. The standard only becomes visible at review,
after the work it governs is finished, so every correction means rework. The standard is also
unwritten: it exists only in the maintainer's head. The five basics match the five requested
checklist items one to one. For at least one item the real need is sharper than the item
itself: the description has to say why the change was made, not merely run to a paragraph.

### 10. The opportunity
**Asked:** If this were solved well, what could a newcomer do that they cannot today; what
would the maintainer stop having to do; and which outcome matters most?
**Answer:** "A newcomer could open a pull request that meets the standard without asking me
first, because the standard is written where they will look before they start. I would stop
writing the same five review comments and stop explaining conventions one contributor at a
time. The outcome that matters most is newcomers getting it right the first time, because
that is what removes the rework; less review time follows from it."

**Decision recorded:** The primary outcome is newcomers getting the pull request right the
first time. Less review time is a consequence of that outcome, not a separate goal.

**Facilitator note:** The opportunity says both where the standard must be and when it must
be seen. It has to sit where a newcomer looks before starting the work, not where the
reviewer looks at the end.

### 11. Constraints
**Asked:** Timeline, technical, organizational, effort, and anything the exploration must not
do or propose.
**Answer:** "Timeline: the outside contributors arrive within the next two weeks, and that is
fixed by when the kit ships. Technical: the repository is a small Python project managed with
uv and tested with pytest, so anything proposed has to fit that and need no new tooling.
Organizational: this repository is the kit's test bed, so keep changes small and ordinary;
nothing that would make it unrepresentative of a real project. Effort: a few hours at most.
Must-nots: do not propose automated enforcement or anything beyond a document at this stage,
and do not propose changes to the kit itself."

**Decision recorded:** The exploration stays inside two boundaries. Whatever is proposed at
this stage is a document, with no automated enforcement. Nothing proposed changes the kit
itself. The deadline is fixed: within two weeks of 2026-09-21, when the kit ships.

**Facilitator note:** The must-not fixes the form of the answer before exploration starts: the
answer is a document. What stays open is what the document says, where it lives, and how a
newcomer meets it before starting the work.

### 12. Prior art
**Asked:** Any earlier contribution guidance here; anything already written, in this
repository or in the kit, that covers the five basics; other projects' guides or conventions
being drawn on; anything already ruled out beyond automated enforcement and kit changes.
**Answer:** "This repository has never had written contribution guidance. Nothing in it
covers the five basics. The kit records the repository's conventions in
.ai-delivery/conventions.md, which is close but is written for the kit's skills, not for a
person opening a pull request. I am drawing on the ordinary shape of open-source contributing
guides, nothing specific. Nothing else has been ruled out."

**Facilitator note:** The nearest existing record, `.ai-delivery/conventions.md`, is written
for the wrong audience rather than missing. The kit's skills read it; a person opening a pull
request does not.

### 13. Success signal
**Asked:** Once the outside contributors have each opened their first few pull requests, what
could be observed, counted or felt that shows it worked: what those pull requests look like,
what disappears from review comments, and a threshold with a failure point.
**Answer:** "Those first pull requests would arrive with a branch name that says what changed,
one commit per change, tests already run locally, a description that says why, and a linked
issue, without my asking. The five review comments would disappear from my review. The
threshold: across the first ten pull requests from outside contributors, no more than one
needs a comment asking for one of the five items. If three or more of those ten need such a
comment, the document did not work."

**Facilitator note:** The pass and fail lines leave exactly two of ten undefined. This was
raised at the framing review.

### 14. Framing review
**Asked:** Does the framing summary reflect the problem accurately, and is anything missing?
Two of ten pull requests needing a comment falls between the pass line and the fail line, so
should it count as a pass, a fail, or inconclusive? The summary also noted that the
conventions record is described without its file path, because two exploration members work
from the framing text alone and their briefs must not carry file paths.
**Answer:** "1. Two of ten is inconclusive."

**Decision recorded:** The framing is approved as summarized. Across the first ten pull
requests from outside contributors, the result is as follows: at most one needing a comment
means it worked, exactly two is inconclusive, and three or more means it did not work.
framing.md was saved on 2026-09-22.

### 15. Risk pass, Discovery completion, and discovery work
**Asked:** (1) After a direction is chosen, should a reviewer with no knowledge of the earlier
discussion red-team it? (2) What completes Discovery for P-MAX-12: stakeholder sign-off on
the problem and the chosen direction, research complete with success measures written, or
both? (3) Which discovery work applies: research plus one stakeholder session with incoming
contributors (the default, because the framing names them), research only, or something
else?
**Answer:** "1a, 2b, 3b"

**Decision recorded:** The risk pass is requested. Discovery completes when the research is
complete and the success measures are written; stakeholder sign-off is not part of completion
for this project. The discovery work is research only, recorded as one Discovery-stage issue
covering this discover run. The stakeholder session with incoming contributors was offered and
declined.

**Linear:** MAX-38, the Discovery review gate issue, was refined rather than recreated. Its
acceptance criteria now read "Research complete, with success measures written", and the
issue says who chose that meaning and when. The update was read back in a separate call and
matched. Before creating anything, discover listed the project's Discovery-milestone issues:
only MAX-38 was there. It then created MAX-44, "Explore directions for a written pull request
standard", in the Discovery milestone with status In Progress, and read it back in a separate
call; it matched.

**Kit note, for the kit's maintainer, Max Adamsky:** The discover skill says each
Discovery-stage issue is recorded in the brief's `**Discovery issues:**` header line as soon as
its read-back returns. The brief is not written until the last phase, however, and the skill
treats an existing brief as a finished run. Writing a brief early would therefore mark this run
complete. Discover recorded the project and MAX-44 as header lines in framing.md instead.
Header lines there are kept out of what the exploration members see. Both lines will be
carried into the brief's header when the brief is written. Correcting the skill's sentence is a
kit change, owned by the kit's maintainer, Max Adamsky.

**Exploration (2026-09-22):** The full council ran: constraint, precedent, stress, null and
operator, all as configured. Every response passed its format check and was saved verbatim
under `council-responses/`. Tool calls per member: constraint 15, precedent 6, stress 0,
null 0, operator 14. The synthesis checked several claims against the repository and the
web. Four checks changed the picture:
- `.ai-delivery/conventions.md` has no rule for any of the five items. The framing had
  described it as close to what is needed.
- The repository has no Python files and no tests. Running pytest collects nothing and
  exits with code 5.
- The repository is on GitHub. GitHub shows a root CONTRIBUTING.md on the repository page,
  on the new-issue page and on the new-pull-request page.
- The existing `codex/…` branches use a prefix that Conventional Branch v1.1.0 lists for AI
  agents.

**Kit note, for the kit's maintainer, Max Adamsky:** The stress and null agent files declare
`tools:` with an empty value. The agent runner reads that as "inherit all tools", and the
agent listing shows both members with all tools. Their framing-only diet therefore rests on
prompt wording, not on the tool allowlist. The discover skill relies on the allowlist
("Diet is enforced by each member's tool allowlist, not by brief prose"). Neither member
made a tool call in this run, so their evidence held in practice. Fixing this is a kit
change.

**Kit note, for the kit's maintainer, Max Adamsky:** The runner gives every subagent the
session's git status, whatever that subagent's tools: the current branch and recent commit
subjects. Precedent works only from the web, yet it named the current branch,
`live-proof-2026-09-21`. The brief never mentions that branch. A tool allowlist cannot
remove this context, so no member's diet is fully closed to the repository. Fixing this is a
kit change.

### 16. Ready for direction setting
**Asked:** After the synthesis was presented, with four candidates, null's premise challenge,
six tensions and the checks that changed the picture: ready to move to direction setting?
**Answer:** "Yes, move to direction setting."

### 17. The premise challenge
**Asked:** Null argues that no outside contributor has opened a pull request here, so the
five items are a forecast of newcomer mistakes, not a record of them (NUL-1). Its
alternative is to write nothing yet, review the first three outside pull requests, record
which items needed a comment, and decide from that record (NUL-6). Accept, or decline with
a reason?
**Answer:** "I decline the challenge. Waiting guarantees the timing failure this exists to
prevent, and it lands on the kit's first users, which is the worst place for it. The
forecast comes from a year of my own review comments, not a guess. I take the baseline
point: I will record, from the first outside pull request onward, which of the five items
needed a comment, so the success measure has something to count."

**Decision recorded:** The premise challenge is declined, for two reasons. Waiting would
land the timing failure on the kit's first users. The five items come from a year of the
maintainer's own review comments, not a guess. Null's baseline point is adopted in part. From
the first outside pull request onward, the maintainer records which of the five items needed
a comment, which gives the success threshold a count. This addresses the finding that
nothing records the count (OPR-5).

### 18. Direction and trade-offs
**Asked:** Which direction is most promising: A (one root CONTRIBUTING.md plus a one-line
README pointer), B (a Contributing section inside README.md), C (CONTRIBUTING.md plus a
GitHub pull request template), two complementary directions, a combination, or a direction
of your own? Conventional Branch and a contributing-guide skeleton could be adopted as parts
of any of them.
**Answer:** "Direction A: one root CONTRIBUTING.md plus a one-line README pointer. One file
only, no pull request template; a template appears after the branch and commits exist, which
is the moment this problem lives before. For the branch rule, use this repository's own
branch pattern rather than adopting the published Conventional Branch standard; the guide
describes what we do here. The contributing-guide skeleton can be a reference for shape,
nothing more."

**Decision recorded:** The chosen direction is A: one root CONTRIBUTING.md plus a one-line
README pointer. Three trade-offs were resolved:
- **One file or a second prompt at pull request time:** one file, with no pull request
  template. A template appears after the branch and commits exist, and the problem lives
  before that moment.
- **Published branch standard or the local pattern:** the local pattern. The guide describes
  what is done in this repository.
- **Act now or wait for evidence:** act now. This was settled when the premise challenge was
  declined at exchange 17.

The contributing-guide skeleton (PRE-3) is a reference for shape only.

### 19. Scope sketch
**Asked:** The first version is a new file plus a one-sentence README edit. Four questions
were asked. What should an outside contributor's branch name look like, given the existing
`codex/<topic>-<number>` branches and `live-proof-2026-09-21`? What should "tests run
locally" say while no tests exist, given that `uv run pytest` reports "no tests ran" and
exits with code 5? Where does the issue link point, Linear team MAX or a GitHub issue? What
is explicitly out of scope?
**Answer:** "1. Branch names: an outside contributor uses their GitHub handle as the prefix
and a short topic after it, for example handle/short-topic. The codex/ prefix stays reserved
for the agent branches and is not for people. 2. Keep the command uv run pytest and say that
"no tests ran", exit code 5, is the expected result until the first test module lands; the
point of the item is the habit, run it before opening. 3. Link a GitHub issue on this
repository; outside contributors do not have Linear. If a Linear issue exists for the work,
the maintainer adds that link at review. 4. Out of scope for this version: any automated
enforcement, a pull request template, a code of conduct, release process, and anything
about how the kit itself works."

**Decision recorded:**
- **Branch rule:** an outside contributor's branch is named `<GitHub handle>/<short topic>`.
  The `codex/` prefix is reserved for agent branches.
- **Tests item:** the item keeps `uv run pytest` and states that "no tests ran" (exit code
  5) is the expected result until the first test module lands. The item is about the habit
  of running the tests before opening a pull request.
- **Issue link:** contributors link a GitHub issue on this repository, because outside
  contributors have no Linear access. If a Linear issue exists for the work, the maintainer
  adds that link at review.
- **Out of scope for this version:** automated enforcement, a pull request template, a code
  of conduct, a release process, and anything about how the kit itself works.

### 20. Success criteria
**Asked:** Do the threshold (from the framing) and the count (from exchange 17) stand as
Direction A's success criteria? Item three is self-attested and there are no tests yet, so a
reviewer cannot see a miss on it (STR-4, OPR-1). Should the threshold count all five items,
only the four a reviewer can see, or something else? Add or change criteria, aiming for two
to four in total.
**Answer:** "The threshold and the count stand. Item three: count only the four items a
reviewer can see from the pull request; item three is a habit the guide teaches and cannot be
measured until tests exist, so it stays in the guide and out of the threshold. Add one
criterion: the guide is in place and linked from the README before the first outside
contributor opens a pull request. That makes three criteria."

**Decision recorded:** Direction A has three success criteria:
1. **The threshold,** judged across the first ten pull requests from outside contributors.
   The count covers only the four items a reviewer can see from the pull request: branch
   name, one commit per change, a description that says why, and a linked issue.
   - At most one pull request needs a comment asking for one of these items: it worked.
   - Exactly two do: inconclusive.
   - Three or more do: it did not work.
2. **The count:** from the first outside pull request onward, the maintainer records which
   items needed a comment.
3. **Timing:** the guide is in place and linked from the README before the first outside
   contributor opens a pull request.

Item three, tests run locally, stays in the guide but is out of the threshold until tests
exist. This narrows the framing's threshold from five items to four. framing.md is left as
approved, and the Chosen Direction records the change.

### 21. Constraints specific to the direction
**Asked:** Are there constraints specific to Direction A that the framing did not cover? The
README pointer edits README.md. Three Backlog issues in the Repository usage documentation
project, MAX-16 to MAX-18, also edit README.md and are meant to land one after another. The
guide's timing criterion ties the pointer to the contributors' arrival. Does the pointer go
in ahead of that queue, wait its turn, or something else?
**Answer:** "The pointer goes in ahead of that queue; it is one line and the arrival date is
fixed, and the README issues can rebase on it. Nothing else to add."

**Decision recorded:** The README pointer lands ahead of MAX-16 to MAX-18. It is one line,
the arrival date is fixed, and those issues rebase on it. No other constraints are specific
to this direction.

### 22. Why this direction
**Asked:** In one or two sentences, what makes Direction A as a whole the right bet,
including over a Contributing section inside the README (B)?
**Answer:** "Direction A puts the standard where GitHub already shows it to a newcomer before
they start, on the repository page and on the new-pull-request page, which a README section
does not get. It is also the smallest change that fully answers the request: one file, one
pointer, nothing that arrives after the branch and commits exist."

**Facilitator note:** Two details in this answer do not match the checks recorded in the
synthesis. First, GitHub's link on the new-pull-request page appears after the branch and
commits exist, not before the contributor starts. Second, GitHub renders a README section on
the repository page too. What a README section does not get is the Contributing tab, the
sidebar link, and the links from the new-issue and new-pull-request pages. A corrected
wording of the rationale was offered at the direction summary for the maintainer to confirm.

### 23. Direction summary
**Asked:** Does the direction summary capture Direction A accurately, including the corrected
rationale? The corrected rationale names the Contributing tab, the sidebar link and the
new-issue page as the places a newcomer meets the guide before starting. It also notes that a
README section is shown on the repository page too.
**Answer:** "1"

**Decision recorded:** The direction summary is approved as presented, with the corrected
rationale. It was written as the Chosen Direction section of exploration-synthesis.md on
2026-09-22. One item is left open for shape: what "one commit per change" means exactly
(STR-5).

### 24. Risk pass on the chosen direction
**Asked:** The risk pass was requested at preferences. Run it now on Direction A, or skip to
the brief?
**Answer:** "1". Run the risk pass.

**Risk pass (2026-09-22):** One general-purpose subagent received the risk brief: the
framing plus the Chosen Direction, with no council output. It made 33 tool calls. Before
writing, it read the feature's framing, synthesis and Q&A log, the kit configuration and the
kit's ship and setup skills. It also queried GitHub and ran checks on scratch copies. Its
response says this itself, and it states that no overlap with the council should count as
an independent re-find. Afterwards the workspace was unchanged: the only changes in
`git status` were discover's own files, and no branch, worktree or stash was added. The
orchestrator saved the raw response to `council-responses/solo-risk.md` and re-verified the
load-bearing claims:
- The ship skill suggests `feat/{feature-name}` when Linear is unavailable.
- The repository's three existing pull requests are multi-section drafts that reference
  Linear and no GitHub issue.
- No GitHub issue has ever been filed.
- `main` has been unchanged since 2026-08-28, and the working branch is 19 commits ahead and
  unpushed.
- `main` has no branch protection.
- MAX-16's README rewrite is already built (commit 890dea8).
- On a local clone, a one-line README edit turns the setup gate from FRESH to STALE.

`risk-challenge.md` records one critical risk, five significant risks, no watch items and
four unstated assumptions. It is labeled as not fresh-context.

**Kit note, for the kit's maintainer, Max Adamsky:** Phase 2b tells the orchestrator to spawn
a `general-purpose` subagent and says the subagent "receives this brief and nothing else — no
workspace access". A general-purpose agent has every tool, including Read, Bash and the web.
Nothing in the brief tells it not to use them, and it did use them, including reading the
exploration synthesis the pass is meant to be unanchored from. Freedom from anchoring
therefore rests on nothing. Fixing this is a kit change.

### 25. How to proceed after the risk pass
**Asked:** The risk pass found one critical risk: the kit's ship skill contradicts three of
the four counted items. It found five significant risks and four unstated assumptions. It
was not independent, because the reviewer read the synthesis first. Four options were
offered: return to direction setting, discuss specific risks here, go straight to the brief
carrying the risks as open questions for shape, or re-run a clean risk pass as a retry.
**Answer:** "3"

**Decision recorded:** Direction A stands unchanged. The risk findings go into the brief as
acknowledged risks and as open questions for shape, and the maintainer owns each one. No
clean retry of the risk pass was run.

### 26. Brief review
**Asked:** Does the brief summary capture what the session worked out: the direction, the key
decisions, the top risks, and ten open questions for shape? Is it ready to finalize?
**Answer:** "1"

**Decision recorded:** The brief is finalized at
`.ai-delivery/features/pull-request-checklist/brief.md` on 2026-09-22. The project line and
the Discovery issues line were carried into its header from framing.md's header.

**Linear (handoff):** Discover read MAX-38, the Discovery review gate issue, at handoff. It is
open, in Backlog. Because the gate is open, discover set nothing: P-MAX-12 stays in Discovery.
The shape skill sets Ready on its own entry once it finds the gate closed. MAX-44, the research
issue, stays In Progress. The kit closes neither issue; closing them is Max Adamsky's call.

### 27. Export the brief
**Asked:** Keep the brief where it is, or also copy it to the project root as
pull-request-checklist-brief.md for easy sharing?
**Answer:** "1". Keep it as it is.

**Decision recorded:** The brief stays only at
`.ai-delivery/features/pull-request-checklist/brief.md`, and nothing was copied. The discover
run is complete.
