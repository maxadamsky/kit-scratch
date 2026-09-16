# Q&A log — Reader text size

Every question put to the requester during this feature's shaping, with the answer as
given. Kept because `qa_log` is on in `.ai-delivery/config.md`.

**Feature:** reader-text-size
**Entry point:** triage (approved request group from `/ai-delivery:triage`)
**Source requests:** MAX-30
**Date:** 2026-09-15

---

## Triage sitting

**Q (intake invitation):** Do you have any additional requests to bring into this
sitting? Paste the text, name a file path, or say you have none.

**A:** "I have nothing to bring in."

---

**Q (grouping):** Here is the whole grouping. Move requests between groups, change the
primary, and mark each group shape now or leave. What should change?

Grouping as proposed: Group A — MAX-29, standalone, shape now. Group B — MAX-30,
standalone, shape now.

**A:** "Change group A, MAX-29, to leave. Group B, MAX-30, stays shape now. Show me the
resulting set."

---

**Q (whole-set approval):** Do you approve this whole grouping? (Resulting set: Group A —
MAX-29 — leave; Group B — MAX-30 — shape now.)

**A:** "I approve this whole set as shown."

---

## Shape Phase 0 — Path D intake

**Q (extraction confirmation):** Does this extraction look right? 1. Looks good —
proceed to preferences and requirements document generation. 2. I need to correct
something. 3. Fill the gaps now — ask me about the missing items.

Extraction presented: feature name `reader-text-size`; problem statement; users; business
goals [NOT FOUND]; in scope; out of scope [NOT FOUND]; additional context. Gaps listed:
cross-device behaviour, which text sizes exist and which is default, first-ever-open
behaviour, no success measure or scope exclusions stated.

**A:** "1"

Gaps were therefore not filled by question; they are carried as Open Questions and as a
stated scope exclusion in the requirements document rather than as invented answers.

---

## Shape — Initial Preferences Setup

Not asked, taken from `.ai-delivery/config.md`: `qa_log: on` (this log exists because of
it) and `ui_facing: false` (Phase 2 UX ideation skipped, noted in the requirements
header). Framework was not asked because it is only asked for UI-facing work.

**Q (document depth):** What level of detail do you need for this requirements document?
1. Full requirements document. 2. Lite requirements document.

**A:** "Lite"

---

**Q (tracker population):** Would you like me to decompose the requirements into units of
work and create them in Linear at the end? You'll review the decomposition before
anything is created. 1. Yes. 2. No.

**A:** "Yes"

Recorded as `Decomposition: planned` in the requirements header.

---

## Shape Phase 1A — document approval

**Q (Lite document approval):** Do you approve this document? (Summary and path given in
the terminal; body not pasted.)

**A:** "Approved"

Recorded as `Status: approved (2026-09-15)`. Notion publication was declined for this
session, so this repository file is the document's home.

---

## Shape Phase 3 — decomposition review

**Q (decomposition review):** Here's the proposed decomposition — two delivery issues
(Unit 1 "Keep the chosen reading text size across reader sessions", Shaped, Urgent,
covers FR-001 and FR-002; Unit 2 "Open at the default size when no kept size is
available", Shaped, Medium, covers FR-003 and FR-004, depends on Unit 1), plus the
proposed request writes for MAX-30 (move Triage to Backlog, attach to the destination
project, keep its description, then one comment linking the project and the delivery
issues). Would you like me to adjust it? 1. Correct a unit's demonstrated phase or
milestone role. 2. Merge or split units. 3. Change priorities or dependencies.
4. Approve as-is — I'll run the project gate before any Linear write.

**A:** "4"

---

## Shape Phase 3 — project gate

**Q (project decision):** Proposed project name "Reader text size", to be created in the
Max-test-workspace team. 1. Confirm the name. 2. Edit the name. 3. Create nothing.

**A:** "3"

Outcome: create nothing. No project was created and no source request moved. No
milestones, delivery issues, relations, request writes, comments or `tracker.md` were
written, and `Decomposition:` was set to `declined (2026-09-15)`.

---

## Shape — build handoff offer

**Q (build handoff):** Would you like to hand this off to build for implementation?
1. Yes — continue into build. 2. No — I will pick it up later.

**A:** "2"

Shaping ended here. No build was started, and this session created nothing in Linear.
