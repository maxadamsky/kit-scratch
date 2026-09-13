# Q&A log — Folder summary

Requirements for a folder summary: a quick view of what a folder holds. This log records
each question the shape skill asked while writing those requirements, and the answer
given, so a later reader can see why the requirements say what they do.

Answers are Max Adamsky's, given in the shape session of 2026-09-13.

## 1. How to start

- **Question:** Start with a guided interview, or import an existing requirements document?
- **Answer:** Guided interview.

## 2. Type of work

- **Question:** What type of work is this — new feature, enhancement, internal tooling,
  integration, or other?
- **Answer:** New feature — a capability that does not exist today.

## 3. Feature name

- **Question:** Use `folder-summary` as the name for file naming and tracking? It matches
  the existing feature directory and the Linear project "Folder summary".
- **Answer:** Use `folder-summary`.

## 4. Core problem

- **Question:** What problem does this solve — what is broken, slow, or missing today,
  and what do people do as a workaround?
- **Answer:** There is no quick way to see what a folder holds without opening it and
  looking file by file. Today people open the folder, count files by eye, and guess at
  total size and which file types make it up, which is slow and often wrong.

## 5. Users and stakeholders

- **Question:** Who are the primary users, who signs off or cares about the outcome, and
  which other teams are affected?
- **Answer:** Primary users are anyone browsing files, typically data analysts. The
  maintainer signs off. No other teams are affected.

## 6. Business goals

- **Question:** What business goals or outcomes are you hoping for? (1–3 goals)
- **Answer:**
  1. One glance shows a folder's file count, total size and the mix of file types.
  2. The numbers are correct for the folder as it is right now.
  3. Looking at a folder changes nothing in it.

## 7. Scope boundaries

- **Question:** What must the first release include, and what is explicitly excluded
  from this phase?
- **Answer:** Must include file count, total size and a breakdown by file type, for a
  single folder. Explicitly excluded: recursing into subfolders, editing or deleting
  files, and saving or exporting the summary.

## 8. Additional context

- **Question:** Anything else to know — data sources, compliance constraints, deadlines,
  prior art, or links?
- **Answer:** Nothing.

## 9. Intake summary

- **Question:** Does the intake summary (feature, type, problem, users, goals, in and out
  of scope, context) look right as the foundation for the requirements document?
- **Answer:** Looks good.

## 10. Document depth

- **Question:** Full 10-section requirements document with a review cycle, or a Lite
  4-section document (problem, scope, units of work, requirements)?
- **Answer:** Lite.

## 11. Tracker population

- **Question:** Decompose the requirements into units of work and create them in Linear
  at the end, after reviewing the decomposition?
- **Answer:** Yes — create the Linear project, milestones, and issues.

## 12. Requirements approval

- **Question:** Does the Lite requirements document look right? Raised with it: 5 of 6
  requirements and 2 of 3 units are Urgent, above the kit's guideline that no more than
  60% be Urgent or High; the type breakdown is assumed to count files per type; and
  Unit 3 with FR-006 (a plain message when a folder cannot be summarized) was added
  although not raised at intake.
- **Answer:** Approve as drafted.

## 13. Next phase

- **Question:** Requirements are approved and UX ideation is skipped (not UI-facing).
  Proceed to decomposition, where units and milestones are proposed for review before
  anything is created in Linear?
- **Answer:** Proceed to decomposition.

## 14. Decomposition

- **Question:** Approve the proposed decomposition, or adjust it? Proposed: three
  independent units, each at milestone role Shaped — "Show a folder's file count and
  total size" (Urgent; FR-001, FR-002, FR-004, FR-005), "Break a folder's files down by
  file type" (Urgent; FR-003) and "Say plainly when a folder cannot be summarized"
  (Medium; FR-006) — with no blocked-by links.
- **Answer:** Approve as-is.

## 15. Milestone set

- **Question:** The project already has Shaped, Editorial review and Specified, in that
  order, none with a description. Keep them untouched (option 1), adopt the delta —
  map existing names and create only the unmapped stages (option 2) — or replace with
  the kit's stage names (option 3)? Which stage does each existing milestone stand for?
- **Answer:** Option 2, adopt the delta. The existing "Shaped" is the shaped stage; the
  existing "Specified" is the specified stage; "Editorial review" maps to no stage and
  stays as it is. Create Prototyped, Handed off, Built and Shipped, in that order after
  the existing three.

## 16. Milestone set approval

- **Question:** Approve the whole resulting set: reuse Shaped and Specified, leave
  Editorial review untouched and unused, and create Prototyped, Handed off, Built and
  Shipped in that order, each with a description of the stage and who moves issues into
  it — resulting order Shaped, Editorial review, Specified, Prototyped, Handed off,
  Built, Shipped?
- **Answer:** Approve this set.

## 17. Build handoff

- **Question:** Hand folder summary off to build for implementation now? Build would read
  the Linear project and the requirements document; nothing is copied.
- **Answer:** No — pick it up later.

## 18. Sharing the requirements

- **Question:** Keep the requirements document in its repository home, or export a
  snapshot copy to the project root for sharing outside the repo tooling?
- **Answer:** Keep as-is.

## Open items

The folder summary requirements are approved and in Linear as MAX-22, MAX-23 and MAX-24
in the Folder summary project; build has not started. Three decisions remain open, and
the maintainer must make them before build starts:

- How a file's type is decided — by its name extension or by its contents — and how files
  with no extension are shown.
- Whether hidden files and links to other files count as files, and whether the summary
  mentions subfolders it did not look inside.
- How a person asks for a summary and sees it.

Max Adamsky picks up the build handoff later.
