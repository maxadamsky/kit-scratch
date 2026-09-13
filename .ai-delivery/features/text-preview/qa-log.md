# Q&A log — Text preview

Questions and answers behind the text preview feature's requirements. The log keeps each
decision traceable to the answer that settled it, so a reader who was not in the session
can see why the requirements say what they say.

- Feature folder: `.ai-delivery/features/text-preview/`
- Linear project: Text preview (`4c1e19e7-c231-4a35-a34a-fb759cae57c7`)
- Started: 2026-09-13

## Exchanges

### 1. How to start
**Asked:** Start with a guided interview, or import an existing requirements document?
**Answer:** Guided interview.

### 2. Type of work
**Asked:** Is this a new feature, an enhancement, internal tooling, an integration, or something else?
**Answer:** New feature — a capability that does not exist today.

### 3. Feature name
**Asked:** Use `text-preview` as the feature name for file naming and tracking, or a different name?
**Answer:** Use `text-preview`.

### 4. Core problem
**Asked:** What is broken, slow, or missing today, and what do users do as a workaround?
**Answer:** There is no way to see what a text file contains without opening it in an editor, so finding the right file means opening files one by one. Opening files just to look at them also risks changing them by accident.

### 5. Users and stakeholders
**Asked:** Who are the primary users, who signs off, and which other teams are affected?
**Answer:** Primary users are anyone browsing files, typically data analysts. The maintainer signs off. No other teams are affected.

### 6. Business goals
**Asked:** What business goals or outcomes are you hoping for (1–3)?
**Answer:**
1. A file's opening lines are visible without opening an editor.
2. The preview cannot change the file.
3. The preview shows the file as it is right now.

### 7. Scope boundaries
**Asked:** What must the first release include, and what is explicitly excluded?
**Answer:** Must include: showing the first lines of a single text file; read-only behaviour; a plain note when the file is empty or is not text. Explicitly excluded: editing, previewing more than one file at once, and previewing non-text files.

### 8. Additional context
**Asked:** Anything else to know — data sources, constraints, deadlines, prior art, links?
**Answer:** Nothing.

### 9. Intake summary
**Asked:** Does the intake summary (feature, type, problem, users, goals, in scope, out of scope, context) look right as the foundation for the requirements?
**Answer:** Looks good — proceed to preferences and drafting.

### 10. Document depth
**Asked:** Full 10-section requirements with a review cycle, or a Lite 4-section document?
**Answer:** Lite — problem and context, scope, units of work, and requirements.

### 11. Tracker population
**Asked:** Break the requirements into units of work and create them in Linear at the end, after reviewing the breakdown?
**Answer:** Yes — create the milestones and issues in Linear after review.

### 12. Requirements approval
**Asked:** Does the Lite requirements document look right? Every requirement (5 of 5) and both units are Urgent, above the skill's 60% guideline — approve as drafted, lower Unit 2 to High, or revise?
**Answer:** Approve as drafted — all priorities stay Urgent.

### 13. Move to decomposition
**Asked:** Requirements are complete (UX ideation skipped because the work has no screens). Move on to breaking the requirements into units of work for Linear?
**Answer:** Start decomposition — nothing is created in Linear before the breakdown is approved.

### 14. Decomposition approval
**Asked:** Approve the proposed breakdown — two independent Urgent units, both at the Shaped stage with no dependencies: "Preview the opening lines of a text file" (FR-001 to FR-003) and "Say plainly when a file is empty or not text" (FR-004, FR-005) — or adjust a phase, merge or split units, or change priorities or dependencies?
**Answer:** Approve as-is.

### 15. Milestone set option
**Asked:** The project already has three milestones, in order: Shaped, Editorial review, Specified (none has a description). Choose one option for the whole set — 1, keep them untouched and map existing names to stages; 2, adopt the delta, mapping existing names and creating only unmapped stages; or 3, replace, using the kit's stage names without mapping, reusing exact name matches and creating missing names — and give any mapping changes.
**Answer:** Option 3, replace. Use the kit's stage names without mapping: reuse the existing "Shaped" and "Specified" by exact name, create Prototyped, Handed off, Built and Shipped, and leave "Editorial review" untouched and unused.

### 16. Milestone set approval
**Asked:** Approve the whole resulting set — Shaped and Specified reused by exact name; Prototyped, Handed off, Built and Shipped created in that order, each with its stage meaning and who moves issues into it; Editorial review untouched and unused; resulting order Shaped, Editorial review, Specified, Prototyped, Handed off, Built, Shipped?
**Answer:** Approve this set.

### 17. Milestone description wording
**Asked:** The created Handed off milestone's description adds a clause that was not in the approved text ("asking engineering to take the work"), and Prototyped's description is reworded with the same meaning; both stay as created. Continue creating Built and Shipped with exactly the approved text, or stop here?
**Answer:** Continue as approved.

### 18. Build handoff
**Asked:** Hand text preview off to build for implementation now? Build reads the Linear project and the requirements document; nothing is copied.
**Answer:** No — pick it up later.

### 19. Sharing the requirements
**Asked:** Keep the requirements document in its repository home, or export a snapshot copy to the project root for sharing?
**Answer:** Keep as-is — the repository file is the only home.

## Open decisions

Four decisions stay open, recorded in the requirements document: how many opening lines a
preview shows; how a file is judged to be text or not text; how a person asks for a
preview and where it is shown; and what a person sees when a file cannot be read. The
maintainer owns all four and must settle them before build starts.
