"""Count the open checklist items in one Markdown notes file and list its headings.

Run it by path, with any Python 3.11 or newer::

    python3 scratch_notes.py <file>
    python3 scratch_notes.py <file> --json

On success the first form prints ``open: N`` on stdout, where N is the number of open
checklist items outside fenced code, then one line per heading outside fenced code, in
file order, and exits with code 0. The second form prints the same count and headings
as one line of JSON, ``{"open": N, "headings": [...]}``, in pure ASCII; ``--json`` may
come before or after the file. An open item is a line that, after any indentation,
holds ``-``, ``*`` or ``+``, then one or more spaces or tabs, then exactly ``[ ]``. A
heading is a line that starts, with no indentation, with one to six ``#`` followed by
a space, a tab or the end of the line; it is printed as written, without its trailing
spaces and tabs.

Every failure prints one line, ``scratch_notes: <message>``, on stderr, leaves stdout
empty and exits non-zero: 2 for a wrong command line and 1 for everything else. A
failed run can therefore never be read as "nothing open".

The work is done by small functions run in a fixed order: the version guard, the
arguments, the read, the scan and the rendering. Only ``read_notes`` touches the
filesystem and only ``main`` writes to the process's streams. The file imports nothing
outside the standard library and keeps to syntax that Python 3.9 can parse, so that
the version guard can run, and report itself, on an old interpreter.
"""

from __future__ import annotations

import json
import os
import re
import stat
import sys

PROGRAM_NAME = "scratch_notes"
USAGE = "usage: scratch_notes.py <file> [--json]"
MINIMUM_PYTHON = (3, 11)
MAX_NOTES_BYTES = 1_048_576
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2

_OPTION_PREFIX = "-"
_JSON_OPTION = "--json"
_BYTE_ORDER_MARK = "﻿"
_TRAILING_WHITESPACE = " \t"

_FENCE_OPENER = re.compile(r"[ \t]*(?:(?P<backticks>`{3,})[^`]*|(?P<tildes>~{3,}).*)")
_FENCE_CLOSER = re.compile(r"[ \t]*(?P<run>`+|~+)[ \t]*")
_OPEN_ITEM = re.compile(r"[ \t]*[-*+][ \t]+\[ \]")
_HEADING = re.compile(r"#{1,6}(?:[ \t]|\Z)")


class ScratchNotesError(Exception):
    """A failure the script reports as one line on stderr.

    Attributes:
        message: one line of text, without a line ending, saying what failed.
        exit_code: the code the process exits with for this kind of failure.
    """

    exit_code = EXIT_FAILURE

    def __init__(self, message: str) -> None:
        """Keep the message.

        Args:
            message: one line of text, without a line ending.
        """
        super().__init__(message)
        self.message = message


class UsageError(ScratchNotesError):
    """The command line does not name exactly one file and at most one ``--json``."""

    exit_code = EXIT_USAGE

    def __init__(self, reason: str) -> None:
        """Build the usage message.

        Args:
            reason: what was wrong with the arguments, shown in brackets.
        """
        super().__init__(f"{USAGE} ({reason})")


class UnsupportedPythonError(ScratchNotesError):
    """The running Python is older than the script supports."""

    def __init__(self, major: int, minor: int, micro: int) -> None:
        """Build the message from the running version.

        Args:
            major: the running version's first number.
            minor: the running version's second number.
            micro: the running version's third number.
        """
        needed = ".".join(str(part) for part in MINIMUM_PYTHON)
        super().__init__(
            f"needs Python {needed} or newer, running {major}.{minor}.{micro}"
        )


class NotesFileMissingError(ScratchNotesError):
    """The path, or a directory in it, does not exist."""

    def __init__(self, path: str) -> None:
        """Build the message.

        Args:
            path: the path as given on the command line.
        """
        super().__init__(f"no such file: {path!a}")


class NotARegularFileError(ScratchNotesError):
    """The path is a directory, a named pipe, a device or a socket."""

    def __init__(self, path: str) -> None:
        """Build the message.

        Args:
            path: the path as given on the command line.
        """
        super().__init__(f"not a regular file: {path!a}")


class NotesFileTooLargeError(ScratchNotesError):
    """The file holds more bytes than the size limit."""

    def __init__(self, path: str) -> None:
        """Build the message.

        Args:
            path: the path as given on the command line.
        """
        super().__init__(f"larger than {MAX_NOTES_BYTES} bytes: {path!a}")


class NotesFileUnreadableError(ScratchNotesError):
    """The operating system refused to look the file up or to read it."""

    def __init__(self, path: str, reason: str) -> None:
        """Build the message.

        Args:
            path: the path as given on the command line.
            reason: the operating system's reason for refusing.
        """
        super().__init__(f"cannot read {path!a}: {reason}")


class NotesFileEncodingError(ScratchNotesError):
    """The file's bytes are not valid UTF-8."""

    def __init__(self, path: str) -> None:
        """Build the message.

        Args:
            path: the path as given on the command line.
        """
        super().__init__(f"not valid UTF-8: {path!a}")


class UnclosedFenceError(ScratchNotesError):
    """The text ends inside a fenced code block."""

    def __init__(self, line_number: int) -> None:
        """Build the message.

        Args:
            line_number: the line, counted from 1, where the fence opened.
        """
        super().__init__(f"code fence opened on line {line_number} is never closed")


class CommandRequest:
    """What the arguments asked for.

    Attributes:
        path: the one file to read, exactly as given.
        as_json: true when ``--json`` was given, so the result is one line of JSON;
            false for plain text.
    """

    def __init__(self, path: str, as_json: bool = False) -> None:
        """Keep the request's fields.

        Args:
            path: the one file to read, exactly as given.
            as_json: whether the result is wanted as JSON; plain text unless stated.
        """
        self.path = path
        self.as_json = as_json


class NotesSummary:
    """What one scan of a notes file found.

    Attributes:
        open_count: how many lines outside fenced code match the open-item rule.
        headings: the lines outside fenced code that match the heading rule, in file
            order, each exactly as written, ``#`` marks included, without its line
            ending or trailing spaces and tabs.
    """

    def __init__(self, open_count: int, headings: list[str]) -> None:
        """Keep the summary's fields.

        Args:
            open_count: how many open items the scan counted; zero or more.
            headings: the headings the scan collected, in file order.
        """
        self.open_count = open_count
        self.headings = headings


class CommandResult:
    """Everything one run hands back to the process.

    Attributes:
        exit_code: 0 on success, above zero on failure.
        stdout: the text for stdout; empty on failure.
        stderr: the text for stderr; empty on success, otherwise one line ending in
            a line feed.
    """

    def __init__(self, exit_code: int, stdout: str, stderr: str) -> None:
        """Keep the result's fields.

        Args:
            exit_code: 0 on success, above zero on failure.
            stdout: the text for stdout.
            stderr: the text for stderr.
        """
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def check_python_version(major: int, minor: int, micro: int) -> None:
    """Refuse to run on a Python older than ``MINIMUM_PYTHON``.

    Args:
        major: the first number of the version to check.
        minor: the second number of the version to check.
        micro: the third number of the version to check.

    Raises:
        UnsupportedPythonError: when the version is below ``MINIMUM_PYTHON``.
    """
    if (major, minor) < MINIMUM_PYTHON:
        raise UnsupportedPythonError(major, minor, micro)


def _show_argument(argument: str) -> str:
    """Return an argument in a form that always fits on one line of a message.

    Printable ASCII is shown as given. Anything else, such as an argument holding a
    line feed or a character outside ASCII, is shown in escaped ASCII inside quotes.

    Args:
        argument: one command-line argument.
    """
    if argument.isascii() and argument.isprintable():
        return argument
    return ascii(argument)


def parse_arguments(arguments: list[str]) -> CommandRequest:
    """Turn the command-line arguments into a request.

    An argument that starts with ``-`` is an option, and the only known option is
    ``--json``, which may be given once, before or after the path. Every other
    argument is a file path, and exactly one is required. An unknown option is
    reported first, then a repeated ``--json``, then a wrong number of paths.

    Args:
        arguments: the arguments after the script name.

    Returns:
        The request holding the one path, exactly as given, and whether ``--json``
        was given.

    Raises:
        UsageError: on an unknown option, on ``--json`` given more than once, or on
            anything other than exactly one path.
    """
    options = [item for item in arguments if item.startswith(_OPTION_PREFIX)]
    paths = [item for item in arguments if not item.startswith(_OPTION_PREFIX)]
    unknown = [item for item in options if item != _JSON_OPTION]
    if unknown:
        raise UsageError(f"unknown option {_show_argument(unknown[0])}")
    if len(options) > 1:
        raise UsageError(f"option {_JSON_OPTION} given twice")
    if len(paths) != 1:
        raise UsageError(f"expected one file, got {len(paths)}")
    return CommandRequest(paths[0], as_json=bool(options))


def _operating_system_reason(error: OSError) -> str:
    """Return the operating system's one-line reason for an error.

    Args:
        error: the error the operating system raised.
    """
    return error.strerror or type(error).__name__


def read_notes(path: str) -> str:
    """Read one regular file of at most ``MAX_NOTES_BYTES`` bytes as UTF-8 text.

    The path is looked up once, following symbolic links, and its file type and
    recorded size are checked before anything is opened, so a named pipe or a device
    can never block the read. At most the limit plus one byte is then read, so a file
    that grew after the lookup is still refused. The file is closed before the bytes
    are decoded.

    Args:
        path: the file to read, exactly as given on the command line.

    Returns:
        The file's text, without a leading byte-order mark.

    Raises:
        NotesFileMissingError: when the path, or a directory in it, does not exist.
        NotARegularFileError: when the path is not a regular file.
        NotesFileTooLargeError: when the file is, or yields, more than the limit.
        NotesFileUnreadableError: when the operating system refuses the lookup or
            the read.
        NotesFileEncodingError: when the bytes are not valid UTF-8.
    """
    try:
        status = os.stat(path)
    except (FileNotFoundError, NotADirectoryError):
        raise NotesFileMissingError(path) from None
    except OSError as error:
        reason = _operating_system_reason(error)
        raise NotesFileUnreadableError(path, reason) from None
    if not stat.S_ISREG(status.st_mode):
        raise NotARegularFileError(path)
    if status.st_size > MAX_NOTES_BYTES:
        raise NotesFileTooLargeError(path)

    chunks = []
    remaining = MAX_NOTES_BYTES + 1
    try:
        with open(path, "rb", buffering=0) as notes_file:
            while remaining > 0:
                chunk = notes_file.read(remaining)
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
    except OSError as error:
        reason = _operating_system_reason(error)
        raise NotesFileUnreadableError(path, reason) from None
    if remaining == 0:
        raise NotesFileTooLargeError(path)

    try:
        text = b"".join(chunks).decode("utf-8")
    except UnicodeDecodeError:
        raise NotesFileEncodingError(path) from None
    text = text.removeprefix(_BYTE_ORDER_MARK)
    return text


def scan_notes(text: str) -> NotesSummary:
    """Apply the line rules to the text of a notes file.

    The text is split at line feeds only, and one trailing carriage return is removed
    from each line. Outside a fence, a line that opens a fence is tested first, then a
    line that is an open item, then a line that is a heading: one to six ``#`` with no
    indentation, followed by a space, a tab or the end of the line. Inside a fence,
    only a line that closes it matters: the fence's own character, at least as many
    times as it was opened with, then optional spaces and tabs. The count and the
    headings come from the same pass, so they always describe the same text. The
    function is pure: the same text always gives the same summary.

    Args:
        text: the whole file's text, without a leading byte-order mark.

    Returns:
        The summary holding the count of open items outside fenced code and the
        headings outside fenced code, in file order, each without its trailing spaces
        and tabs.

    Raises:
        UnclosedFenceError: when the text ends inside a fence, carrying the line
            number where that fence opened.
    """
    open_count = 0
    headings = []
    fence_marker = ""
    fence_length = 0
    fence_opened_at = 0
    for number, line in enumerate(text.split("\n"), start=1):
        line = line.removesuffix("\r")
        if fence_marker:
            closer = _FENCE_CLOSER.fullmatch(line)
            if closer:
                run = closer.group("run")
                if run[0] == fence_marker and len(run) >= fence_length:
                    fence_marker = ""
            continue
        opener = _FENCE_OPENER.fullmatch(line)
        if opener:
            run = opener.group("backticks") or opener.group("tildes")
            fence_marker = run[0]
            fence_length = len(run)
            fence_opened_at = number
        elif _OPEN_ITEM.match(line):
            open_count += 1
        elif _HEADING.match(line):
            headings.append(line.rstrip(_TRAILING_WHITESPACE))
    if fence_marker:
        raise UnclosedFenceError(fence_opened_at)
    return NotesSummary(open_count, headings)


def render_plain(summary: NotesSummary) -> str:
    """Lay a summary out as plain text.

    Headings are written as the summary holds them; nothing in them is escaped.

    Args:
        summary: what the scan found.

    Returns:
        The line ``open: N``, then one line per heading in the summary's order, each
        line ending in a line feed. With no headings, only the ``open: N`` line.
    """
    lines = [f"open: {summary.open_count}", *summary.headings]
    return "\n".join(lines) + "\n"


def render_json(summary: NotesSummary) -> str:
    """Lay a summary out as one line of JSON.

    The standard encoder's defaults are used unchanged: a comma and a space between
    items, a colon and a space after each key, and a ``\\u`` escape for every
    character outside ASCII. Quotes, backslashes and control characters in a heading
    are escaped too, so the line is pure ASCII and no heading can break it.

    Args:
        summary: what the scan found.

    Returns:
        A JSON object with exactly two keys, ``open``, a number, then ``headings``,
        a list of text in the summary's order, followed by one line feed.
    """
    return json.dumps({"open": summary.open_count, "headings": summary.headings}) + "\n"


def run(arguments: list[str]) -> CommandResult:
    """Do one whole run without writing to stdout or stderr.

    The steps run in a fixed order: the version guard, the arguments, the read, the
    scan and the rendering, as JSON when the arguments ask for it and as plain text
    otherwise. The result is complete before it is returned, so a failure never
    follows partial output.

    Args:
        arguments: the arguments after the script name.

    Returns:
        The exit code with the text for stdout and stderr. Every error in the
        ``ScratchNotesError`` family becomes a failed result with empty stdout and
        one line for stderr; nothing from that family is raised.
    """
    try:
        check_python_version(*sys.version_info[:3])
        request = parse_arguments(arguments)
        summary = scan_notes(read_notes(request.path))
        render = render_json if request.as_json else render_plain
        output = render(summary)
    except ScratchNotesError as error:
        return CommandResult(error.exit_code, "", f"{PROGRAM_NAME}: {error.message}\n")
    return CommandResult(EXIT_SUCCESS, output, "")


def main() -> int:
    """Run the command on the process's own arguments and write the result out.

    Stdout and stderr are written as UTF-8 bytes, whatever the terminal's locale.

    Returns:
        The exit code for the process.
    """
    result = run(sys.argv[1:])
    sys.stdout.buffer.write(result.stdout.encode("utf-8"))
    sys.stderr.buffer.write(result.stderr.encode("utf-8"))
    return result.exit_code


if __name__ == "__main__":
    sys.exit(main())
