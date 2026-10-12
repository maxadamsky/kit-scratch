## Council Response

**Evidence consulted:** none; reasoning from the framing only

### Failure Modes

**Failure mode 1: Process startup cost on every prompt draw**
- **Trigger:** The prompt calls the tool on every draw. At 100x that means many terminal panes, fast command loops, or a notes file 100x larger. The larger file matters least.
- **Mechanism:** Parsing even a multi-megabyte file line by line is cheap. The fixed cost of each call is not. A CPython cold start takes tens of milliseconds. If the prompt invokes the tool through `uv run` (an assumption, since the framing says only that the tool uses the repository's uv setup), each call may also resolve or sync the environment, adding more time before a single line is read. Locating the notes file could add more if it walks directories or globs, especially on network or synced mounts (also an assumption; the framing does not say how the file is found).
- **Consequence:** Every prompt draw lags visibly. The "fast enough for every draw" constraint fails on invocation overhead, not on parsing, so no parser optimisation fixes it.
- **Likelihood:** High
- **Impact:** High

**Failure mode 2: Checkbox and heading lookalikes in non-list contexts**
- **Trigger:** The notes contain ordinary Markdown in which checkbox or heading syntax is not a list item or a heading:
  - fenced or indented code blocks, such as a pasted README template or a shell script whose comment is `# install deps`
  - blockquoted items such as `&gt; - [ ]`
  - HTML comments
  - an unclosed ``` fence
- **Mechanism:** With no Markdown parser, a line-based matcher counts `- [ ]` inside code and lists `#` shell comments as headings. A matcher that does track fences has the opposite problem: one unclosed fence silences everything after it.
- **Consequence:** The count stops matching a hand count, which is the framing's single success signal. It can be too high (code samples counted) or too low (everything after a stray fence dropped).
- **Likelihood:** High
- **Impact:** High

**Failure mode 3: Spacing and marker variants the rule does not settle**
- **Trigger:** The same spacing variance that breaks grep today, including:
  - `- [  ]` (two spaces inside the box) and `- []`
  - tabs instead of spaces, and mixed tab/space nesting
  - `-[ ]` with no space after the marker
  - a non-breaking space pasted from a browser
  - CRLF line endings
  - checked states `[x]`, `[X]`, and `[-]`
- **Mechanism:** The framing names three markers followed by `[ ]` but does not say which near-misses count. Each implementation will pick silently, and the developer's hand count uses a different, unstated rule. An exact-match rule misses items that are obviously open. A loose rule counts `[-]` or malformed lines.
- **Consequence:** The trusted count diverges from the hand count on exactly the inputs that caused the original pain. **Open decision:** the developer must define the near-miss rule before building; until then no build can meet the success signal.
- **Likelihood:** High
- **Impact:** Medium

**Failure mode 4: A hostile or odd file target blocks or explodes**
- **Trigger:** The notes path resolves to something that is not a small UTF-8 text file:
  - a FIFO or a symlink to `/dev/zero` or `/dev/random`
  - a huge accidental file, such as a log renamed to `.md`
  - a file with non-UTF-8 bytes (a Latin-1 paste)
  - a UTF-8 byte-order mark on the first line
  - a directory
  - a file on an unresponsive network or cloud-synced mount
- **Mechanism:**
  - Reading a FIFO blocks forever; `/dev/zero` read whole exhausts memory.
  - A strict decode raises on the first bad byte.
  - A byte-order mark turns `# Title` into `﻿# Title`, so the first heading is missed.
  - A cloud placeholder file can trigger a download on open.
- **Consequence:** The prompt hangs or stalls instead of failing fast. The "errors go to stderr, prompt unaffected" constraint does not help, because a blocked read never produces an error at all.
- **Likelihood:** Low
- **Impact:** High

**Failure mode 5: Reading while the editor is saving**
- **Trigger:** The developer saves the notes file while one or more terminal panes are drawing their prompts. With many panes at 100x, this collision becomes routine.
- **Mechanism:** Editors that save by truncating and then rewriting in place (an assumption; this varies by editor and setting) leave a window in which the file is empty or partly written. The tool reads it without complaint because it is valid text.
- **Consequence:** For that draw the prompt shows a wrong count, often 0, without any error, so the developer sees a false "nothing open". The tool is read-only, so the file itself is not at risk.
- **Likelihood:** Medium
- **Impact:** Low

**Failure mode 6: Heading text that attacks the terminal or the JSON consumer**
- **Trigger:** Heading text contains ANSI escape sequences or other control characters (for example pasted terminal output), or text that looks like a JSON field, such as `"open": 0`.
- **Mechanism:** Plain-text output passes escape sequences straight to the terminal, where they can recolour output, move the cursor, or set the window title. `json.dumps` escapes these safely. But the prompt script is hand-written, and if it pulls the count out with grep or sed rather than a real JSON parser (an assumption), a heading containing `"open": 0` can be read as the count. JSON output also grows with the number of headings, yet the prompt reads it on every draw and needs only one integer.
- **Consequence:** Terminal output is corrupted, or the prompt shows a spoofed or garbled count taken from heading text.
- **Likelihood:** Low
- **Impact:** Medium

## Strongest Statement

The first thing to break is trust in the count, not speed of parsing. Failure modes 2 and 3 break it without any error: code fences, blockquotes, and spacing variants silently produce a number that differs from a hand count, and "matches a hand count" is the only success signal. Speed breaks second, on per-draw process and `uv` startup rather than on file size. Before any direction is chosen, the developer who owns this repository must decide two things: which near-miss checkbox forms count, and how the prompt invokes the tool without going through `uv run` on every draw.

**END OF RESPONSE. Do not add anything after this line.**
