"""Tests for ``scratch_notes.py``: the open count (MAX-82), the headings (MAX-83) and
the ``--json`` output (MAX-84).

These tests prove that the script at the repository root keeps to its contracts in
``.ai-delivery/features/scratch-notes/design/1b-contracts.md``: the command (C1), the
functions (C2), the line rules behind ``scan_notes`` and the failures (C3). A plain
``uv run pytest`` from the repository root collects and runs them.

The tests come in two groups. The rule tests load ``scratch_notes.py`` by its file
location, under the module name ``scratch_notes``, and call its functions; the
interpreter's import path is never changed, because the script is not an installed
package (ADR-001). The command tests run the script as a process, the way the shell
prompt calls it, and check the exit code, stdout and stderr.

Every test builds its own input, inline or in pytest's temporary directory, and none
shares state with another. Exact plain output is asserted only on samples that hold no
heading lines, and summaries are compared by their open count alone, so that later
units can add headings and a JSON mode without editing these tests. The heading
tests are the ones that compare a summary's headings and the lines printed under
``open: N``.

The JSON tests compare the exact line ``--json`` prints, and what it parses back to.
The sample builder makes a notes-like file of a requested size whose count and headings
are known from how it was built; the same sample serves the correctness test at the
size limit and the timing test. The timing test runs the script with the shell prompt's
interpreter, ``/opt/homebrew/bin/python3``, and is skipped where that does not exist.
"""

import importlib.machinery
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scratch_notes.py"

SIZE_LIMIT_BYTES = 1_048_576
PROCESS_TIMEOUT_SECONDS = 5
SYSTEM_PYTHON = "/usr/bin/python3"
ERROR_PREFIX = "scratch_notes: "

GOOD_NOTES = (
    "Shopping\n"
    "- [ ] milk\n"
    "- [x] bread\n"
    "  * [ ] eggs\n"
    "```\n"
    "- [ ] not a task, only an example\n"
    "```\n"
    "+ [ ] post the letter\n"
)
GOOD_NOTES_OPEN_COUNT = 3

UNCLOSED_NOTES = "- [ ] one\n\n```\n- [ ] inside\n"
UNCLOSED_NOTES_FENCE_LINE = 3

SMALL_NOTES = "# Plan\n- [ ] book a table\n- [x] choose a day\n## Later\n"
SMALL_NOTES_JSON = '{"open": 1, "headings": ["# Plan", "## Later"]}\n'
EMPTY_NOTES_JSON = '{"open": 0, "headings": []}\n'

PROMPT_PYTHON = "/opt/homebrew/bin/python3"
TIMING_RUNS = 20
TIME_LIMIT_MS = 50.0


class _UncachedSourceLoader(importlib.machinery.SourceFileLoader):
    """Load a source file without leaving a bytecode cache beside it.

    The script sits at the repository root, where a ``__pycache__`` directory would
    show up as an untracked change after every test run.
    """

    def set_data(self, path: str, data: object, *, _mode: int = 0o666) -> None:
        """Discard the bytecode the import system would otherwise write.

        Args:
            path: where the bytecode cache would be written.
            data: the bytecode itself.
            _mode: the permissions the cache file would get.
        """


def _load_script() -> ModuleType:
    """Load ``scratch_notes.py`` by file location, under the name ``scratch_notes``.

    The import path is left alone, and the module name lets coverage measure the
    script.

    Raises:
        FileNotFoundError: when the script does not exist at the repository root.
    """
    loader = _UncachedSourceLoader("scratch_notes", str(SCRIPT))
    spec = importlib.util.spec_from_file_location(
        "scratch_notes", SCRIPT, loader=loader
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


scratch_notes = _load_script()


def _run_script(
    *arguments: str,
    interpreter: str = sys.executable,
    flags: tuple[str, ...] = (),
) -> tuple[int, bytes, bytes]:
    """Run the script as a process and return its exit code, stdout and stderr.

    Args:
        arguments: the arguments after the script's path.
        interpreter: the Python that runs the script; the one running the tests
            unless stated.
        flags: interpreter flags placed before the script's path.

    Raises:
        subprocess.TimeoutExpired: when the process is still running after
            ``PROCESS_TIMEOUT_SECONDS``, so a hang fails the test.
    """
    completed = subprocess.run(
        [interpreter, *flags, str(SCRIPT), *arguments],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def _write(path: Path, content: bytes) -> Path:
    """Write ``content`` to ``path`` exactly as given and return the path.

    Args:
        path: the file to create.
        content: the bytes the file holds.
    """
    path.write_bytes(content)
    return path


def _build_sample(size_bytes: int) -> tuple[str, int, list[str]]:
    """Build notes-like text of an exact size, with its known count and headings.

    The text is made of numbered blocks. Each block holds a heading, a line of prose,
    an open item, a done item, a nested open item, and a fenced block holding a
    look-alike open item and a look-alike heading, then a blank line. Whole blocks
    are added while they fit, and the last line is padded with plain text to reach the
    size. Every character is ASCII, so one character is one byte. The count and the
    headings are tallied as the blocks are added, not by running the script.

    Args:
        size_bytes: how many bytes the text must hold when encoded as UTF-8.

    Returns:
        The text, the number of open items it holds outside fenced code, and its
        headings outside fenced code, in order.

    Raises:
        ValueError: when ``size_bytes`` is below zero.
    """
    if size_bytes < 0:
        raise ValueError(f"a sample cannot hold {size_bytes} bytes")
    blocks = []
    headings = []
    open_count = 0
    used = 0
    number = 1
    while True:
        heading = f"## Topic {number}"
        block = (
            f"{heading}\n"
            "What came up, and what to do next.\n"
            f"- [ ] follow up on {number}\n"
            "- [x] file the note\n"
            "  - [ ] check the detail\n"
            "```text\n"
            "- [ ] not a task\n"
            "# not a heading\n"
            "```\n"
            "\n"
        )
        if used + len(block) > size_bytes:
            break
        blocks.append(block)
        headings.append(heading)
        open_count += 2
        used += len(block)
        number += 1
    padding = "." * (size_bytes - used)
    return "".join(blocks) + padding, open_count, headings


def _open_count(text: str) -> int:
    """Return the open count ``scan_notes`` reports for ``text``.

    Args:
        text: the notes text to scan.
    """
    count: int = scratch_notes.scan_notes(text).open_count
    return count


def _headings(text: str) -> list[str]:
    """Return the headings ``scan_notes`` reports for ``text``, in file order.

    Args:
        text: the notes text to scan.
    """
    headings: list[str] = scratch_notes.scan_notes(text).headings
    return headings


def _assert_failed_result(result: Any, exit_code: int) -> None:
    """Assert that a ``run`` result is a failure in the shape C3 promises.

    Args:
        result: the value ``run`` returned.
        exit_code: the exit code the failure must carry.
    """
    assert result.exit_code == exit_code
    assert result.stdout == ""
    assert result.stderr.startswith(ERROR_PREFIX)
    assert result.stderr.endswith("\n")
    assert result.stderr.count("\n") == 1


def _assert_failed_process(outcome: tuple[int, bytes, bytes], exit_code: int) -> None:
    """Assert that a process run failed in the shape C1 promises.

    Args:
        outcome: the exit code, stdout and stderr of the run.
        exit_code: the exit code the failure must carry.
    """
    code, stdout, stderr = outcome
    assert code == exit_code
    assert stdout == b""
    assert stderr.startswith(ERROR_PREFIX.encode("ascii"))
    assert stderr.endswith(b"\n")
    assert stderr.count(b"\n") == 1


# Rule tests: the open-item rule (FR-002)


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("- [ ] task", id="hyphen-marker"),
        pytest.param("* [ ] task", id="asterisk-marker"),
        pytest.param("+ [ ] task", id="plus-marker"),
        pytest.param("    - [ ] task", id="indented-with-spaces"),
        pytest.param("\t- [ ] task", id="indented-with-a-tab"),
        pytest.param(" \t  - [ ] task", id="indented-with-spaces-and-a-tab"),
        pytest.param("-  [ ] task", id="two-spaces-after-the-marker"),
        pytest.param("-\t[ ] task", id="a-tab-after-the-marker"),
        pytest.param("- [ ]", id="nothing-after-the-brackets"),
        pytest.param("- [ ]buy milk", id="no-space-after-the-brackets"),
    ],
)
def test_line_counts_as_an_open_item(line: str) -> None:
    """Each accepted form of an open checklist item counts as one."""
    count = _open_count(line + "\n")

    assert count == 1


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("- [x] done", id="lowercase-x"),
        pytest.param("- [X] done", id="uppercase-x"),
        pytest.param("- [-] dropped", id="hyphen-in-the-brackets"),
        pytest.param("- [] task", id="empty-brackets"),
        pytest.param("- [  ] task", id="two-spaces-in-the-brackets"),
        pytest.param("-[ ] task", id="no-space-after-the-marker"),
        pytest.param("1. [ ] task", id="numbered-item"),
        pytest.param("> - [ ] task", id="blockquoted-item"),
        pytest.param("- [ ] task", id="non-breaking-space-after-the-marker"),
        pytest.param(" - [ ] task", id="non-breaking-space-as-indentation"),
        pytest.param("[ ] task", id="no-list-marker"),
        pytest.param("buy milk - [ ] later", id="text-before-the-marker"),
    ],
)
def test_line_does_not_count_as_an_open_item(line: str) -> None:
    """Each look-alike that the rule excludes leaves the count at zero."""
    count = _open_count(line + "\n")

    assert count == 0


def test_mixed_file_gives_the_sum_of_its_open_items() -> None:
    """A file mixing open items with look-alikes counts only the open ones."""
    text = (
        "Today\n"
        "- [ ] first\n"
        "- [x] finished\n"
        "\t* [ ] second\n"
        "1. [ ] numbered\n"
        "+ [ ]third\n"
        "> - [ ] quoted\n"
        "-[ ] cramped\n"
        "- [ ]\n"
    )

    count = _open_count(text)

    assert count == 4


def test_empty_file_has_no_open_items() -> None:
    """An empty text gives a count of zero."""
    count = _open_count("")

    assert count == 0


def test_file_of_blank_lines_has_no_open_items() -> None:
    """A text holding only blank lines gives a count of zero."""
    count = _open_count("\n\n   \n\t\n\n")

    assert count == 0


def test_last_line_without_a_line_feed_still_counts() -> None:
    """An open item on a final line that has no line feed is counted."""
    count = _open_count("- [ ] first\n- [ ] last")

    assert count == 2


# Rule tests: fences (FR-003, FR-004)


def test_open_item_inside_a_backtick_fence_does_not_count() -> None:
    """Items before and after a backtick fence count; the one inside does not."""
    text = "- [ ] before\n```\n- [ ] inside\n```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 2


def test_open_item_inside_a_tilde_fence_does_not_count() -> None:
    """Items before and after a tilde fence count; the one inside does not."""
    text = "- [ ] before\n~~~\n- [ ] inside\n~~~\n- [ ] after\n"

    count = _open_count(text)

    assert count == 2


def test_fence_with_a_language_name_is_a_fence() -> None:
    """Backticks followed by a language name still open a fence."""
    text = "```python\n- [ ] inside\n```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_fence_indented_under_a_list_item_is_a_fence() -> None:
    """A fence nested under a list item, with any indentation, is a fence."""
    text = "- step one\n  ```\n  - [ ] inside\n  ```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_fence_closer_may_be_indented_differently_from_its_opener() -> None:
    """An indented closer closes a fence whose opener was not indented."""
    text = "```\n- [ ] inside\n\t   ```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_backtick_line_inside_a_tilde_fence_does_not_close_it() -> None:
    """Only tildes close a tilde fence, so the item after the backticks stays in."""
    text = "~~~\n```\n- [ ] inside\n~~~\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_tilde_line_inside_a_backtick_fence_does_not_close_it() -> None:
    """Only backticks close a backtick fence, so the item after the tildes stays in."""
    text = "```\n~~~\n- [ ] inside\n```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_closer_shorter_than_its_opener_does_not_close_the_fence() -> None:
    """Three backticks do not close a fence that four backticks opened."""
    text = "````\n- [ ] inside\n```\n- [ ] still inside\n````\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_closer_longer_than_its_opener_closes_the_fence() -> None:
    """Five backticks close a fence that three backticks opened."""
    text = "```\n- [ ] inside\n`````\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_closer_followed_by_trailing_spaces_and_tabs_closes_the_fence() -> None:
    """Spaces and tabs after the closing run do not stop it closing the fence."""
    text = "```\n- [ ] inside\n``` \t \n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_closer_followed_by_text_does_not_close_the_fence() -> None:
    """A run of the fence's character followed by text leaves the fence open."""
    text = "```\n- [ ] inside\n``` text\n- [ ] still inside\n```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_closer_followed_by_a_non_breaking_space_does_not_close_the_fence() -> None:
    """A non-breaking space is not trailing whitespace, so the fence stays open."""
    text = "```\n- [ ] inside\n``` \n- [ ] still inside\n```\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_one_line_backtick_snippet_is_text_not_a_fence() -> None:
    """A line that opens and closes with three backticks does not open a fence."""
    text = "```ls -la```\n- [ ] counts\n"

    count = _open_count(text)

    assert count == 1


def test_tildes_followed_by_text_open_a_fence() -> None:
    """Three tildes open a fence whatever follows them on the line."""
    text = "~~~ a note about ~~~ marks\n- [ ] inside\n~~~\n- [ ] after\n"

    count = _open_count(text)

    assert count == 1


def test_fence_left_open_on_line_one_is_an_error_naming_line_one() -> None:
    """A text ending inside a fence opened on line 1 raises, naming line 1."""
    text = "```\n- [ ] inside\n"

    with pytest.raises(scratch_notes.UnclosedFenceError) as raised:
        scratch_notes.scan_notes(text)

    assert str(raised.value) == "code fence opened on line 1 is never closed"
    assert raised.value.exit_code == 1


def test_fence_left_open_later_is_an_error_naming_its_line() -> None:
    """A text ending inside a fence opened on line 6 raises, naming line 6."""
    text = "- [ ] one\n```\ncode\n```\n\n~~~ shell\n- [ ] inside\n```\n"

    with pytest.raises(scratch_notes.UnclosedFenceError) as raised:
        scratch_notes.scan_notes(text)

    assert str(raised.value) == "code fence opened on line 6 is never closed"


# Rule tests: the heading rule (FR-005)


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("# Title", id="one-mark"),
        pytest.param("## Section", id="two-marks"),
        pytest.param("### Part", id="three-marks"),
        pytest.param("###### Deep", id="six-marks"),
        pytest.param("#\tTabbed", id="a-tab-after-the-mark"),
        pytest.param("#  Two  spaces", id="runs-of-spaces-kept"),
        pytest.param("# Title #", id="closing-mark-kept"),
        pytest.param("# - [ ] looks like a task", id="checkbox-text"),
    ],
)
def test_line_is_a_heading_reported_as_written(line: str) -> None:
    """Each accepted form of a heading is reported exactly as written."""
    headings = _headings(line + "\n")

    assert headings == [line]


@pytest.mark.parametrize(
    ("line", "reported"),
    [
        pytest.param("#", "#", id="one-mark-alone"),
        pytest.param("######", "######", id="six-marks-alone"),
        pytest.param("##   ", "##", id="marks-then-only-spaces"),
        pytest.param("#\t", "#", id="mark-then-only-a-tab"),
        pytest.param("# Title  \t \t", "# Title", id="text-then-spaces-and-tabs"),
    ],
)
def test_heading_is_reported_without_trailing_spaces_and_tabs(
    line: str, reported: str
) -> None:
    """Marks with nothing after them are a heading; trailing whitespace is removed."""
    headings = _headings(line + "\n")

    assert headings == [reported]


def test_trailing_non_breaking_space_stays_on_a_heading() -> None:
    """A non-breaking space is not trailing whitespace, so it is kept as written."""
    headings = _headings("# Title \n")

    assert headings == ["# Title "]


@pytest.mark.parametrize(
    "line",
    [
        pytest.param("#tag", id="no-space-after-the-mark"),
        pytest.param("#######", id="seven-marks-alone"),
        pytest.param("####### Seven", id="seven-marks-with-text"),
        pytest.param(" # indented", id="indented-with-a-space"),
        pytest.param("\t# indented", id="indented-with-a-tab"),
        pytest.param("# Title", id="non-breaking-space-after-the-mark"),
        pytest.param("Title # not at the start", id="text-before-the-mark"),
        pytest.param("> # quoted", id="blockquoted-heading"),
    ],
)
def test_line_is_not_a_heading(line: str) -> None:
    """Each look-alike that the heading rule excludes gives no heading."""
    headings = _headings(line + "\n")

    assert headings == []


@pytest.mark.parametrize(
    "underline",
    [
        pytest.param("===", id="equals-signs"),
        pytest.param("---", id="hyphens"),
    ],
)
def test_underlined_title_gives_no_heading(underline: str) -> None:
    """A title marked by a line of ``===`` or ``---`` under it is not a heading."""
    headings = _headings("Title\n" + underline + "\n")

    assert headings == []


def test_text_without_headings_gives_an_empty_list() -> None:
    """An empty text, and one holding only items and prose, give no headings."""
    empty_headings = _headings("")
    prose_headings = _headings(GOOD_NOTES)

    assert empty_headings == []
    assert prose_headings == []


def test_heading_inside_a_backtick_fence_is_not_a_heading() -> None:
    """Headings before and after a backtick fence are kept; the one inside is not."""
    text = "# Before\n```\n# inside\n```\n## After\n"

    headings = _headings(text)

    assert headings == ["# Before", "## After"]


def test_heading_inside_a_tilde_fence_is_not_a_heading() -> None:
    """Headings before and after a tilde fence are kept; the one inside is not."""
    text = "# Before\n~~~ shell\n# inside\n~~~\n## After\n"

    headings = _headings(text)

    assert headings == ["# Before", "## After"]


def test_heading_on_line_one_after_a_byte_order_mark_is_a_heading(
    tmp_path: Path,
) -> None:
    """A UTF-8 byte-order mark before a first-line heading is not reported with it."""
    path = _write(tmp_path / "notes.md", b"\xef\xbb\xbf# Title\n## Section\n")

    headings = _headings(scratch_notes.read_notes(str(path)))

    assert headings == ["# Title", "## Section"]


def test_crlf_copy_gives_the_same_headings_as_the_lf_original() -> None:
    """A CRLF copy of a sample gives the LF original's headings, free of returns."""
    lf_notes = "# Title\n- [ ] one\n## Section  \n```\n# inside\n```\n###\n"
    crlf_notes = lf_notes.replace("\n", "\r\n")

    lf_headings = _headings(lf_notes)
    crlf_headings = _headings(crlf_notes)

    assert lf_headings == ["# Title", "## Section", "###"]
    assert crlf_headings == lf_headings
    assert not any("\r" in heading for heading in crlf_headings)


def test_headings_come_back_in_file_order() -> None:
    """Several headings, repeats included, are listed in the order of their lines."""
    text = "## Second level first\ntext\n# Top\n### Third\n# Top\n###### Last"

    headings = _headings(text)

    assert headings == [
        "## Second level first",
        "# Top",
        "### Third",
        "# Top",
        "###### Last",
    ]


def test_open_items_and_headings_do_not_count_as_each_other() -> None:
    """An open item is counted and is no heading; a heading leaves the count alone."""
    text = "# Tasks\n- [ ] one\n## More\n  * [ ] two\n# - [ ] a heading\n"

    summary = scratch_notes.scan_notes(text)

    assert summary.open_count == 2
    assert summary.headings == ["# Tasks", "## More", "# - [ ] a heading"]


# Rule tests: plain output with headings (FR-016)


def test_render_plain_puts_each_heading_on_its_own_line_under_the_count() -> None:
    """A count and two headings render as three lines, each ending in a line feed."""
    summary = scratch_notes.NotesSummary(3, ["# Title", "## Section"])

    text = scratch_notes.render_plain(summary)

    assert text == "open: 3\n# Title\n## Section\n"


def test_render_plain_without_headings_gives_only_the_count_line() -> None:
    """A summary with no headings renders as the ``open: N`` line alone."""
    summary = scratch_notes.NotesSummary(4, [])

    text = scratch_notes.render_plain(summary)

    assert text == "open: 4\n"


def test_render_plain_keeps_non_ascii_heading_text_as_written() -> None:
    """A heading holding letters outside ASCII is rendered unchanged."""
    summary = scratch_notes.NotesSummary(0, ["# Café ☕ 日本語"])

    text = scratch_notes.render_plain(summary)

    assert text == "open: 0\n# Café ☕ 日本語\n"


def test_run_on_a_file_with_headings_lists_them_under_the_count(
    tmp_path: Path,
) -> None:
    """A file with headings gives exit code 0 and the headings after ``open: N``."""
    path = _write(tmp_path / "notes.md", b"# Title\n- [ ] one\n\n## Section\ntext\n")

    result = scratch_notes.run([str(path)])

    assert result.exit_code == 0
    assert result.stdout == "open: 1\n# Title\n## Section\n"
    assert result.stderr == ""


# Rule tests: line endings and the byte-order mark (FR-006)


def test_crlf_copy_gives_the_same_count_as_the_lf_original() -> None:
    """A CRLF copy of a sample scans exactly like its LF original."""
    crlf_notes = GOOD_NOTES.replace("\n", "\r\n")

    lf_count = _open_count(GOOD_NOTES)
    crlf_count = _open_count(crlf_notes)

    assert lf_count == GOOD_NOTES_OPEN_COUNT
    assert crlf_count == GOOD_NOTES_OPEN_COUNT


def test_open_item_on_line_one_after_a_byte_order_mark_counts(tmp_path: Path) -> None:
    """A UTF-8 byte-order mark before a first-line open item does not hide it."""
    path = _write(tmp_path / "notes.md", b"\xef\xbb\xbf- [ ] first\n- [ ] second\n")

    count = _open_count(scratch_notes.read_notes(str(path)))

    assert count == 2


@pytest.mark.parametrize(
    "separator",
    [
        pytest.param("\f", id="form-feed"),
        pytest.param("\v", id="vertical-tab"),
        pytest.param("\r", id="lone-carriage-return"),
        pytest.param("\x1c", id="file-separator"),
        pytest.param("\x85", id="next-line"),
        pytest.param(" ", id="unicode-line-separator"),
        pytest.param(" ", id="unicode-paragraph-separator"),
    ],
)
def test_only_a_line_feed_ends_a_line(separator: str) -> None:
    """Text, another separator, then an item on the same line does not count."""
    text = "note" + separator + "- [ ] task\n"

    count = _open_count(text)

    assert count == 0


# Rule tests: read_notes (FR-006, FR-009, FR-010, FR-017)


def test_read_notes_returns_the_text_of_a_regular_file(tmp_path: Path) -> None:
    """A regular file comes back as its text, decoded as UTF-8."""
    path = _write(tmp_path / "notes.md", "- [ ] café\r\n".encode())

    text = scratch_notes.read_notes(str(path))

    assert text == "- [ ] café\r\n"


def test_read_notes_follows_a_symbolic_link_to_a_regular_file(tmp_path: Path) -> None:
    """A symbolic link to a regular file is read through."""
    target = _write(tmp_path / "target.md", b"- [ ] linked\n")
    link = tmp_path / "link.md"
    link.symlink_to(target)

    text = scratch_notes.read_notes(str(link))

    assert text == "- [ ] linked\n"


def test_read_notes_removes_only_a_leading_byte_order_mark(tmp_path: Path) -> None:
    """One byte-order mark at the very start is removed; a later one is kept."""
    path = _write(tmp_path / "notes.md", b"\xef\xbb\xbfa\xef\xbb\xbfb\n")

    text = scratch_notes.read_notes(str(path))

    assert text == "a﻿b\n"


def test_read_notes_refuses_a_missing_path(tmp_path: Path) -> None:
    """A path that does not exist raises NotesFileMissingError naming it."""
    path = str(tmp_path / "absent.md")

    with pytest.raises(scratch_notes.NotesFileMissingError) as raised:
        scratch_notes.read_notes(path)

    assert str(raised.value) == f"no such file: {path!a}"
    assert raised.value.exit_code == 1


def test_read_notes_refuses_a_path_under_a_missing_directory(tmp_path: Path) -> None:
    """A path whose directory does not exist raises NotesFileMissingError."""
    path = str(tmp_path / "no-such-directory" / "notes.md")

    with pytest.raises(scratch_notes.NotesFileMissingError) as raised:
        scratch_notes.read_notes(path)

    assert str(raised.value) == f"no such file: {path!a}"


def test_read_notes_refuses_a_path_under_a_regular_file(tmp_path: Path) -> None:
    """A path whose parent is a file, not a directory, raises NotesFileMissingError."""
    parent = _write(tmp_path / "plain.md", b"- [ ] task\n")
    path = str(parent / "notes.md")

    with pytest.raises(scratch_notes.NotesFileMissingError) as raised:
        scratch_notes.read_notes(path)

    assert str(raised.value) == f"no such file: {path!a}"


def test_read_notes_refuses_a_directory(tmp_path: Path) -> None:
    """A directory raises NotARegularFileError naming it."""
    path = str(tmp_path)

    with pytest.raises(scratch_notes.NotARegularFileError) as raised:
        scratch_notes.read_notes(path)

    assert str(raised.value) == f"not a regular file: {path!a}"
    assert raised.value.exit_code == 1


def test_read_notes_refuses_a_symbolic_link_to_a_directory(tmp_path: Path) -> None:
    """A symbolic link is followed, so a link to a directory is refused."""
    link = tmp_path / "link"
    link.symlink_to(tmp_path, target_is_directory=True)

    with pytest.raises(scratch_notes.NotARegularFileError) as raised:
        scratch_notes.read_notes(str(link))

    assert str(raised.value) == f"not a regular file: {str(link)!a}"


def test_read_notes_refuses_a_file_with_no_permissions(tmp_path: Path) -> None:
    """A file the user may not read raises NotesFileUnreadableError with the reason."""
    if os.geteuid() == 0:
        pytest.skip("running as the superuser, who can read a file with no permissions")
    path = _write(tmp_path / "notes.md", b"- [ ] task\n")
    path.chmod(0)
    prefix = f"cannot read {str(path)!a}: "

    with pytest.raises(scratch_notes.NotesFileUnreadableError) as raised:
        scratch_notes.read_notes(str(path))

    message = str(raised.value)
    assert message.startswith(prefix)
    assert message[len(prefix) :].strip()
    assert "\n" not in message
    assert raised.value.exit_code == 1


def test_read_notes_reports_a_lookup_the_operating_system_refuses(
    tmp_path: Path,
) -> None:
    """A path the operating system will not look up raises NotesFileUnreadableError."""
    path = str(tmp_path / ("n" * 5000))
    prefix = f"cannot read {path!a}: "

    with pytest.raises(scratch_notes.NotesFileUnreadableError) as raised:
        scratch_notes.read_notes(path)

    message = str(raised.value)
    assert message.startswith(prefix)
    assert message[len(prefix) :].strip()
    assert "\n" not in message


def test_read_notes_refuses_bytes_that_are_not_utf8(tmp_path: Path) -> None:
    """Invalid UTF-8 raises NotesFileEncodingError, without quoting the file."""
    path = _write(tmp_path / "notes.md", b"- [ ] hidden \xff\xfe words\n")

    with pytest.raises(scratch_notes.NotesFileEncodingError) as raised:
        scratch_notes.read_notes(str(path))

    assert str(raised.value) == f"not valid UTF-8: {str(path)!a}"
    assert raised.value.exit_code == 1


def test_read_notes_reads_a_file_of_exactly_the_size_limit(tmp_path: Path) -> None:
    """A file of exactly 1,048,576 bytes is read in full."""
    path = _write(tmp_path / "notes.md", b"a" * SIZE_LIMIT_BYTES)

    text = scratch_notes.read_notes(str(path))

    assert len(text) == SIZE_LIMIT_BYTES


def test_read_notes_refuses_a_file_one_byte_over_the_limit(tmp_path: Path) -> None:
    """A file of 1,048,577 bytes raises NotesFileTooLargeError naming the limit."""
    path = _write(tmp_path / "notes.md", b"a" * (SIZE_LIMIT_BYTES + 1))

    with pytest.raises(scratch_notes.NotesFileTooLargeError) as raised:
        scratch_notes.read_notes(str(path))

    assert str(raised.value) == f"larger than 1048576 bytes: {str(path)!a}"
    assert raised.value.exit_code == 1


def test_read_notes_refuses_a_file_that_yields_more_than_its_recorded_size(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A file whose recorded size is within the limit is still refused when it yields
    more than the limit, as a file that grew after the size check would."""
    path = _write(tmp_path / "notes.md", b"a" * (SIZE_LIMIT_BYTES + 1))
    real_stat = os.stat
    real_fields = tuple(real_stat(path))
    understated = os.stat_result(
        real_fields[:6] + (SIZE_LIMIT_BYTES,) + real_fields[7:]
    )

    def stat_understating_the_size(target: Any, *args: Any, **kwargs: Any) -> Any:
        """Report the notes file as exactly at the limit; pass other paths through."""
        if target == str(path):
            return understated
        return real_stat(target, *args, **kwargs)

    monkeypatch.setattr(os, "stat", stat_understating_the_size)

    with pytest.raises(scratch_notes.NotesFileTooLargeError) as raised:
        scratch_notes.read_notes(str(path))

    assert str(raised.value) == f"larger than 1048576 bytes: {str(path)!a}"


@pytest.mark.parametrize(
    ("content", "error_name"),
    [
        pytest.param(None, "NotesFileMissingError", id="missing-file"),
        pytest.param(b"\xff", "NotesFileEncodingError", id="invalid-utf8"),
        pytest.param(
            b"a" * (SIZE_LIMIT_BYTES + 1), "NotesFileTooLargeError", id="oversized-file"
        ),
    ],
)
def test_message_shows_an_awkward_path_in_escaped_ascii_on_one_line(
    tmp_path: Path, content: bytes | None, error_name: str
) -> None:
    """A path with a space, a non-ASCII letter and a line feed is escaped in full."""
    path = tmp_path / "my nötes\ntoday.md"
    if content is not None:
        _write(path, content)

    with pytest.raises(getattr(scratch_notes, error_name)) as raised:
        scratch_notes.read_notes(str(path))

    message = str(raised.value)
    assert message.isascii()
    assert "\n" not in message
    assert message.endswith(ascii(str(path)))
    assert "my n\\xf6tes\\ntoday.md" in message


def test_message_shows_an_awkward_directory_path_in_escaped_ascii(
    tmp_path: Path,
) -> None:
    """A directory whose name has a space and a non-ASCII letter is escaped."""
    path = tmp_path / "my nötes"
    path.mkdir()

    with pytest.raises(scratch_notes.NotARegularFileError) as raised:
        scratch_notes.read_notes(str(path))

    message = str(raised.value)
    assert message.isascii()
    assert "\n" not in message
    assert message == f"not a regular file: {str(path)!a}"
    assert "my n\\xf6tes" in message


# Rule tests: arguments, the version guard, the error family and run (FR-001, FR-009,
# FR-013)


def test_one_path_gives_a_request_holding_it_as_given() -> None:
    """One argument becomes the request's path, unchanged."""
    request = scratch_notes.parse_arguments(["../notes/my today.md"])

    assert request.path == "../notes/my today.md"


def test_path_starting_with_dot_slash_hyphen_is_accepted() -> None:
    """A file whose name starts with a hyphen is passed as ``./-name``."""
    request = scratch_notes.parse_arguments(["./-name"])

    assert request.path == "./-name"


@pytest.mark.parametrize(
    ("arguments", "count"),
    [
        pytest.param([], 0, id="no-argument"),
        pytest.param(["one.md", "two.md"], 2, id="two-paths"),
        pytest.param(["one.md", "two.md", "three.md"], 3, id="three-paths"),
    ],
)
def test_wrong_number_of_paths_is_a_usage_error_naming_the_count(
    arguments: list[str], count: int
) -> None:
    """Anything other than exactly one path raises UsageError with the count."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(arguments)

    message = str(raised.value)
    assert message.startswith("usage: ")
    assert f"(expected one file, got {count})" in message
    assert raised.value.exit_code == 2


@pytest.mark.parametrize(
    "option",
    [
        pytest.param("--verbose", id="long-option"),
        pytest.param("-", id="single-hyphen"),
        pytest.param("--", id="double-hyphen"),
        pytest.param("--help", id="help"),
        pytest.param("-v", id="short-option"),
    ],
)
def test_unknown_option_is_a_usage_error_naming_the_option(option: str) -> None:
    """Any argument starting with a hyphen raises UsageError naming it."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(["notes.md", option])

    message = str(raised.value)
    assert message.startswith("usage: ")
    assert message.endswith(f"(unknown option {option})")
    assert raised.value.exit_code == 2


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(["--verbose"], id="no-path"),
        pytest.param(["one.md", "two.md", "--verbose"], id="two-paths"),
    ],
)
def test_unknown_option_is_reported_before_a_wrong_path_count(
    arguments: list[str],
) -> None:
    """With both faults present, the message names the option, not the count."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(arguments)

    message = str(raised.value)
    assert "(unknown option --verbose)" in message
    assert "expected one file" not in message


def test_usage_message_for_an_unprintable_option_stays_on_one_line() -> None:
    """An option holding a line feed or a non-ASCII letter is shown escaped."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(["notes.md", "--vérbose\nnow"])

    message = str(raised.value)
    assert message.isascii()
    assert "\n" not in message
    assert "unknown option '--v\\xe9rbose\\nnow'" in message


@pytest.mark.parametrize(
    ("version", "shown"),
    [
        pytest.param((3, 9, 6), "3.9.6", id="3.9.6"),
        pytest.param((3, 10, 99), "3.10.99", id="3.10.99"),
        pytest.param((2, 12, 0), "2.12.0", id="2.12.0"),
    ],
)
def test_version_guard_refuses_a_python_older_than_3_11(
    version: tuple[int, int, int], shown: str
) -> None:
    """A version below 3.11 raises UnsupportedPythonError naming the version."""
    with pytest.raises(scratch_notes.UnsupportedPythonError) as raised:
        scratch_notes.check_python_version(*version)

    assert str(raised.value) == f"needs Python 3.11 or newer, running {shown}"
    assert raised.value.exit_code == 1


@pytest.mark.parametrize(
    "version",
    [
        pytest.param((3, 11, 0), id="3.11.0"),
        pytest.param((3, 14, 5), id="3.14.5"),
        pytest.param((4, 0, 0), id="4.0.0"),
    ],
)
def test_version_guard_accepts_python_3_11_or_newer(
    version: tuple[int, int, int],
) -> None:
    """A version of 3.11 or above returns without raising."""
    outcome = scratch_notes.check_python_version(*version)

    assert outcome is None


@pytest.mark.parametrize(
    ("error_name", "exit_code"),
    [
        pytest.param("UsageError", 2, id="usage"),
        pytest.param("UnsupportedPythonError", 1, id="unsupported-python"),
        pytest.param("NotesFileMissingError", 1, id="missing-file"),
        pytest.param("NotARegularFileError", 1, id="not-a-regular-file"),
        pytest.param("NotesFileTooLargeError", 1, id="too-large"),
        pytest.param("NotesFileUnreadableError", 1, id="unreadable"),
        pytest.param("NotesFileEncodingError", 1, id="encoding"),
        pytest.param("UnclosedFenceError", 1, id="unclosed-fence"),
    ],
)
def test_every_error_belongs_to_the_family_with_its_exit_code(
    error_name: str, exit_code: int
) -> None:
    """Each error in C3 derives from ScratchNotesError and carries its exit code."""
    error_class = getattr(scratch_notes, error_name)

    assert issubclass(error_class, scratch_notes.ScratchNotesError)
    assert error_class.exit_code == exit_code


def test_render_plain_gives_the_open_count_line() -> None:
    """The plain rendering of a summary with two open items is ``open: 2``."""
    summary = scratch_notes.scan_notes("- [ ] one\n- [ ] two\n- [x] three\n")

    text = scratch_notes.render_plain(summary)

    assert text == "open: 2\n"


def test_run_on_a_good_file_returns_the_count_line(tmp_path: Path) -> None:
    """A good file gives exit code 0, ``open: N`` on stdout and empty stderr."""
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())

    result = scratch_notes.run([str(path)])

    assert result.exit_code == 0
    assert result.stdout == f"open: {GOOD_NOTES_OPEN_COUNT}\n"
    assert result.stderr == ""


def test_run_on_an_empty_file_reports_zero(tmp_path: Path) -> None:
    """An empty file gives ``open: 0``."""
    path = _write(tmp_path / "notes.md", b"")

    result = scratch_notes.run([str(path)])

    assert result.exit_code == 0
    assert result.stdout == "open: 0\n"
    assert result.stderr == ""


def test_run_without_arguments_returns_a_usage_failure() -> None:
    """No argument gives exit code 2 and a usage line on stderr."""
    result = scratch_notes.run([])

    _assert_failed_result(result, exit_code=2)
    assert result.stderr.startswith("scratch_notes: usage:")
    assert "(expected one file, got 0)" in result.stderr


def test_run_with_an_unknown_option_returns_a_usage_failure(tmp_path: Path) -> None:
    """An unknown option gives exit code 2, even beside a good file."""
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())

    result = scratch_notes.run([str(path), "--verbose"])

    _assert_failed_result(result, exit_code=2)
    assert result.stderr.startswith("scratch_notes: usage:")
    assert "(unknown option --verbose)" in result.stderr


def test_run_on_a_missing_file_returns_a_failure(tmp_path: Path) -> None:
    """A missing file gives exit code 1 and names the path on stderr."""
    path = str(tmp_path / "absent.md")

    result = scratch_notes.run([path])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: no such file: {path!a}\n"


def test_run_on_a_directory_returns_a_failure(tmp_path: Path) -> None:
    """A directory gives exit code 1 and says it is not a regular file."""
    result = scratch_notes.run([str(tmp_path)])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: not a regular file: {str(tmp_path)!a}\n"


def test_run_on_an_oversized_file_returns_a_failure(tmp_path: Path) -> None:
    """A file over the limit gives exit code 1 and names the limit."""
    path = _write(tmp_path / "notes.md", b"- [ ] a\n" * (SIZE_LIMIT_BYTES // 8 + 1))

    result = scratch_notes.run([str(path)])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: larger than 1048576 bytes: {str(path)!a}\n"


def test_run_on_invalid_utf8_returns_a_failure(tmp_path: Path) -> None:
    """Invalid UTF-8 gives exit code 1 and says so, even after open items."""
    path = _write(tmp_path / "notes.md", b"- [ ] one\n\xff\n")

    result = scratch_notes.run([str(path)])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: not valid UTF-8: {str(path)!a}\n"


def test_run_on_an_unclosed_fence_returns_a_failure(tmp_path: Path) -> None:
    """An unclosed fence gives exit code 1, names its line and prints no count."""
    path = _write(tmp_path / "notes.md", UNCLOSED_NOTES.encode())

    result = scratch_notes.run([str(path)])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == (
        f"scratch_notes: code fence opened on line {UNCLOSED_NOTES_FENCE_LINE} "
        "is never closed\n"
    )


# Rule tests: the --json option in the arguments (FR-007)


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(["notes/today.md", "--json"], id="path-then-option"),
        pytest.param(["--json", "notes/today.md"], id="option-then-path"),
    ],
)
def test_json_option_in_either_position_gives_a_request_for_json(
    arguments: list[str],
) -> None:
    """``--json`` before or after the path asks for JSON and keeps the path."""
    request = scratch_notes.parse_arguments(arguments)

    assert request.as_json is True
    assert request.path == "notes/today.md"


def test_path_alone_gives_a_request_for_plain_text() -> None:
    """Without ``--json`` the request asks for plain text."""
    request = scratch_notes.parse_arguments(["notes/today.md"])

    assert request.as_json is False
    assert request.path == "notes/today.md"


@pytest.mark.parametrize(
    "arguments",
    [
        pytest.param(["notes.md", "--json", "--json"], id="both-after-the-path"),
        pytest.param(["--json", "notes.md", "--json"], id="either-side-of-the-path"),
        pytest.param(["--json", "--json"], id="no-path"),
        pytest.param(["--json", "one.md", "two.md", "--json"], id="two-paths"),
    ],
)
def test_json_option_given_twice_is_a_usage_error_naming_it(
    arguments: list[str],
) -> None:
    """A second ``--json`` raises UsageError, reported before a wrong path count."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(arguments)

    assert str(raised.value) == (
        "usage: scratch_notes.py <file> [--json] (option --json given twice)"
    )
    assert raised.value.exit_code == 2


@pytest.mark.parametrize(
    ("arguments", "count"),
    [
        pytest.param(["--json"], 0, id="no-path"),
        pytest.param(["one.md", "--json", "two.md"], 2, id="two-paths"),
    ],
)
def test_json_option_with_a_wrong_number_of_paths_is_a_usage_error(
    arguments: list[str], count: int
) -> None:
    """``--json`` does not stand in for the path: the count of paths is still named."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(arguments)

    assert str(raised.value) == (
        f"usage: scratch_notes.py <file> [--json] (expected one file, got {count})"
    )
    assert raised.value.exit_code == 2


def test_usage_message_for_an_unknown_option_shows_the_json_option() -> None:
    """``--verbose`` is still unknown, and the usage text now holds ``[--json]``."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(["notes.md", "--verbose"])

    assert str(raised.value) == (
        "usage: scratch_notes.py <file> [--json] (unknown option --verbose)"
    )
    assert raised.value.exit_code == 2


@pytest.mark.parametrize(
    "option",
    [
        pytest.param("--JSON", id="upper-case"),
        pytest.param("--jso", id="abbreviation"),
        pytest.param("-json", id="one-hyphen"),
        pytest.param("--json=1", id="with-a-value"),
        pytest.param("--json ", id="trailing-space"),
    ],
)
def test_look_alike_of_the_json_option_is_an_unknown_option(option: str) -> None:
    """Only the exact text ``--json`` is the option; a near miss is unknown."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(["notes.md", option])

    assert str(raised.value).endswith(f"(unknown option {option})")


def test_unknown_option_is_reported_before_a_repeated_json_option() -> None:
    """With an unknown option and ``--json`` twice, the unknown option is named."""
    with pytest.raises(scratch_notes.UsageError) as raised:
        scratch_notes.parse_arguments(["--json", "notes.md", "--json", "--verbose"])

    message = str(raised.value)
    assert message.endswith("(unknown option --verbose)")
    assert "given twice" not in message


# Rule tests: render_json (FR-007)


def test_render_json_gives_the_exact_line_for_a_small_file() -> None:
    """Two headings, one open item and one done item give the contract's line."""
    summary = scratch_notes.scan_notes(SMALL_NOTES)

    text = scratch_notes.render_json(summary)

    assert text == SMALL_NOTES_JSON


def test_render_json_with_nothing_found_gives_zero_and_an_empty_list() -> None:
    """A count of 0 and no headings give ``{"open": 0, "headings": []}``."""
    summary = scratch_notes.NotesSummary(0, [])

    text = scratch_notes.render_json(summary)

    assert text == EMPTY_NOTES_JSON


def test_render_json_gives_one_line_ending_in_a_line_feed() -> None:
    """Many headings still give one line: the only line feed is the last character."""
    summary = scratch_notes.NotesSummary(12, [f"## Part {n}" for n in range(40)])

    text = scratch_notes.render_json(summary)

    assert text.count("\n") == 1
    assert text.endswith("\n")
    assert "\r" not in text


def test_render_json_parses_to_exactly_the_two_keys_with_their_types() -> None:
    """The line parses to ``open``, a whole number, then ``headings``, a text list."""
    summary = scratch_notes.NotesSummary(7, ["# Title", "## Section"])

    parsed = json.loads(scratch_notes.render_json(summary))

    assert list(parsed) == ["open", "headings"]
    assert type(parsed["open"]) is int
    assert parsed["open"] == 7
    assert type(parsed["headings"]) is list
    assert all(type(heading) is str for heading in parsed["headings"])
    assert parsed["headings"] == ["# Title", "## Section"]


def test_render_json_writes_a_count_of_one_as_a_number_not_true() -> None:
    """A count of 1 is the JSON number ``1``, never ``true`` and never text."""
    summary = scratch_notes.NotesSummary(1, [])

    text = scratch_notes.render_json(summary)

    assert text == '{"open": 1, "headings": []}\n'


@pytest.mark.parametrize(
    "heading",
    [
        pytest.param('# Say "hi" to C:\\notes', id="quote-and-backslash"),
        pytest.param("# Café ☕ 日本語", id="non-ascii-letters"),
        pytest.param("## Done 😀", id="outside-the-basic-plane"),
        pytest.param('### "é\\" \\u00e9', id="quote-backslash-and-non-ascii"),
        pytest.param("# One\tTwo\x1b[31m", id="control-characters"),
        pytest.param("# One\u2028Two\x85Three", id="unicode-line-separators"),
    ],
)
def test_render_json_escapes_an_awkward_heading_and_parses_back_to_it(
    heading: str,
) -> None:
    """The line is pure printable ASCII, and parsing gives the heading as written."""
    summary = scratch_notes.NotesSummary(0, [heading])

    text = scratch_notes.render_json(summary)

    assert text.isascii()
    assert text[:-1].isprintable()
    assert text.count("\n") == 1
    assert json.loads(text) == {"open": 0, "headings": [heading]}


def test_render_json_escapes_a_non_ascii_heading_exactly() -> None:
    """A letter outside ASCII is written as a ``\\u`` escape, a quote as ``\\"``."""
    summary = scratch_notes.NotesSummary(2, ['# Café "plans"'])

    text = scratch_notes.render_json(summary)

    assert text == '{"open": 2, "headings": ["# Caf\\u00e9 \\"plans\\""]}\n'


# Rule tests: run with --json (FR-007, FR-009)


@pytest.mark.parametrize(
    "option_first",
    [
        pytest.param(False, id="path-then-option"),
        pytest.param(True, id="option-then-path"),
    ],
)
def test_run_with_json_on_a_good_file_returns_the_json_line(
    tmp_path: Path, option_first: bool
) -> None:
    """A good file gives exit code 0, the JSON line on stdout and empty stderr."""
    path = _write(tmp_path / "notes.md", SMALL_NOTES.encode())
    arguments = ["--json", str(path)] if option_first else [str(path), "--json"]

    result = scratch_notes.run(arguments)

    assert result.exit_code == 0
    assert result.stdout == SMALL_NOTES_JSON
    assert result.stderr == ""


def test_run_with_json_on_an_empty_file_reports_zero_and_no_headings(
    tmp_path: Path,
) -> None:
    """An empty file gives ``{"open": 0, "headings": []}``."""
    path = _write(tmp_path / "notes.md", b"")

    result = scratch_notes.run([str(path), "--json"])

    assert result.exit_code == 0
    assert result.stdout == EMPTY_NOTES_JSON
    assert result.stderr == ""


def test_run_with_json_agrees_with_the_plain_run_on_the_same_file(
    tmp_path: Path,
) -> None:
    """Both renderings of one file carry the same count and the same headings."""
    notes = (
        "# Café\n- [ ] one\n```\n# inside\n- [ ] inside\n```\n## Later  \n* [ ] two\n"
    )
    path = _write(tmp_path / "notes.md", notes.encode())

    plain = scratch_notes.run([str(path)])
    as_json = scratch_notes.run([str(path), "--json"])

    assert plain.stdout == "open: 2\n# Café\n## Later\n"
    assert json.loads(as_json.stdout) == {"open": 2, "headings": ["# Café", "## Later"]}


def test_run_with_json_and_no_path_returns_a_usage_failure() -> None:
    """``--json`` alone gives exit code 2, a usage line and no JSON."""
    result = scratch_notes.run(["--json"])

    _assert_failed_result(result, exit_code=2)
    assert result.stderr == (
        "scratch_notes: usage: scratch_notes.py <file> [--json] "
        "(expected one file, got 0)\n"
    )


def test_run_with_json_given_twice_returns_a_usage_failure(tmp_path: Path) -> None:
    """``--json`` twice gives exit code 2, even beside a good file."""
    path = _write(tmp_path / "notes.md", SMALL_NOTES.encode())

    result = scratch_notes.run([str(path), "--json", "--json"])

    _assert_failed_result(result, exit_code=2)
    assert result.stderr == (
        "scratch_notes: usage: scratch_notes.py <file> [--json] "
        "(option --json given twice)\n"
    )


def test_run_with_json_on_a_missing_file_returns_a_failure(tmp_path: Path) -> None:
    """A missing file gives exit code 1, one stderr line and no JSON on stdout."""
    path = str(tmp_path / "absent.md")

    result = scratch_notes.run([path, "--json"])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: no such file: {path!a}\n"


def test_run_with_json_on_a_directory_returns_a_failure(tmp_path: Path) -> None:
    """A directory gives exit code 1, one stderr line and no JSON on stdout."""
    result = scratch_notes.run(["--json", str(tmp_path)])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: not a regular file: {str(tmp_path)!a}\n"


def test_run_with_json_on_an_oversized_file_returns_a_failure(tmp_path: Path) -> None:
    """A file one byte over the limit gives exit code 1 and no JSON on stdout."""
    path = _write(tmp_path / "notes.md", b"a" * (SIZE_LIMIT_BYTES + 1))

    result = scratch_notes.run([str(path), "--json"])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: larger than 1048576 bytes: {str(path)!a}\n"


def test_run_with_json_on_invalid_utf8_returns_a_failure(tmp_path: Path) -> None:
    """Invalid UTF-8 after a heading and an open item gives exit code 1 and no JSON."""
    path = _write(tmp_path / "notes.md", b"# Plan\n- [ ] one\n\xff\n")

    result = scratch_notes.run([str(path), "--json"])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == f"scratch_notes: not valid UTF-8: {str(path)!a}\n"


def test_run_with_json_on_an_unclosed_fence_returns_a_failure(tmp_path: Path) -> None:
    """An unclosed fence gives exit code 1, names its line and prints no JSON."""
    path = _write(tmp_path / "notes.md", UNCLOSED_NOTES.encode())

    result = scratch_notes.run([str(path), "--json"])

    _assert_failed_result(result, exit_code=1)
    assert result.stderr == (
        f"scratch_notes: code fence opened on line {UNCLOSED_NOTES_FENCE_LINE} "
        "is never closed\n"
    )


# Rule tests: the sample builder and the script at the size limit (FR-012, FR-017)


@pytest.mark.parametrize(
    "size_bytes",
    [
        pytest.param(0, id="empty"),
        pytest.param(1, id="one-byte"),
        pytest.param(4096, id="a-few-kilobytes"),
        pytest.param(SIZE_LIMIT_BYTES, id="the-size-limit"),
    ],
)
def test_sample_builder_gives_text_of_exactly_the_requested_size(
    size_bytes: int,
) -> None:
    """The sample holds exactly the bytes asked for, and its tallies fit its blocks."""
    text, open_count, headings = _build_sample(size_bytes)

    assert len(text.encode()) == size_bytes
    assert open_count == 2 * len(headings)
    assert len(set(headings)) == len(headings)


def test_run_with_json_on_a_sample_at_the_size_limit_gives_the_built_tallies(
    tmp_path: Path,
) -> None:
    """A notes-like file of exactly 1,048,576 bytes gives the builder's count and
    headings, which are known from how the text was built."""
    text, open_count, headings = _build_sample(SIZE_LIMIT_BYTES)
    path = _write(tmp_path / "sample.md", text.encode())

    result = scratch_notes.run([str(path), "--json"])

    assert open_count > 0
    assert result.exit_code == 0
    assert result.stderr == ""
    assert result.stdout.count("\n") == 1
    assert json.loads(result.stdout) == {"open": open_count, "headings": headings}


# Command tests: the script run as a process


def test_command_on_a_good_file_prints_the_count(tmp_path: Path) -> None:
    """The script exits 0 with ``open: N`` on stdout and nothing on stderr."""
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())

    code, stdout, stderr = _run_script(str(path))

    assert code == 0
    assert stdout == f"open: {GOOD_NOTES_OPEN_COUNT}\n".encode("ascii")
    assert stderr == b""


def test_command_runs_with_the_standard_library_alone(tmp_path: Path) -> None:
    """Under ``-I -S``, with no site packages, the result is the same (FR-011)."""
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())

    code, stdout, stderr = _run_script(str(path), flags=("-I", "-S"))

    assert code == 0
    assert stdout == f"open: {GOOD_NOTES_OPEN_COUNT}\n".encode("ascii")
    assert stderr == b""


def test_command_on_a_crlf_file_with_a_byte_order_mark_prints_the_count(
    tmp_path: Path,
) -> None:
    """A CRLF file that starts with a byte-order mark gives the LF file's count."""
    crlf_notes = "- [ ] first\n" + GOOD_NOTES
    content = b"\xef\xbb\xbf" + crlf_notes.replace("\n", "\r\n").encode()
    path = _write(tmp_path / "notes.md", content)

    code, stdout, stderr = _run_script(str(path))

    assert code == 0
    assert stdout == f"open: {GOOD_NOTES_OPEN_COUNT + 1}\n".encode("ascii")
    assert stderr == b""


def test_command_refuses_a_named_pipe_without_hanging(tmp_path: Path) -> None:
    """A named pipe is refused before the timeout, with nothing on stdout (FR-010)."""
    if not hasattr(os, "mkfifo"):
        pytest.skip("this platform cannot create named pipes")
    pipe = tmp_path / "pipe"
    try:
        os.mkfifo(pipe)
    except OSError as error:
        pytest.skip(f"a named pipe cannot be created here: {error}")
    expected = f"scratch_notes: not a regular file: {str(pipe)!a}\n".encode("ascii")

    outcome = _run_script(str(pipe))

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2] == expected


def test_command_refuses_a_device() -> None:
    """``/dev/null`` is refused with a non-zero exit and nothing on stdout."""
    if not os.path.exists("/dev/null"):
        pytest.skip("/dev/null does not exist on this platform")

    outcome = _run_script("/dev/null")

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2] == b"scratch_notes: not a regular file: '/dev/null'\n"


def test_command_without_arguments_is_a_usage_failure() -> None:
    """No argument exits 2 with one usage line on stderr."""
    outcome = _run_script()

    _assert_failed_process(outcome, exit_code=2)
    assert outcome[2].startswith(b"scratch_notes: usage:")
    assert b"(expected one file, got 0)" in outcome[2]


def test_command_with_an_unknown_option_is_a_usage_failure(tmp_path: Path) -> None:
    """An unknown option exits 2 and prints no help on stdout."""
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())

    outcome = _run_script(str(path), "--verbose")

    _assert_failed_process(outcome, exit_code=2)
    assert outcome[2].startswith(b"scratch_notes: usage:")
    assert b"(unknown option --verbose)" in outcome[2]


def test_command_on_a_missing_file_fails(tmp_path: Path) -> None:
    """A missing file exits 1 with one line on stderr naming the path."""
    path = str(tmp_path / "absent.md")

    outcome = _run_script(path)

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2] == f"scratch_notes: no such file: {path!a}\n".encode("ascii")


def test_command_on_a_directory_fails(tmp_path: Path) -> None:
    """A directory exits 1 with one line on stderr."""
    outcome = _run_script(str(tmp_path))

    _assert_failed_process(outcome, exit_code=1)
    assert b"not a regular file: " in outcome[2]


def test_command_on_an_unreadable_file_fails(tmp_path: Path) -> None:
    """A file with no permissions exits 1 with one line on stderr."""
    if os.geteuid() == 0:
        pytest.skip("running as the superuser, who can read a file with no permissions")
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())
    path.chmod(0)

    outcome = _run_script(str(path))

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2].startswith(
        f"scratch_notes: cannot read {str(path)!a}: ".encode("ascii")
    )


def test_command_on_invalid_utf8_fails(tmp_path: Path) -> None:
    """Invalid UTF-8 exits 1 with one line on stderr."""
    path = _write(tmp_path / "notes.md", b"- [ ] one\n\xff\n")

    outcome = _run_script(str(path))

    _assert_failed_process(outcome, exit_code=1)
    assert b"not valid UTF-8: " in outcome[2]


def test_command_on_an_oversized_file_fails(tmp_path: Path) -> None:
    """A file one byte over the limit exits 1 and names the limit."""
    path = _write(tmp_path / "notes.md", b"a" * (SIZE_LIMIT_BYTES + 1))

    outcome = _run_script(str(path))

    _assert_failed_process(outcome, exit_code=1)
    assert b"larger than 1048576 bytes: " in outcome[2]


def test_command_on_a_path_with_non_ascii_text_prints_one_ascii_line(
    tmp_path: Path,
) -> None:
    """A missing path with a space and a non-ASCII letter is shown escaped."""
    path = str(tmp_path / "my nötes.md")

    outcome = _run_script(path)

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2].isascii()
    assert outcome[2] == f"scratch_notes: no such file: {path!a}\n".encode("ascii")


def test_command_on_an_unclosed_fence_fails_naming_the_line(tmp_path: Path) -> None:
    """An unclosed fence exits 1 with one line on stderr naming where it opened."""
    path = _write(tmp_path / "notes.md", UNCLOSED_NOTES.encode())

    outcome = _run_script(str(path))

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2] == (
        f"scratch_notes: code fence opened on line {UNCLOSED_NOTES_FENCE_LINE} "
        "is never closed\n"
    ).encode("ascii")


def test_command_never_changes_the_file_it_reads(tmp_path: Path) -> None:
    """A good file and a failing file keep their bytes and modification time."""
    good = _write(tmp_path / "good.md", GOOD_NOTES.encode())
    unclosed = _write(tmp_path / "unclosed.md", UNCLOSED_NOTES.encode())
    before = {
        path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (good, unclosed)
    }

    good_code, _, _ = _run_script(str(good))
    unclosed_code, _, _ = _run_script(str(unclosed))

    after = {
        path: (path.read_bytes(), path.stat().st_mtime_ns) for path in (good, unclosed)
    }
    assert good_code == 0
    assert unclosed_code == 1
    assert after == before


def test_command_refuses_a_python_older_than_3_11(tmp_path: Path) -> None:
    """Under an old system Python, the script names 3.11 on stderr and stops."""
    if not os.path.exists(SYSTEM_PYTHON):
        pytest.skip(f"{SYSTEM_PYTHON} does not exist on this machine")
    probe = subprocess.run(
        [SYSTEM_PYTHON, "-c", "import sys; print('%d.%d.%d' % sys.version_info[:3])"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
        check=False,
    )
    if probe.returncode != 0:
        pytest.skip(f"{SYSTEM_PYTHON} cannot report its version")
    version = probe.stdout.decode("ascii").strip()
    major, minor = (int(part) for part in version.split(".")[:2])
    if (major, minor) >= (3, 11):
        pytest.skip(f"{SYSTEM_PYTHON} is Python {version}, which is not below 3.11")
    path = _write(tmp_path / "notes.md", GOOD_NOTES.encode())

    outcome = _run_script(str(path), interpreter=SYSTEM_PYTHON)

    _assert_failed_process(outcome, exit_code=1)
    assert b"Traceback" not in outcome[2]
    assert outcome[2] == (
        f"scratch_notes: needs Python 3.11 or newer, running {version}\n"
    ).encode("ascii")


def test_command_on_a_file_with_headings_lists_them_under_the_count(
    tmp_path: Path,
) -> None:
    """The script exits 0 with ``open: N``, then the headings in file order."""
    notes = (
        "# Café plans\n"
        "- [ ] book a table\n"
        "- [x] choose a day\n"
        "## Later  \n"
        "```\n"
        "# a comment in code\n"
        "```\n"
        "  + [ ] send invitations\n"
        "#tag\n"
        "### Done\n"
    )
    path = _write(tmp_path / "notes.md", notes.encode())

    code, stdout, stderr = _run_script(str(path))

    assert code == 0
    assert stdout == "open: 2\n# Café plans\n## Later\n### Done\n".encode()
    assert stderr == b""


# Command tests: the script run as a process with --json (FR-007, FR-012)


def test_command_with_json_prints_the_json_line(tmp_path: Path) -> None:
    """The script exits 0 with the exact JSON line on stdout and nothing on stderr."""
    path = _write(tmp_path / "notes.md", SMALL_NOTES.encode())

    code, stdout, stderr = _run_script(str(path), "--json")

    assert code == 0
    assert stdout == SMALL_NOTES_JSON.encode("ascii")
    assert stderr == b""


def test_command_with_json_runs_with_the_standard_library_alone(
    tmp_path: Path,
) -> None:
    """Under ``-I -S``, with no site packages, the JSON line is the same (FR-011)."""
    path = _write(tmp_path / "notes.md", SMALL_NOTES.encode())

    code, stdout, stderr = _run_script(str(path), "--json", flags=("-I", "-S"))

    assert code == 0
    assert stdout == SMALL_NOTES_JSON.encode("ascii")
    assert stderr == b""


def test_command_with_json_first_prints_ascii_for_a_non_ascii_heading(
    tmp_path: Path,
) -> None:
    """With the option before the path, a heading outside ASCII leaves as escapes."""
    path = _write(tmp_path / "notes.md", "# Café plans\n- [ ] book\n".encode())

    code, stdout, stderr = _run_script("--json", str(path))

    assert code == 0
    assert stdout == b'{"open": 1, "headings": ["# Caf\\u00e9 plans"]}\n'
    assert stderr == b""


def test_command_with_json_on_an_unclosed_fence_fails_with_empty_stdout(
    tmp_path: Path,
) -> None:
    """An unclosed fence exits 1 with one stderr line and no JSON on stdout."""
    path = _write(tmp_path / "notes.md", UNCLOSED_NOTES.encode())

    outcome = _run_script(str(path), "--json")

    _assert_failed_process(outcome, exit_code=1)
    assert outcome[2] == (
        f"scratch_notes: code fence opened on line {UNCLOSED_NOTES_FENCE_LINE} "
        "is never closed\n"
    ).encode("ascii")


def test_command_with_json_given_twice_is_a_usage_failure(tmp_path: Path) -> None:
    """``--json`` twice exits 2 with one usage line and nothing on stdout."""
    path = _write(tmp_path / "notes.md", SMALL_NOTES.encode())

    outcome = _run_script(str(path), "--json", "--json")

    _assert_failed_process(outcome, exit_code=2)
    assert outcome[2] == (
        b"scratch_notes: usage: scratch_notes.py <file> [--json] "
        b"(option --json given twice)\n"
    )


def test_command_with_json_timing_stays_under_the_limit_at_the_size_limit(
    tmp_path: Path,
) -> None:
    """Twenty runs in a row on a notes-like 1,048,576-byte sample, with the shell
    prompt's interpreter, each exit 0, and the slowest takes under 50 ms (FR-012)."""
    if not os.path.exists(PROMPT_PYTHON):
        pytest.skip(f"{PROMPT_PYTHON}, the shell prompt's Python, does not exist here")
    text, open_count, headings = _build_sample(SIZE_LIMIT_BYTES)
    path = _write(tmp_path / "sample.md", text.encode())
    exit_codes = []
    timings_ms = []
    last_stdout = b""

    for _ in range(TIMING_RUNS):
        started = time.perf_counter()
        code, last_stdout, _ = _run_script(
            str(path), "--json", interpreter=PROMPT_PYTHON
        )
        timings_ms.append((time.perf_counter() - started) * 1000)
        exit_codes.append(code)

    shown = "timings_ms: " + " ".join(f"{timing:.1f}" for timing in timings_ms)
    print(shown)
    assert exit_codes == [0] * TIMING_RUNS, shown
    assert json.loads(last_stdout) == {"open": open_count, "headings": headings}
    assert max(timings_ms) < TIME_LIMIT_MS, shown


# End-to-end journeys (MAX-86): the finished script run as a process on one sample
# file, the way the shell prompt and the developer call it (FR-007, FR-009, FR-016)

JOURNEY_SAMPLE_BYTES = 4096


def _write_journey_sample(directory: Path) -> tuple[Path, int, list[str]]:
    """Write the journeys' one sample notes file and return it with its tallies.

    The sample comes from ``_build_sample``, so it holds headings, open items, done
    items, nested open items and fenced blocks with look-alike lines, and its count
    and headings are known from how it was built.

    Args:
        directory: the directory to write the file in.

    Returns:
        The file's path, the number of open items it was built with, and the headings
        it was built with, in order.
    """
    text, open_count, headings = _build_sample(JOURNEY_SAMPLE_BYTES)
    path = _write(directory / "notes.md", text.encode())
    return path, open_count, headings


def _old_system_python_version() -> str:
    """Return the version of the system Python, skipping the test unless it is old.

    Returns:
        The version of ``SYSTEM_PYTHON`` as ``major.minor.micro``, which is below
        3.11.
    """
    if not os.path.exists(SYSTEM_PYTHON):
        pytest.skip(f"{SYSTEM_PYTHON} does not exist on this machine")
    probe = subprocess.run(
        [SYSTEM_PYTHON, "-c", "import sys; print('%d.%d.%d' % sys.version_info[:3])"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=PROCESS_TIMEOUT_SECONDS,
        check=False,
    )
    if probe.returncode != 0:
        pytest.skip(f"{SYSTEM_PYTHON} cannot report its version")
    version = probe.stdout.decode("ascii").strip()
    major, minor = (int(part) for part in version.split(".")[:2])
    if (major, minor) >= (3, 11):
        pytest.skip(f"{SYSTEM_PYTHON} is Python {version}, which is not below 3.11")
    return version


def _missing_file_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a path that does not exist.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    path = str(directory / "absent.md")
    return [path], f"no such file: {path!a}\n".encode("ascii")


def _directory_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a path that is a directory.

    Args:
        directory: the test's own temporary directory, which is the path given.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    path = str(directory)
    return [path], f"not a regular file: {path!a}\n".encode("ascii")


def _oversized_file_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a file one byte over the size limit.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    path = str(_write(directory / "notes.md", b"a" * (SIZE_LIMIT_BYTES + 1)))
    return [path], f"larger than 1048576 bytes: {path!a}\n".encode("ascii")


def _invalid_utf8_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a file whose bytes are not valid UTF-8, after a heading and an item.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    path = str(_write(directory / "notes.md", b"# Plan\n- [ ] one\n\xff\n"))
    return [path], f"not valid UTF-8: {path!a}\n".encode("ascii")


def _unclosed_fence_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a file that ends inside a fence.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    path = str(_write(directory / "notes.md", UNCLOSED_NOTES.encode()))
    message = f"code fence opened on line {UNCLOSED_NOTES_FENCE_LINE} is never closed\n"
    return [path], message.encode("ascii")


def _no_file_argument_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a command line that names no file.

    Args:
        directory: the test's own temporary directory; nothing is written to it.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    message = b"usage: scratch_notes.py <file> [--json] (expected one file, got 0)\n"
    return [], message


def _unknown_option_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange an unknown option beside the journeys' good sample file.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    path, _, _ = _write_journey_sample(directory)
    message = b"usage: scratch_notes.py <file> [--json] (unknown option --verbose)\n"
    return [str(path), "--verbose"], message


def _unreadable_file_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange the journeys' sample file with all its permissions removed.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``; the operating system's own
        reason follows it.
    """
    if os.geteuid() == 0:
        pytest.skip("running as the superuser, who can read a file with no permissions")
    path, _, _ = _write_journey_sample(directory)
    path.chmod(0)
    return [str(path)], f"cannot read {str(path)!a}: ".encode("ascii")


def _named_pipe_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange a path that is a named pipe, which would block a script that opened it.

    Args:
        directory: the test's own temporary directory.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    if not hasattr(os, "mkfifo"):
        pytest.skip("this platform cannot create named pipes")
    pipe = directory / "pipe"
    try:
        os.mkfifo(pipe)
    except OSError as error:
        pytest.skip(f"a named pipe cannot be created here: {error}")
    return [str(pipe)], f"not a regular file: {str(pipe)!a}\n".encode("ascii")


def _device_failure(directory: Path) -> tuple[list[str], bytes]:
    """Arrange the path ``/dev/null``, a device.

    Args:
        directory: the test's own temporary directory; nothing is written to it.

    Returns:
        The arguments for the script, without ``--json``, and the start of the message
        the script must print after ``scratch_notes: ``.
    """
    if not os.path.exists("/dev/null"):
        pytest.skip("/dev/null does not exist on this platform")
    return ["/dev/null"], b"not a regular file: '/dev/null'\n"


JOURNEY_FAILURES = {
    "missing-file": (_missing_file_failure, 1),
    "directory": (_directory_failure, 1),
    "oversized-file": (_oversized_file_failure, 1),
    "invalid-utf8": (_invalid_utf8_failure, 1),
    "unclosed-fence": (_unclosed_fence_failure, 1),
    "no-file-argument": (_no_file_argument_failure, 2),
    "unknown-option": (_unknown_option_failure, 2),
    "unreadable-file": (_unreadable_file_failure, 1),
    "named-pipe": (_named_pipe_failure, 1),
    "device": (_device_failure, 1),
}


def test_journey_prompt_reads_the_open_count_from_one_json_line(
    tmp_path: Path,
) -> None:
    """The prompt's journey: ``--json`` on the sample exits 0 with one JSON line whose
    ``open`` is the count the sample was built with (FR-007)."""
    path, open_count, _ = _write_journey_sample(tmp_path)

    code, stdout, stderr = _run_script(str(path), "--json")

    assert open_count > 0
    assert code == 0
    assert stderr == b""
    assert stdout.endswith(b"\n")
    assert stdout.count(b"\n") == 1
    parsed = json.loads(stdout)
    assert type(parsed["open"]) is int
    assert parsed["open"] == open_count


def test_journey_developer_sees_the_count_and_headings_the_prompt_gets(
    tmp_path: Path,
) -> None:
    """The developer's journey: the plain run on the same file shows the JSON run's
    count on its first line, then the JSON run's headings in the same order (FR-016)."""
    path, _, headings = _write_journey_sample(tmp_path)

    json_code, json_stdout, _ = _run_script(str(path), "--json")
    code, stdout, stderr = _run_script(str(path))

    assert json_code == 0
    from_json = json.loads(json_stdout)
    assert headings
    assert from_json["headings"] == headings
    assert code == 0
    assert stderr == b""
    assert stdout.endswith(b"\n")
    lines = stdout.decode("utf-8")[:-1].split("\n")
    assert lines[0] == f"open: {from_json['open']}"
    assert lines[1:] == from_json["headings"]


@pytest.mark.parametrize(
    "as_json",
    [
        pytest.param(False, id="plain"),
        pytest.param(True, id="json"),
    ],
)
@pytest.mark.parametrize("failure", list(JOURNEY_FAILURES))
def test_journey_failure_leaves_stdout_empty_and_one_line_on_stderr(
    tmp_path: Path, failure: str, as_json: bool
) -> None:
    """The failure journey: each failure, in plain mode and with ``--json``, exits
    with its code, prints nothing on stdout and one line on stderr (FR-009)."""
    arrange, exit_code = JOURNEY_FAILURES[failure]
    arguments, message_start = arrange(tmp_path)
    if as_json:
        arguments.append("--json")

    outcome = _run_script(*arguments)

    _assert_failed_process(outcome, exit_code)
    assert outcome[2].startswith(ERROR_PREFIX.encode("ascii") + message_start)


def test_journey_failure_under_an_old_python_with_json_names_3_11(
    tmp_path: Path,
) -> None:
    """The failure journey under an old system Python: with ``--json`` the script
    exits 1, prints nothing on stdout and names 3.11 on one stderr line (FR-013)."""
    version = _old_system_python_version()
    path, _, _ = _write_journey_sample(tmp_path)

    outcome = _run_script(str(path), "--json", interpreter=SYSTEM_PYTHON)

    _assert_failed_process(outcome, exit_code=1)
    assert b"Traceback" not in outcome[2]
    assert outcome[2] == (
        f"scratch_notes: needs Python 3.11 or newer, running {version}\n"
    ).encode("ascii")
