# Q&A log — Notebook export

This log records each question asked while shaping the notebook export requirements and the answer given, so anyone who picks the work up later can see how each decision was reached.

## 2026-09-13

1. **How to start the requirements document.** Options offered: a guided interview, or importing an existing document.
   **Answer:** Guided interview.
2. **Type of work.** Options offered: new feature, enhancement, internal tooling, integration, or other.
   **Answer:** New feature.
3. **Feature name for file naming and tracking.** Proposed: notebook-export.
   **Answer:** Use notebook-export.
4. **What problem this solves: what is broken, slow, or missing today, and the current workaround.**
   **Answer:** A notebook's cells and their outputs can only be seen inside the notebook app, so there is no way to hand someone a single document of what the notebook did. Today people take screenshots or copy cells into a separate document by hand, and the outputs go stale the moment the notebook is re-run.
5. **Who is involved: primary users, stakeholders, and affected teams.**
   **Answer:** Primary users: notebook authors, typically data analysts, and the colleagues they share results with. Stakeholders: the maintainer signs off. Affected teams: none.
6. **Business goals or outcomes (one to three).**
   **Answer:** (1) Share a notebook's results as one file without screenshots or manual copying. (2) The exported file always reflects the run it was exported from, with each output next to its cell. (3) The file opens without the notebook app installed.
7. **Scope boundaries: what the first release must include, and what is explicitly excluded.**
   **Answer:** Must include: export a single notebook's cells and outputs to one file; outputs placed next to their cells in order; the file readable without the notebook app. Explicitly excluded: editing the exported file, exporting more than one notebook at a time, any cloud or shared-drive upload, and any format other than the one chosen for the first release.
8. **Anything else to know: data sources, format constraints, deadlines, or links.**
   **Answer:** Nothing.
9. **Whether the intake summary (feature, type, problem, users, goals, in scope, out of scope, context) is right.**
   **Answer:** Looks good.
10. **Level of detail for the requirements document.** Options offered: a full ten-section document with a section-by-section review, or a lite four-section document (problem, scope, units of work, requirements).
    **Answer:** Lite document.
11. **Whether to decompose the requirements into units of work and create them in Linear, after reviewing the decomposition.**
    **Answer:** Yes, create in Linear.
12. **Whether the lite requirements document is right as drafted** (three units of work; five requirements, of which three are Urgent, one High and one Medium; three assumptions and three open decisions owned by the maintainer).
    **Answer:** Approve as drafted.
13. **Whether to proceed from the approved requirements to decomposition,** with the unit breakdown reviewed before anything is written to Linear.
    **Answer:** Proceed to decomposition.
14. **Whether to adjust or approve the proposed decomposition:** three units — export a notebook and its text outputs to one shareable file (Urgent; FR-001 to FR-003), include image and chart outputs (High; FR-004, blocked by the first unit), and show a note where an output cannot be displayed (Medium; FR-005, blocked by the first unit) — each proposed at the Shaped phase.
    **Answer:** Approve as-is.
15. **How this project's existing milestones (Shaped, Editorial review, Specified, in that order, none with a description) fit the kit's six shared stages.** Options offered: keep theirs untouched and map existing names; adopt the delta by mapping existing names and creating the unmapped stages; or replace by reusing exact name matches and creating the missing names.
    **Answer:** Option 1, keep theirs untouched. The existing "Shaped" is the Shaped stage; the existing "Specified" is the Specified stage; "Editorial review" maps to no stage and stays as it is. Prototyped, Handed off, Built and Shipped stay absent. Create nothing.
16. **Whether to approve the resulting milestone set:** Shaped and Specified mapped to the existing milestones of those names, the other four stages absent, Editorial review untouched and unused, nothing created in Linear, and the mapping recorded in the delivery config.
    **Answer:** Approve this set.
17. **Whether to hand notebook export off to build for implementation,** with build reading the Linear project and the requirements document rather than copies.
    **Answer:** No, pick it up later.
18. **How to share the requirements document,** kept in this repository at .ai-delivery/features/notebook-export/requirements.md. Options offered: keep it as-is, or export a snapshot copy to the project root.
    **Answer:** Keep as-is.

Three decisions recorded in requirements.md remain open: the export file format, which notebook file format the export reads, and how an export is started. The maintainer owns all three and needs to make them before build starts.
