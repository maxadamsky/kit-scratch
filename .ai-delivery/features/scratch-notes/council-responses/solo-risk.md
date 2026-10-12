## Risk Challenge Output

### Risks

**Risk 1: The `python3 -I` test does not prove standard-library-only**
- **Category:** Technical
- **Description:** `-I` (isolated mode) ignores environment variables and the user site-packages directory. It does not disable the `site` module, and it does not stop a virtual environment's own site-packages from being added to the import path. When pytest runs under uv, the test's `python3` is most likely the repository's venv interpreter. That venv already holds the Markdown parsing package that the brief names. An accidental `import markdown` would therefore still resolve, and the test would pass. The failure would appear only later, in the shell prompt, where a different `python3` lacks the package, and the prompt would show `?` in every project. This depends on how venv path setup behaves under `-I`, which the brief does not settle. I am treating it as a strong assumption, not a verified fact.
- **Likelihood:** High (that the test as specified proves less than it claims)
- **Impact if realized:** Medium
- **Mitigation signal:** Before relying on the test, the developer runs `python3 -I -c "import markdown"` inside the repository's venv. If it succeeds, the test must use `-S` or a non-venv interpreter, or assert against `sys.modules` after import.

**Risk 2: `python3` on PATH changes when the developer switches projects**
- **Category:** Assumption
- **Description:** The tool is meant to matter most at the moment of switching into a project. That is also when a project's virtual environment, pyenv version file, or uv shim is likely to become active and change what `python3` means. A project pinned to 3.9 or 3.10, or macOS's system `/usr/bin/python3`, falls below the 3.11 floor. The script then fails, and the prompt shows `?` in exactly the projects being entered. The constraint says `python3` "must be 3.11 or newer" but nothing enforces or pins it.
- **Likelihood:** High
- **Impact if realized:** Medium
- **Mitigation signal:** The developer decides whether the prompt calls a fixed absolute interpreter path rather than `python3`. The success check should then run the prompt inside at least one project that has its own activated environment.

**Risk 3: The 50 ms budget measures the wrong thing**
- **Category:** Technical
- **Description:** The success criterion times "each call on the developer's largest notes file". On a small Markdown file, interpreter startup dominates, not parsing. If `python3` resolves through a shim (pyenv and similar tools use shell-script shims), startup alone can exceed 50 ms before the script runs. The prompt draws on every command, so any overshoot is felt constantly. This is the kind of friction that makes a developer remove a prompt segment.
- **Likelihood:** Medium
- **Impact if realized:** High
- **Mitigation signal:** Measure end-to-end wall time of the prompt segment exactly as the prompt invokes it, warm and cold, inside a project with an active environment. Accept or reject the direction against that number.

**Risk 4: Fence handling produces silent miscounts or frequent `?`**
- **Category:** Technical
- **Description:** Two failure modes pull against each other:
  - **Too strict.** "An unclosed fence is an error" means that while the developer is mid-edit, with a fence opened and not yet closed, the prompt shows `?`. That happens in exactly the project being worked in.
  - **Too naive.** If fence detection ignores Markdown's rules, a fenced block can toggle wrongly. The rules it could miss are that a closing fence must use the same character and be at least as long as the opening, that fences can be nested inside list items, and that a `~~~` line inside a ```` ``` ```` block is not a fence. A wrong toggle inverts counting for the rest of the file and yields a confident wrong number, with no `?`.

  A silent miscount directly breaks the "always matches a hand count" signal, which is the whole reason the tool exists.
- **Likelihood:** Medium
- **Impact if realized:** High
- **Mitigation signal:** The developer settles the fence rules explicitly: which fence characters and lengths, whether indented fences count, and whether an unclosed fence is an error or "treat to end of file". The test file then includes nested, mismatched and in-list fences taken from the real notes files.

**Risk 5: The line rule and the developer's "hand count" may disagree**
- **Category:** Assumption
- **Description:** The rule is purely line-based, but a person counting by eye may count differently. Cases where the two could diverge:
  - Items inside blockquotes (`> - [ ]`) do not match the rule, though a person may count them.
  - Lines in indented (4-space) code blocks or HTML comments do match the rule, though a person would not count them.
  - A UTF-8 byte-order mark hides a first-line item or heading.
  - A non-breaking space after the marker defeats "spaces or tabs".
  - A non-UTF-8 byte raises a decode error, and the prompt shows `?`.

  Headings have a related problem: any line starting with `#` is shown as a heading, including `#tag` or shell-comment lines outside fences. The heading list may therefore carry noise.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** Before build, the developer runs the rule by hand against all ten real notes files and records every line where the rule and their own count disagree. Each such line becomes a decided test case.

**Risk 6: Coupling to this repository's working copy reaches beyond branch switches**
- **Category:** Organizational
- **Description:** The brief accepts `?` when this repository is on a branch without the script. The same coupling has broader effects. A half-edited or syntactically broken `scratch_notes.py` on any branch, or a moved or renamed repository directory, breaks the prompt in all ten projects at once. Development of the tool and daily use of the tool share one file with no release step between them.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** The developer explicitly accepts that editing the tool can break every prompt. If that is not acceptable, they decide on a stable copy or path that the prompt calls, separate from the working copy.

**Risk 7: Locating each project's notes file is unowned, and that invites scope growth**
- **Category:** Scope
- **Description:** The tool takes one file path, but the prompt script must know which file to pass for whichever project the shell is in. The brief does not say where the ten notes files live or how they are named. If there is no single convention, that logic will either sprawl in the prompt script or be pushed back into the tool. Pushing it into the tool would reopen the exclusions on multiple files, config files, and cross-project listing.
- **Likelihood:** Medium
- **Impact if realized:** Medium
- **Mitigation signal:** The developer states the per-project notes-file convention, such as a fixed filename at the project root, and states that "no notes file found" is the prompt script's job, with its own display.

### Top Concern

**What is the single biggest risk in this direction?**
The biggest risk is that a fresh `python3` process launched on every prompt draw is the weak point of the whole design, and none of the success criteria test it the way it will actually run. Which interpreter runs changes with whatever environment is active in the project just entered. Its startup cost, not the parsing, sets the latency. Every failure path, whether wrong version, shim overhead, missing package, or an edit in progress, turns into `?` or lag at exactly the moment the tool is supposed to help. A prompt segment that is sometimes slow and sometimes `?` loses the developer's trust as quickly as the grep count did. The direction pins the parsing rules carefully but leaves the invocation path, which is where it will most likely fail, as a stated requirement with nothing to enforce it or check it.

### Unstated Assumptions

- **Assumption:** Each project's notes file can be found by the prompt script without help, through a consistent name or location.
  **Why it matters if wrong:** Without it, the prompt has nothing to pass the tool, and file discovery will creep into the tool against the stated exclusions.
- **Assumption:** The developer's "hand count" is the same thing as the line rule in the scope.
  **Why it matters if wrong:** The success signal, "always matches a count done by hand", fails even when the code is correct, and trust is lost the first time the two differ.
- **Assumption:** The notes files are local, UTF-8, regular files that open instantly.
  **Why it matters if wrong:** Several cases break that. A cloud-synced file not yet downloaded can pass the regular-file check and still block while it downloads, which hangs the prompt. A symlink into a synced folder can behave the same way. A file in another encoding produces `?`.
- **Assumption:** A per-draw subprocess is an acceptable cost in the developer's prompt setup.
  **Why it matters if wrong:** If the prompt framework runs segments synchronously on every draw, any latency over budget is felt on every command. The fix would then be outside this direction's scope, such as caching or asynchronous segments.

Each mitigation above is a decision or validation step for the developer who owns this repository and the shell prompt.
