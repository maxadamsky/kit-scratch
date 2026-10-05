# Q&A log — Repository changelog

Questions and answers behind the repository changelog feature's requirements. The log keeps
each decision traceable to the answer that settled it, so a reader who was not in the
session can see why the requirements say what they say.

- Feature folder: .ai-delivery/features/repository-changelog/
- Linear project: Repository changelog (P-MAX-13,
  https://linear.app/max-test-workspace/project/repository-changelog-705794e8fbf9)
- Started: 2026-09-29
- Entry point: triage — this feature arrived as an approved group holding two brought-in
  requests, not a guided interview. During triage those requests were labelled A and B;
  A and B were only labels in that conversation, not Linear issue IDs. Linear records
  request A as MAX-72 and request B as MAX-73.

## Exchanges

### 1. Additional requests to bring in
**Asked:** The Triage inbox is empty. Are there requests to bring in, and for each one, who
asked, how it reached you, and when?
**Answer:** Two requests, both from Max Adamsky, channel "live proof", dated 2026-09-29:
A — "Add a CHANGELOG.md at the repository root that records each release's user-facing
changes, newest first." B — "Link the changelog from the README so readers can find what
changed between versions." A Linear member read matched the requester to exactly one
workspace member, who is also the person running the sitting.

### 2. Grouping, lead and problem statement
**Asked:** Here is the whole grouping. Move requests between groups, change the primary,
and mark each group shape now or leave. The grouping was one group of related requests
holding A and B, with A as the primary — the request the group's project is named after.
Also: who leads the project, and is the proposed one-line problem statement right?
**Answer:** "Approve Group A as shape now, primary R1. Lead: Max Adamsky. The problem
statement is right." Read as approving the table exactly as shown: the only group, with
request 1 (label A) as primary. The problem statement is: the repository keeps no record
of what changed between releases, so readers can't tell what a new version changes for
them.

### 3. Milestones for the project
**Asked:** Create the five stage milestones — Discovery, Prototype, Build, Validate,
Release — on the project, which had none?
**Answer:** "Yes, create the five milestones."

### 4. Extraction of the two requests, for shaping
**Asked:** Does the extraction look right — feature name repository-changelog, the
confirmed problem statement, readers of the repository as inferred users, the changelog
and the README link as scope, nothing found for out of scope, and six gaps: what counts as
a release, starting content, format, keeping it current, where the README link goes, and
what is excluded?
**Answer:** "1" — looks good; write the gaps into the requirements as marked assumptions.

### 5. Requirements document depth
**Asked:** Full (ten sections with a section-by-section review) or Lite (four sections
generated in one pass for approval)?
**Answer:** "2" — Lite.

### 6. Tracker population
**Asked:** Decompose the requirements into units of work and create them in Linear, in the
project's Prototype milestone, after reviewing the decomposition — or requirements only,
with nothing written to Linear?
**Answer:** "1" — yes, decompose and create the delivery issues after review.

### 7. Approval of the Lite requirements document
**Asked:** Here's the Lite requirements document — two units, seven requirements, and six
open questions each carrying a working answer. Does it look right, or would you like me to
revise anything? Approving it also accepts the six working answers.
**Answer:** "Approved as written." The document is approved on 2026-09-29, and all six
working answers are accepted: a release is a new `version` in `pyproject.toml`; the
changelog starts with one `0.1.0` entry under an empty Unreleased section; the "Keep a
Changelog" 1.1.0 layout; the maintainer keeps it current with no new `CONTRIBUTING.md`
rule; the README link follows the checklist sentence; `0.1.0` is dated 2026-09-17.

### 8. Decomposition review
**Asked:** Two delivery issues in the Prototype milestone — "Record version 0.1.0 in a
changelog at the repository root" (Urgent, FR-001 to FR-005, `CHANGELOG.md` only) and
"Link the changelog from the README" (High, FR-006 and FR-007, `README.md` and the setup
record) — with no blocked-by relation. Linear writes: read the project and adopt its
milestones and review issues, write `tracker.md`, create the two issues, relate each to
both request issues, and add one comment to each request issue. Adjust, or approve as-is?
**Answer:** "Approve as-is, except skip step 5: add no comments to the request issues."
The request issues get no comment; everything else proceeds as proposed.

### 9. Tracker population result
**Asked:** (No question — record of what the approved decomposition wrote.)
**Answer:** Created MAX-74 "Record version 0.1.0 in a changelog at the repository root"
(Urgent) and MAX-75 "Link the changelog from the README" (High), both in the Prototype
milestone of P-MAX-13 in Backlog, each related to MAX-72 and MAX-73. No blocked-by
relation, and no comment on either request issue, as instructed.
