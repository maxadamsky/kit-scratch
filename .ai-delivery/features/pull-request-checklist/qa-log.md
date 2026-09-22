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
