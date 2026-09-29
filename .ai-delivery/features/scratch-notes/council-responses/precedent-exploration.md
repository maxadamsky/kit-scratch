## Council Response

**Evidence consulted:** searched — https://github.com/yshavit/mdq, https://github.com/yshavit/mdq/wiki/Full-User-Manual, https://github.com/harehare/mq, https://github.com/DandyLyons/md-utils/issues/145, https://github.com/trashfeed/markdown-unchecked-counter; fetched — https://github.com/yshavit/mdq, https://github.com/yshavit/mdq/wiki/Full-User-Manual, https://github.com/harehare/mq

Both adoptable tools I found are separate Rust command-line binaries. Adopting either one breaks the framing's rule of "no new dependency, standard library only", even though neither would be a Python import. I found no Python-stdlib library or existing command-line tool that prints this exact output: an open-item count plus a list of headings, as plain text or as JSON. Other things I searched that do not fit: md-utils has "checkbox" commands, but they are only a proposal and not built yet (issue #145). markdown-unchecked-counter is a VS Code extension, not a command-line tool.

### Candidate 1: mdq (yshavit/mdq)

**What it is:** A Rust command-line tool described as "like jq but for Markdown." jq is a well-known command-line JSON query tool. mdq parses a Markdown file and uses selector strings to pull out parts of it. One person maintains it, and it is also packaged for Homebrew, Docker and FreeBSD ports.
**What it covers:** The `- [ ]` selector picks out unchecked task items. The `#` selector picks out headings and their sections. `--output json` gives structured output that a script can read. It only reads files; the docs describe querying, not editing. Because it is a real Markdown parser, it should handle `*`/`+` bullets, varied spacing and nesting correctly. That is the exact reason the developer's grep gives wrong counts. (This is an inference from it being a parser; I did not test these cases.)
**What it does not cover:** It has no count option that I could find documented. The JSON is mdq's own item schema, not a `{open, headings}` summary. So you still need a small wrapper, for example `mdq --output json '- [ ]' notes.md | jq '.items | length'`, plus a second call for headings. That means two processes on every prompt draw. The framing's rule is line-based: any `- [ ]` line counts. mdq's parser rule differs: it will skip `- [ ]` lines inside fenced code blocks, and it may treat some edge cases differently. The count can therefore disagree with a count done by hand under the framing's own definition. I did not confirm how it handles ordered tasks (`1. [ ]`) or what exit code it returns when nothing matches.
**Adoption cost:** MIT or Apache-2.0 (your choice). Installed with `brew install mdq` or as a prebuilt binary. It is an external binary rather than something inside this repo, so pytest cannot own its behaviour. It is also a new runtime dependency, which the framing rules out. There is little lock-in, since selectors are a small surface to replace later. Relying on one maintainer is a moderate risk.
**Evidence basis:** `fetched — https://github.com/yshavit/mdq`, `fetched — https://github.com/yshavit/mdq/wiki/Full-User-Manual`, `searched — https://github.com/yshavit/mdq/wiki/Full-User-Manual` (the `- [ ]` selector and the `--output json | jq` example came from the search snippet)

### Candidate 2: mq (harehare/mq)

**What it is:** Another jq-style Markdown query language and command-line tool, written in Rust, with a wider feature set: a query language, streaming, and parallel processing of many files.
**What it covers:** It selects headings by level (`.h(1..3)`). It has a `-c/--count` option and a `len` function, so it can produce a count directly. `-F json` gives JSON output. It is packaged for Homebrew, Cargo, Arch and Docker.
**What it does not cover:** The README I read does not explicitly document how to select task-list items, including unchecked ones. So the most important part of the problem, the trusted open count, is unconfirmed for this tool. It has the same gap as mdq on the parser rule versus the line rule, and it still needs a wrapper to produce the combined summary.
**Adoption cost:** MIT. External binary, and an install-by-script option (`curl | bash`) that some people will not want to use. It has a larger query language to learn than mdq, and it also counts as the new dependency the framing excludes.
**Evidence basis:** `fetched — https://github.com/harehare/mq`

### Candidate 3: A documented regex pattern with ripgrep or grep (pattern, not a product)

**What it is:** Instead of the developer's loose grep, use one anchored regular expression that encodes the framing's rule: `^\s*[-*+]\s+\[ \]`. It matches an optional indent, any of the three bullet characters, then `[ ]` (open, not `[x]`). Numbered items do not match. Count with `rg -c` or `grep -cE`, and list headings with `^#{1,6}\s`.
**What it covers:** A trustworthy count under the framing's own line-based definition. It runs fast enough for a prompt, needs no new dependency, and never touches the file.
**What it does not cover:** It has no JSON output, no single combined command, and no clean error handling on stderr. It is still a hand-written pattern, which is the very thing the success signal says the developer wants to stop writing. It also counts `- [ ]` lines inside code blocks and treats `#` lines inside code fences as headings.
**Adoption cost:** Free, with no lock-in. The cost is that this regex is almost exactly the core of what a stdlib Python build would contain anyway.
**Evidence basis:** `recalled`

## Strongest Statement

mdq comes closest to something you could adopt. Its `- [ ]` selector and JSON output cover most of the problem, and because it parses Markdown properly it fixes the miscounting that makes grep untrustworthy. However, adopting it breaks the "no new dependency" rule, still needs a wrapper to produce the single count-plus-headings summary the prompt wants, and counts by a parser rule that can differ from the framing's line rule. Adopting it is therefore a trade, not a clean win. Nothing I found delivers the whole framed output directly.

One decision is still open. The developer who owns this repository needs to decide whether an external binary like mdq is acceptable despite the stdlib-only rule, or whether that rule stands.

**END OF RESPONSE. Do not add anything after this line.**
