# Q&A log — Scratch notes 3.0.2 live proof

Questions and answers behind the scratch-notes discovery. The log keeps each decision
traceable to the answer that settled it, so a reader who was not in the session can see
why the framing and the brief say what they say.

- Feature folder: .ai-delivery/features/scratch-notes/
- Linear project: Scratch notes 3.0.2 live proof (P-MAX-15,
  https://linear.app/max-test-workspace/project/scratch-notes-302-live-proof-bd6ecd9d3df9), lead Max Adamsky
- Started: 2026-09-29
- Entry point: discover — a new topic, framed by guided interview.

## Exchanges

### 1. Topic
**Asked:** Start a new topic or revisit a finished one?
**Answer:** New topic: "A small command-line tool, scratch-notes, that reads a Markdown
notes file and prints three things: the count of open checklist items, the list of
headings, and the same summary as JSON when given --json."

### 2. Linear tracking
**Asked:** No project named Scratch notes 3.0.2 live proof exists in team MAX. Create one, name an existing
one, or run untracked?
**Answer:** Create "Scratch notes 3.0.2 live proof", with Max Adamsky as lead. Created as P-MAX-15, unattached
(no initiative is bound), with the five stage milestones and five gate issues (`MAX-92`
Discovery review through `MAX-96` Release review), each read back after writing. Project
status moved from Backlog to Discovery and read back.

### 3. Who is affected
**Asked:** Who experiences this problem — who keeps or reads the notes files, is anyone
affected differently (for example a script consuming the JSON), and roughly how many people
and files?
**Answer:** Just me. I keep about ten Markdown notes files across my own projects, and nobody
else reads them. I read the plain output in the terminal. The JSON would only feed my own
shell scripts; no other tool reads it.

### 4. Pain points — what's broken today
**Asked:** What happens today when you want to know what's open or what's in a notes file,
where does it break down, and when does it bite?
**Answer:** Today I grep for "- [ ]" and skim the headings by eye. It breaks down in two ways:
grep also counts checked items when the spacing varies, so I get the count wrong, and doing
it file by file is slow. It bites most when I switch projects and want to know what's still
open in that project's notes. My scripts can't get the count at all today without me writing
a fragile grep.

### 5. The opportunity
**Asked:** If this were solved well, what would be different — what could you do on switching
into a project, what would you stop doing, and what would your scripts do with a reliable
count?
**Answer:** When I switch into a project I'd run one command on its notes file and trust the
open-item count and see the headings right away. I'd stop hand-writing grep patterns and
opening files to check. My scripts would read the --json output to show the open count in my
shell prompt. That's all; nothing fails a check and nothing lists across projects.

### 6. Constraints
**Asked:** What constraints apply — technical (this repo, uv, pytest, dependencies),
prompt performance and error behaviour, which checklist forms count, and anything that must
not be done?
**Answer:** It lives in this repo and uses the existing uv and pytest setup. No new
dependency: standard library only, no Markdown parser. It must be fast enough for the prompt
to call on every draw, and it must never print errors into the prompt: errors go to stderr
with a non-zero exit, so my script can ignore them. Checklist forms: "- [ ]", "* [ ]" and
"+ [ ]", including indented and nested items; numbered items don't count. The one thing it
must never do is change a notes file.

### 7. Prior art
**Asked:** Has this been tackled before — anything tried besides grep, tools seen or ruled
out, or anything already in this repository?
**Answer:** Nothing beyond grep. I haven't tried or ruled out any other tool. I don't know of
anything in this repo that does this.

### 8. Success signal
**Asked:** Six months on, with this solved, what would you see or check that tells you it
worked, and when would you notice?
**Answer:** The count in my prompt always matches what I'd get counting by hand, and I
haven't written a grep pattern for this since. I'd notice it every time I switch projects: I
glance at the prompt, see the open count, and trust it without opening the file.

### 9. Framing review
**Asked:** Does the framing summary accurately reflect the problem — proceed, or adjust?
**Answer:** "1" — looks good. Saved as framing.md.

### 10. Preferences and Discovery plan
**Asked:** (a) After a direction is chosen, run an independent risk pass on it? (b) What
does completing Discovery mean for this project — stakeholder sign-off, research complete
with success measures written, or both? (c) Which discovery work gets a Linear issue in the
Discovery milestone?
**Answer:** (a) Yes, red-team it. (b) Research complete with success measures written.
(c) Research only: one issue covering the exploration, the direction choice and the
decision brief. No spike, stakeholder session or presentation.
Q&A logging and the five-member council came from config and were not asked.

### 11. Linear write failure on the research issue
**Asked:** Creating the Discovery research issue failed twice with a 503 from Linear; the
project was checked after each failure and held no such issue. Retry now, explore first and
create later, or wait?
**Answer:** "1" — retry now. The retry succeeded: `MAX-97`, "Explore solution directions for
scratch-notes and write the decision brief", in the Discovery milestone, read back.

### 12. Exploration synthesis review
**Asked:** Ready to move to direction setting?
**Answer:** "Yes."

### 13. Premise challenge and direction choice
**Asked:** Null argues the untrustworthy count is a grep quoting mistake, not a missing tool,
and proposes fixing the pattern and checking it against a hand count instead of building.
The check showed the diagnosis holds but the named fix (fixed-string grep) found 2 of 5 open
items. Accept or decline? If declining, which direction: A (standard-library script run by
path), B (installed command), C (adopt mdq), D (anchored grep, no tool), or a combination?
**Answer:** "Decline: the tool stays small. Direction A: one standard-library script plus a
test, run by path from this repo with python3."

### 14. Trade-off: silent errors or a visible failure marker
**Asked:** Keep errors silent (stderr and non-zero exit, nothing in the prompt), or have the
prompt script show a marker such as "?" on a non-zero exit plus a version field in the JSON?
**Answer:** "B without the version field: my prompt script shows "?" when the script exits
non-zero, the tool itself still never prints into the prompt, and the JSON stays as small as
it is."

### 15. Trade-off: checkbox and heading lines inside fenced code blocks
**Asked:** Count every matching line including inside code blocks (plain line rule), or skip
lines inside fenced code blocks, with a rule for unclosed fences? Do the notes contain fenced
code with "- [ ]" or "#" lines?
**Answer:** "Sometimes, yes. B: skip lines inside fenced code blocks, both ``` and ~~~. An
unclosed fence is an error: the tool exits non-zero, so my prompt shows "?". Headings inside
code blocks don't count either."

### 16. Definition: which near-miss checkbox forms count as open
**Asked:** Proposed default: open = any indentation (spaces or tabs), then "-", "*" or "+",
then one or more spaces or tabs, then exactly "[ ]". Not open: "[x]", "[X]", "[-]". Not a
checkbox: "- []", "- [  ]", "-[ ]". CRLF line endings accepted. Where is it wrong?
**Answer:** "Your default is right. Use it as written."

### 17. Scope sketch
**Asked:** Command shape, heading definition and display, JSON field names, and what else is
explicitly out of scope?
**Answer:** "Yes: python3 scratch_notes.py <file> [--json], one file per run. Headings: only #
to ###### lines outside fences, not the underlined style, shown as written with their #
marks, so the structure stays visible. JSON: {"open": N, "headings": [...]} with those names,
each heading a string as written with its # marks. Also out of scope: colour, watch mode,
reading stdin, and any config file."

### 18. Success criteria
**Asked:** Draft criteria — (1) the open count equals a hand count on real notes files,
including ones with fenced code; (2) no grep pattern written for open items since; (3) the
prompt shows a number or "?", never error text; (4) fast enough not to notice, measurably
under 50 ms per call on the largest notes file. Do these capture it; keep 4 measurable?
**Answer:** "These capture it. Keep criterion 4 as the measurable version: under 50 ms per
call on my largest notes file."

### 19. Direction-specific constraints
**Asked:** Keep, drop or add to five candidate constraints: a python3 -I test proving
standard-library only; runs on the python3 on PATH (3.11 or newer); only regular files are
opened, anything else is an error with non-zero exit; accepted that a branch without the
script shows "?"; CONTRIBUTING.md item 3 updated when the first test lands.
**Answer:** "Keep all five as written. Nothing to add."

### 20. Direction rationale
**Asked:** Why Direction A over the alternatives?
**Answer:** "The tool stays small, and A is the smallest option that still gives a count I can
trust, the headings and JSON. Grep gives no JSON or headings, an installed command adds a
build step I don't need, and mdq breaks the standard-library rule."

### 21. Direction summary review
**Asked:** Does the direction summary capture it — record it and move to the risk pass, or
change something?
**Answer:** "1" — looks good; recorded as the Chosen Direction in exploration-synthesis.md and
moving to the risk pass.

### 22. Decisions from the risk challenge
**Asked:** Settle any of six decisions the risk pass surfaced now, or carry them into the
brief as open: (1) a fixed interpreter path instead of python3; (2) the standard-library test
runs with -I -S; (3) exact fence rules and whether an unclosed fence stays an error while
editing; (4) the per-project notes-file convention; (5) accept that a broken edit breaks every
prompt; (6) the 50 ms measured end to end as the prompt calls it.
**Answer:** "Settle two now: 2, yes, the standard-library test runs with -I -S. 6, yes, the
50 ms is measured end to end, the way the prompt calls it. Carry 1, 3, 4 and 5 into the brief
as open questions, and go straight to the brief."
Recorded: the Chosen Direction's constraint and criterion 4 updated to match.

### 23. Brief review
**Asked:** Does the brief capture the outcome — finalize, or change something?
**Answer:** "1. Finalize it, then stop here: don't start shape in this session."

## Shape exchanges

Shape started 2026-09-30 from the discovery brief (entry point: discover). Numbering
continues from the discovery exchanges above.

### 24. Feature to shape
**Asked:** Which feature should shape work on — scratch-notes (discovery finished, no
requirements yet), a new feature, or a revision to a finished one?
**Answer:** "scratch-notes."

### 25. Intake summary from the brief
**Asked:** Does the summary extracted from the brief look right, and should the six open
questions from the brief be answered now, or drafted as flagged assumptions?
**Answer:** "Looks good, draft now." The six open questions go into the requirements as
`[ASSUMPTION]` items, to be settled in review.

### 26. Document depth and Linear population
**Asked:** Full (10 sections with review) or Lite (4 sections) requirements document? And
after approval, decompose into units of work and create them as issues in project P-MAX-15?
**Answer:** "Lite." "Yes, create them." Recorded as `Decomposition: planned` in the
requirements header.

### 27. Requirements approval
**Asked:** Approve the Lite requirements document as written (all seven working answers
accepted, headings at Medium), approve with headings at High, or revise?
**Answer:** "Approve as written." Header set to `Status: approved (2026-09-30)`; open
questions 1–7 closed on their working answers.

### 28. Decomposition review
**Asked:** Create the proposed two issues (the whole script as one, and the `CONTRIBUTING.md`
update as the other), adjust them, or write nothing to Linear?
**Answer:** "Split the script into three units, one per printed item: the open count, the
headings, and the --json output. I accept that they share scratch_notes.py. Keep the
CONTRIBUTING.md change as its own unit or fold it into one of those, whichever you judge
better, but no more than four units in total."
Recorded: the `CONTRIBUTING.md` change was kept as its own unit, making four units in all.
Section 3 of the requirements was revised as a Moderate rework dated 2026-10-01: FR-001's
`--json` form moved to FR-007, and FR-008's heading lines became the new FR-016. The unit
titles are now: Count the open checklist items in a notes file; List the notes file's
headings under the count; Give the shell prompt the count and headings as JSON; Tell
contributors that `uv run pytest` now runs real tests.

### 29. Revised decomposition approval
**Asked:** Create the four issues (count, headings, JSON and `CONTRIBUTING.md`), with
headings blocked by count and JSON blocked by count and headings?
**Answer:** "Approve as-is." Created MAX-98, MAX-99, MAX-100 and MAX-101 in the Prototype
milestone of P-MAX-15, with three blocked-by links, and moved the project from Discovery
to Ready because the Discovery review gate issue was closed. Header set to
`Decomposition: populated (2026-10-01)`.
