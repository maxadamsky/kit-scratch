---
schema_version: 1
generated_on: 2026-09-12
regenerated_on: null
---

# Q&A Log — Repository usage documentation

This log records every question the shape skill asked while defining requirements for
repository usage documentation, with the answer given. It lets a reader who was not in
the session see where each requirement came from.

## 2026-09-12 — Intake

1. **Q:** How would you like to get started: a guided interview, or importing an
   existing document?
   **A (Max):** Guided interview.
2. **Q:** What type of work is this?
   **A (Max):** New feature — a net-new capability that doesn't exist today.
3. **Q:** Should the feature be named `repository-usage-documentation` (the short name
   used for the feature directory and tracking), or something else?
   **A (Max):** Keep the name.
4. **Q:** What problem does this solve? What is broken, slow, or missing today, and what
   do people have to do instead?
   **A (Max):** kit-scratch has no usage documentation: the README is a two-line note that
   says it is a scratch repository and names an old kit version, so anyone opening it
   cannot tell what it is for, which branches are evidence, or how the ai-delivery kit is
   exercised in it. Today they have to read the ai-delivery-kit repository's runbooks to
   work that out.
5. **Q:** Who are the key people involved: primary users, stakeholders who sign off, and
   any affected teams?
   **A (Max):** Primary users: the kit maintainer (Max) and any first external recipient
   of the ai-delivery kit who opens kit-scratch to see a worked example. Stakeholders: the
   kit maintainer signs off. Affected teams: none; the repository is a fixture, not a
   product.
6. **Q:** What business goals or outcomes are you hoping for? (1–3 goals)
   **A (Max):**
   1. A first-time reader can tell what kit-scratch is for, and that it is a fixture
      rather than a product, from the README alone.
   2. The evidence branches and their pull requests are listed with one line each saying
      which runbook created them and why they stay unmerged.
   3. The README states the kit version the repository was last exercised against and
      where the kit's own records for that are.
7. **Q:** What must the first release include, and what is explicitly excluded?
   **A (Max):** Must include: a rewritten README.md with a purpose statement, a table of
   evidence branches and pull requests with one line each, and the kit version last
   exercised with a pointer to the kit repository's runbooks. Explicitly excluded: any
   change to the .ai-delivery directory, any edit to the evidence branches or their pull
   requests, any documentation beyond the single README, and any automation that
   regenerates the README.
8. **Q:** Anything else I should know (data sources, constraints, timeline, links)?
   **A (Max):** Branch and pull request facts come from the repository itself (git branch
   list and the open pull requests on GitHub), not from the kit's ledgers. Tone plain,
   length under one screen, plain Markdown, no em dashes. No timeline pressure. Point at
   the ai-delivery-kit repository by name only; do not link individual runbooks.
9. **Q:** Does the intake summary (feature, type, problem, users, goals, in scope, out of
   scope, additional context) look right as the foundation for the requirements document?
   **A (Max):** Looks good.

## 2026-09-12 — Preferences

10. **Q:** What level of detail do you need for this requirements document: Full
    (10 sections with a review cycle) or Lite (4 sections: Problem, Scope, Units of Work,
    Requirements)?
    **A (Max):** Lite requirements.
11. **Q:** Should the requirements be decomposed into units of work and created in Linear
    at the end (after review of the decomposition), or kept as a requirements document
    only?
    **A (Max):** Yes, create the Linear project, milestones, and issues.

Not asked, because the project record already answers them: Q&A logging (`qa_log: on` in
`.ai-delivery/config.md`), UI-facing work (`ui_facing: false`), and framework (only asked
for UI-facing work).

## 2026-09-12 — Requirements approval

12. **Q:** Here's the Lite requirements document (`requirements.md` in this directory).
    Does this look right, or would you like me to revise anything?
    **A (Max):** Looks good.
13. **Q:** All three requirements (purpose statement, evidence table, kit version) are
    marked Urgent because each was named as must-include, and the guideline says to
    reconsider when more than 60% are Urgent or High. Should any be lower?
    **A (Max):** Kit version to High (Unit 3 and FR-003 become High).

## 2026-09-12 — Decomposition

14. **Q:** The requirements are approved, UX ideation is skipped (not UI-facing), and the
    work is to be created in Linear. Ready to move to decomposition, with the units proposed
    in chat before anything is created?
    **A (Max):** Proceed to decomposition.
15. **Q:** Proposed decomposition: three issues. Unit 1 "Explain what kit-scratch is for
    in the README" (Urgent, covers FR-001, the foundation); Unit 2 "List evidence branches
    and their pull requests in the README" (Urgent, covers FR-002, blocked by Unit 1);
    Unit 3 "State the kit version kit-scratch was last exercised against" (High, covers
    FR-003, blocked by Unit 1). All three at the Shaped milestone role, because the
    approved requirements agree the problem and scope boundary and no per-unit
    specification exists yet. All three edit README.md, so build runs Units 2 and 3 one
    after another. Approve, merge into one unit, correct a milestone role, or change
    priorities or dependencies?
    **A (Max):** Approve as-is. This settles the requirements open question on the shared
    file: three units, built one after another after Unit 1.
16. **Q:** No tracker exists and config records no initiative (`initiative_id: null`), so
    the work would be created outside an initiative with no overlap check. Create a Linear
    project in team MAX (Max-test-workspace) named "Repository usage documentation", edit
    the name, or create nothing?
    **A (Max):** Create as named.
17. **Q:** The new project has no milestones. Choose one option for its whole milestone
    set: keep theirs untouched (create nothing), adopt the delta (create every unmapped
    role), or replace (use the shared stage names). With no existing milestones, options 2
    and 3 both create Shaped, Specified, Prototyped, Handed off, Built and Shipped, in that
    order, each with its stage meaning and who moves issues into it in its description.
    **A (Max):** Adopt the delta, approving all six milestones as shown.

## 2026-09-12 — Handoff and sharing

18. **Q:** Hand this off to build for implementation now? Build reads the Linear project
    for what to build and the requirements document for context; nothing gets copied.
    **A (Max):** No, pick it up later.
19. **Q:** The requirements document is saved at `requirements.md` in this directory. Keep
    it as-is, or export a snapshot copy to the project root for sharing?
    **A (Max):** Keep as-is.

## Open actions

Requirements are approved and the work is in Linear as three issues. One decision remains
open: which source establishes the kit version last exercised (FR-003, the kit-version
requirement, tracked in Linear as MAX-18). Max owns it, before build starts on that issue.
