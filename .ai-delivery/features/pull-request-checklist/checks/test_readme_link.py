"""Acceptance checks for the README pointer to the pull request checklist (contract C2).

The README's last paragraph must be exactly one sentence holding exactly one Markdown
inline link whose target is exactly ``CONTRIBUTING.md``, and that sentence must use the
word "checklist". The file must still begin with ``# kit-scratch`` and end with exactly
one newline.

Every failure names its condition from contract C4's error taxonomy (MissingDocument,
TitleMissing, FileEnding, PointerSentenceCount, LinkTargetMismatch, PointerUnlabelled)
and quotes the offending text. The parsing lives in pure functions that take README
text, so the real-file checks and the adverse checks against inline samples exercise
the same code.

This module reads only ``README.md``. It never reads ``CONTRIBUTING.md``, the
environment, the network or git. It lives outside pytest's default collection on
purpose (ADR-001), so run it by naming its path on the command line.
"""

import functools
import re
from collections.abc import Callable
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
README_PATH = REPO_ROOT / "README.md"

EXPECTED_TITLE = "# kit-scratch"
EXPECTED_LINK_TARGET = "CONTRIBUTING.md"
REQUIRED_WORD = "checklist"

_BLANK_LINE = re.compile(r"\n[ \t]*\n")
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^()\s]*\)")
_SENTENCE_END = re.compile(r"[.?!](?=\s|$)")
_INLINE_LINK = re.compile(r"\[([^\[\]]*)\]\(([^()\s]*)\)")
_REQUIRED_WORD = re.compile(rf"\b{REQUIRED_WORD}\b", re.IGNORECASE)


class ReadmeContractError(Exception):
    """Raised when README text breaks contract C2.

    Attributes:
        condition: the C4 error-taxonomy name of the failed criterion.
    """

    def __init__(self, condition: str, detail: str) -> None:
        """Build the error from a C4 condition name and a detail quoting the text.

        Args:
            condition: the C4 error-taxonomy name, such as "LinkTargetMismatch".
            detail: what was wrong, quoting the offending line or text.
        """
        super().__init__(f"{condition}: {detail}")
        self.condition = condition


def last_paragraph(text: str) -> str:
    """Return the last non-empty paragraph of ``text`` with its whitespace collapsed.

    Paragraphs are separated by blank lines (lines empty or holding only spaces and
    tabs). Returns an empty string when the text holds no paragraph at all.

    Args:
        text: the full Markdown text.
    """
    paragraphs = [part for part in _BLANK_LINE.split(text) if part.strip()]
    if not paragraphs:
        return ""
    return " ".join(paragraphs[-1].split())


def count_sentences(paragraph: str) -> int:
    """Count sentences in ``paragraph`` by contract C4's sentence-counting rule.

    A sentence ends at ``.``, ``?`` or ``!`` followed by whitespace or the end of the
    text. Full stops inside backtick code spans and inside a link's target do not
    count, so ``CONTRIBUTING.md`` never ends a sentence. Trailing text after the last
    sentence end counts as one more, unterminated, sentence.

    Args:
        paragraph: a single paragraph of Markdown text.
    """
    masked = _CODE_SPAN.sub("``", paragraph)
    masked = _LINK_TARGET.sub("]()", masked)
    ends = list(_SENTENCE_END.finditer(masked))
    count = len(ends)
    tail_start = ends[-1].end() if ends else 0
    if masked[tail_start:].strip():
        count += 1
    return count


def find_links(paragraph: str) -> list[tuple[str, str]]:
    """Return every Markdown inline link in ``paragraph`` as ``(text, target)`` pairs.

    Args:
        paragraph: a single paragraph of Markdown text.
    """
    return [
        (match.group(1), match.group(2)) for match in _INLINE_LINK.finditer(paragraph)
    ]


def check_title(text: str) -> None:
    """Check that the first line is the title and no second level-1 heading exists.

    Args:
        text: the full README text.

    Raises:
        ReadmeContractError: TitleMissing, quoting the offending line.
    """
    lines = text.split("\n")
    if lines[0] != EXPECTED_TITLE:
        raise ReadmeContractError(
            "TitleMissing", f"first line is {lines[0]!r}, expected {EXPECTED_TITLE!r}"
        )
    for number, line in enumerate(lines[1:], start=2):
        if line.startswith("# "):
            raise ReadmeContractError(
                "TitleMissing", f"second level-1 heading on line {number}: {line!r}"
            )


def check_file_ending(text: str) -> None:
    """Check that the text ends with exactly one newline.

    Args:
        text: the full README text.

    Raises:
        ReadmeContractError: FileEnding, quoting the file's last characters.
    """
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ReadmeContractError(
            "FileEnding",
            f"file must end with exactly one newline; it ends {text[-20:]!r}",
        )


def check_pointer_sentence_count(text: str) -> None:
    """Check that the last paragraph is exactly one sentence.

    Args:
        text: the full README text.

    Raises:
        ReadmeContractError: PointerSentenceCount, quoting the last paragraph.
    """
    paragraph = last_paragraph(text)
    count = count_sentences(paragraph)
    if count != 1:
        raise ReadmeContractError(
            "PointerSentenceCount",
            f"last paragraph has {count} sentences, expected 1: {paragraph!r}",
        )


def check_link_target(text: str) -> None:
    """Check that the last paragraph holds exactly one link, targeting CONTRIBUTING.md.

    Args:
        text: the full README text.

    Raises:
        ReadmeContractError: LinkTargetMismatch, quoting the paragraph or its links.
    """
    paragraph = last_paragraph(text)
    links = find_links(paragraph)
    if len(links) != 1:
        raise ReadmeContractError(
            "LinkTargetMismatch",
            f"last paragraph has {len(links)} inline links, expected 1: {paragraph!r}",
        )
    target = links[0][1]
    if target != EXPECTED_LINK_TARGET:
        raise ReadmeContractError(
            "LinkTargetMismatch",
            f"link target is {target!r}, expected exactly {EXPECTED_LINK_TARGET!r}",
        )


def check_pointer_labelled(text: str) -> None:
    """Check that the last paragraph uses the word "checklist".

    Args:
        text: the full README text.

    Raises:
        ReadmeContractError: PointerUnlabelled, quoting the last paragraph.
    """
    paragraph = last_paragraph(text)
    if not _REQUIRED_WORD.search(paragraph):
        raise ReadmeContractError(
            "PointerUnlabelled",
            f"last paragraph does not say {REQUIRED_WORD!r}: {paragraph!r}",
        )


@functools.cache
def read_readme() -> str:
    """Read the repository's README once, byte-exact, so line endings are preserved.

    Raises:
        ReadmeContractError: MissingDocument, when README.md is absent at the root.
    """
    if not README_PATH.is_file():
        raise ReadmeContractError("MissingDocument", f"no file at {str(README_PATH)!r}")
    return README_PATH.read_bytes().decode("utf-8")


def _raised_condition(check: Callable[[str], None], text: str) -> str | None:
    """Run ``check`` on ``text`` and return the C4 condition it raised, if any.

    Args:
        check: one of this module's check functions.
        text: the sample README text to check.
    """
    try:
        check(text)
    except ReadmeContractError as error:
        return error.condition
    return None


_SAMPLE_BODY = (
    "# kit-scratch\n"
    "\n"
    "kit-scratch is a fixture for exercising the ai-delivery kit. It is not a product.\n"
)
_GOOD_SENTENCE = "Before you open a pull request, read the [pull request checklist](CONTRIBUTING.md).\n"


def test_readme_exists_at_root() -> None:
    """README.md exists at the repository root and holds text (MissingDocument)."""
    text = read_readme()
    assert text.strip(), f"MissingDocument: {str(README_PATH)!r} is empty"


def test_readme_first_line_is_title() -> None:
    """The first line is ``# kit-scratch``, the only level-1 heading (TitleMissing)."""
    check_title(read_readme())


def test_readme_last_paragraph_is_one_sentence() -> None:
    """The last paragraph is exactly one sentence (PointerSentenceCount)."""
    check_pointer_sentence_count(read_readme())


def test_readme_last_paragraph_links_to_contributing() -> None:
    """The last paragraph holds one link, targeting exactly CONTRIBUTING.md."""
    check_link_target(read_readme())


def test_readme_pointer_mentions_checklist() -> None:
    """The last paragraph uses the word "checklist" (PointerUnlabelled)."""
    check_pointer_labelled(read_readme())


def test_readme_ends_with_one_newline() -> None:
    """The file ends with exactly one newline (FileEnding)."""
    check_file_ending(read_readme())


def test_good_sample_passes_every_check() -> None:
    """A sample shaped like the contract's example passes all pointer checks."""
    sample = _SAMPLE_BODY + "\n" + _GOOD_SENTENCE
    checks = (
        check_title,
        check_pointer_sentence_count,
        check_link_target,
        check_pointer_labelled,
        check_file_ending,
    )
    assert [_raised_condition(check, sample) for check in checks] == [None] * len(
        checks
    )


def test_two_sentence_pointer_is_pointer_sentence_count() -> None:
    """A last paragraph of two sentences is reported as PointerSentenceCount."""
    sample = _SAMPLE_BODY + "\nRead this first. See the [checklist](CONTRIBUTING.md).\n"
    assert (
        _raised_condition(check_pointer_sentence_count, sample)
        == "PointerSentenceCount"
    )


def test_sentence_appended_to_previous_line_is_pointer_sentence_count() -> None:
    """A sentence joined to the previous paragraph, with no blank line, fails the count."""
    sample = _SAMPLE_BODY + _GOOD_SENTENCE
    assert (
        _raised_condition(check_pointer_sentence_count, sample)
        == "PointerSentenceCount"
    )


def test_absolute_or_dotted_target_is_link_target_mismatch() -> None:
    """A full GitHub URL or a ``./`` target is reported as LinkTargetMismatch."""
    targets = (
        "https://github.com/maxadamsky/kit-scratch/blob/main/CONTRIBUTING.md",
        "./CONTRIBUTING.md",
    )
    results = [
        _raised_condition(
            check_link_target,
            _SAMPLE_BODY + f"\nRead the [pull request checklist]({target}).\n",
        )
        for target in targets
    ]
    assert results == ["LinkTargetMismatch", "LinkTargetMismatch"]


def test_pointer_without_link_is_link_target_mismatch() -> None:
    """A last paragraph with no link is reported as LinkTargetMismatch."""
    sample = _SAMPLE_BODY + "\nRead the pull request checklist in CONTRIBUTING.md.\n"
    assert _raised_condition(check_link_target, sample) == "LinkTargetMismatch"


def test_pointer_without_checklist_is_pointer_unlabelled() -> None:
    """A sentence that never says "checklist" is reported as PointerUnlabelled."""
    sample = (
        _SAMPLE_BODY
        + "\nBefore you open a pull request, read [this](CONTRIBUTING.md).\n"
    )
    assert _raised_condition(check_pointer_labelled, sample) == "PointerUnlabelled"
