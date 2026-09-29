# Problem Framing: scratch-notes

**Created:** 2026-09-29
**Status:** Completed
**Profile:** software (of config: software)
**Project:** P-MAX-14 (Scratch notes)
**Risk challenge:** requested
**Discovery issues:** MAX-81 (Explore solution directions for scratch-notes and write the decision brief)
**Council roster:** constraint, precedent, stress, null, operator (of: constraint, precedent, stress, null, operator)

## Raw Description

A small command-line tool, scratch-notes, that reads a Markdown notes file and prints three
things: the count of open checklist items, the list of headings, and the same summary as JSON
when given --json.

## Who Is Affected

- One person: the developer who keeps about ten Markdown notes files across their own
  projects. Nobody else reads these files.
- The developer reads the plain output in the terminal.
- The developer's own shell scripts are the only machine consumer: they would read the JSON
  to show the open count in the shell prompt. No other tool reads it.

## Pain Points — What's Broken Today

- Today the developer greps for "- [ ]" and skims the headings by eye.
- The count is wrong: grep also counts checked items when the spacing varies, so the number
  cannot be trusted.
- It is slow: the check is done file by file.
- It bites most when switching projects, at the moment the developer wants to know what is
  still open in that project's notes.
- Scripts cannot get the count at all today without a hand-written, fragile grep.

## The Opportunity

- On switching into a project, one command on that project's notes file gives an open-item
  count the developer trusts, and shows the headings straight away.
- The developer stops hand-writing grep patterns and stops opening files to check.
- The developer's scripts read the --json output to show the open count in the shell prompt.
- That is the whole scope: nothing fails a check on the count, and nothing lists across
  projects.

## Constraints

- Lives in this repository and uses its existing uv and pytest setup.
- No new dependency: Python standard library only, no Markdown parser.
- Fast enough for the shell prompt to call on every draw.
- Never prints errors into the prompt: errors go to stderr with a non-zero exit, so the
  calling script can ignore them.
- Open checklist items are lines using "- [ ]", "* [ ]" or "+ [ ]", including indented and
  nested items. Numbered items do not count.
- Must never change a notes file.

## Prior Art and Context

- Nothing beyond grep. No other tool has been tried or ruled out.
- The developer knows of nothing in this repository that does this.

## Success Signal

- The count in the shell prompt always matches a count done by hand.
- The developer has not written a grep pattern for this since.
- Noticed every time the developer switches projects: a glance at the prompt shows the open
  count, and it is trusted without opening the file.
