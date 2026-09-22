"""Acceptance checks for the pull request checklist in CONTRIBUTING.md (MAX-45).

These checks prove that the repository's root ``CONTRIBUTING.md`` keeps to contract C1
in ``design/1b-contracts.md``: a title, one tool-neutral introductory sentence, and five
numbered items, each one rule sentence followed by exactly one example. Every failure
message names the C4 condition it reports and quotes the offending text.

The module lives outside pytest's default collection on purpose (ADR-001), so that a
plain ``uv run pytest`` from the repository root still collects nothing. Run it by path::

    PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib \\
        .ai-delivery/features/pull-request-checklist/checks/test_contributing.py

Parsing and checking live in small pure functions that take text and return a list of
findings, one string per problem, empty when the text passes. The real-file tests run
them on ``CONTRIBUTING.md``; the adverse tests run them on inline samples to show each
major check can fail.
"""

import functools
import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"

MIN_LINES = 24
MAX_LINES = 36
ITEM_COUNT = 5
EXAMPLE_MARKER = "Example:"

LEADING_VERBS = {1: "Name", 2: "Make", 3: "Run", 4: "Write", 5: "Link"}

REQUIRED_PHRASES = {
    1: ("<GitHub handle>/<short topic>", "codex/", "agent"),
    2: ("logical change", "several"),
    3: ("uv run pytest", "no tests ran", "exit code 5"),
    4: ("one-paragraph", "why"),
    5: ("GitHub issue", "before", "Linear", "review"),
}

EXCLUDED_TERMS = (
    "kit",
    "ship",
    "ai-delivery",
    "Claude",
    "code of conduct",
    "release process",
    "template",
    "enforcement",
    "CI",
    "licence",
    "license",
)
ALLOWED_REPOSITORY_NAME = "kit-scratch"

CLOSING_KEYWORDS = (
    "close",
    "closes",
    "closed",
    "fix",
    "fixes",
    "fixed",
    "resolve",
    "resolves",
    "resolved",
)

_ITEM_START = re.compile(r"(\d+)\. ")
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^()\s]*\)")
_SENTENCE_END = re.compile(r"[.?!](?:\s+|$)")
_WHITESPACE = re.compile(r"\s+")
_BRANCH_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/[a-z0-9][a-z0-9-]*")
_ISSUE_REFERENCE = re.compile(r"(?<![\w#])#\d+\b")
_CLOSING_KEYWORD = re.compile(
    r"\b(?:" + "|".join(CLOSING_KEYWORDS) + r")\b", re.IGNORECASE
)
_BLANK_LINE = re.compile(r"\n[ \t]*\n")


@dataclass(frozen=True)
class ChecklistItem:
    """One numbered item of the checklist.

    Attributes:
        number: the number at the start of the item's first line.
        header: the item's first line exactly as written, quoted in findings.
        rule: the text before the first ``Example:``, whitespace collapsed.
        example: the raw text after the first ``Example:``, line breaks kept.
        example_count: how many times ``Example:`` appears in the item.
        continuation_lines: the item's lines after its first, exactly as written.
    """

    number: int
    header: str
    rule: str
    example: str
    example_count: int
    continuation_lines: tuple[str, ...]


@dataclass(frozen=True)
class ChecklistDocument:
    """The parsed structure of a checklist document.

    Attributes:
        introduction: the text between the first line and item 1, whitespace
            collapsed.
        items: the numbered items in the order they appear.
    """

    introduction: str
    items: tuple[ChecklistItem, ...]

    def item(self, number: int) -> ChecklistItem | None:
        """Return the first item carrying ``number``, or None when there is none.

        Args:
            number: the item number to look up.
        """
        return next((item for item in self.items if item.number == number), None)


def collapse(text: str) -> str:
    """Return ``text`` with every run of whitespace reduced to one space and trimmed.

    Args:
        text: any text.
    """
    return _WHITESPACE.sub(" ", text).strip()


def count_sentences(text: str) -> int:
    """Count sentences in ``text`` by C4's sentence-counting rule.

    A sentence ends at ``.``, ``?`` or ``!`` followed by whitespace or the end of the
    text. Full stops inside backtick code spans and inside a link's target are ignored,
    so ``CONTRIBUTING.md`` and ``uv run pytest`` never end a sentence. Unterminated
    text after the last sentence end counts as one more sentence.

    Args:
        text: the prose to count.
    """
    masked = _LINK_TARGET.sub("]", _CODE_SPAN.sub("code", text))
    return sum(1 for part in _SENTENCE_END.split(masked) if part.strip())


def parse_document(text: str) -> ChecklistDocument:
    """Parse checklist text into its introduction and numbered items.

    An item starts at a line beginning, at column 0, with a number, a full stop and a
    space, and runs until the next such line or the end of the text. The first line is
    taken as the title and is not part of the introduction.

    Args:
        text: the whole document text.
    """
    lines = tuple(text.splitlines())
    starts = [i for i, line in enumerate(lines) if _ITEM_START.match(line)]
    intro_end = starts[0] if starts else len(lines)
    introduction = collapse("\n".join(lines[1:intro_end]))
    items = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        header = lines[start]
        match = _ITEM_START.match(header)
        assert match is not None
        body = header[match.end() :] + "\n" + "\n".join(lines[start + 1 : end])
        rule, _, example = body.partition(EXAMPLE_MARKER)
        items.append(
            ChecklistItem(
                number=int(match.group(1)),
                header=header,
                rule=collapse(rule),
                example=example.strip(),
                example_count=body.count(EXAMPLE_MARKER),
                continuation_lines=lines[start + 1 : end],
            )
        )
    return ChecklistDocument(introduction=introduction, items=tuple(items))


def check_title(text: str) -> list[str]:
    """Report TitleMissing unless the first line is the only level-1 heading.

    Args:
        text: the whole document text.
    """
    lines = text.splitlines()
    first = lines[0] if lines else ""
    findings = []
    if not first.startswith("# ") or not first[2:].strip():
        findings.append(f"TitleMissing: first line is not a level-1 heading: {first!r}")
    for number, line in enumerate(lines[1:], start=2):
        if line.startswith("# "):
            findings.append(
                f"TitleMissing: second level-1 heading on line {number}: {line!r}"
            )
    return findings


def check_introduction(document: ChecklistDocument) -> list[str]:
    """Report IntroductionCount or IntroductionNotToolNeutral for the introduction.

    Args:
        document: the parsed document.
    """
    intro = document.introduction
    findings = []
    sentences = count_sentences(intro)
    if sentences != 1:
        findings.append(
            f"IntroductionCount: expected 1 sentence, found {sentences}: {intro!r}"
        )
    if not re.search(r"\btool\b", intro, re.IGNORECASE):
        findings.append(
            f"IntroductionNotToolNeutral: introduction lacks the word 'tool': {intro!r}"
        )
    return findings


def check_item_count(document: ChecklistDocument) -> list[str]:
    """Report ItemCount unless exactly five items are numbered 1 to 5 in order.

    Args:
        document: the parsed document.
    """
    numbers = [item.number for item in document.items]
    expected = list(range(1, ITEM_COUNT + 1))
    if numbers == expected:
        return []
    headers = [item.header for item in document.items]
    return [
        f"ItemCount: expected items numbered {expected}, found {numbers}: {headers!r}"
    ]


def check_leading_verbs(document: ChecklistDocument) -> list[str]:
    """Report ItemContent for any item whose rule does not begin with its leading verb.

    Args:
        document: the parsed document.
    """
    findings = []
    for number, verb in LEADING_VERBS.items():
        item = document.item(number)
        if item is None:
            findings.append(f"ItemContent: item {number} is missing")
            continue
        first_word = item.rule.split(" ", 1)[0]
        if first_word != verb:
            findings.append(
                f"ItemContent: item {number} rule must begin with {verb!r}: {item.rule!r}"
            )
    return findings


def check_required_phrases(document: ChecklistDocument) -> list[str]:
    """Report ItemContent for each required phrase an item's rule lacks.

    Phrases are matched without regard to case.

    Args:
        document: the parsed document.
    """
    findings = []
    for number, phrases in REQUIRED_PHRASES.items():
        item = document.item(number)
        if item is None:
            findings.append(f"ItemContent: item {number} is missing")
            continue
        rule = item.rule.casefold()
        for phrase in phrases:
            if phrase.casefold() not in rule:
                findings.append(
                    f"ItemContent: item {number} rule lacks {phrase!r}: {item.rule!r}"
                )
    return findings


def check_rule_sentences(document: ChecklistDocument) -> list[str]:
    """Report RuleSentenceCount for any rule that is not exactly one sentence.

    Args:
        document: the parsed document.
    """
    findings = []
    for item in document.items:
        sentences = count_sentences(item.rule)
        if sentences != 1:
            findings.append(
                f"RuleSentenceCount: item {item.number} rule has {sentences} sentences: "
                f"{item.rule!r}"
            )
    return findings


def check_example_count(document: ChecklistDocument) -> list[str]:
    """Report ExampleCount for any item without exactly one ``Example:``.

    Args:
        document: the parsed document.
    """
    return [
        f"ExampleCount: item {item.number} has {item.example_count} examples: "
        f"{item.header!r}"
        for item in document.items
        if item.example_count != 1
    ]


def check_branch_example(document: ChecklistDocument) -> list[str]:
    """Report ItemContent unless item 1's example is one ``handle/topic`` code span.

    The branch name must not start with the reserved ``codex/`` prefix.

    Args:
        document: the parsed document.
    """
    item = document.item(1)
    if item is None:
        return ["ItemContent: item 1 is missing"]
    spans = [span.strip("`") for span in _CODE_SPAN.findall(item.example)]
    if len(spans) != 1:
        return [
            (
                f"ItemContent: item 1 example needs exactly one code span, found "
                f"{len(spans)}: {item.example!r}"
            )
        ]
    branch = spans[0]
    if not _BRANCH_NAME.fullmatch(branch) or branch.startswith("codex/"):
        return [
            (
                f"ItemContent: item 1 example is not a handle/topic branch outside "
                f"codex/: {branch!r}"
            )
        ]
    return []


def check_description_example(document: ChecklistDocument) -> list[str]:
    """Report ItemContent unless item 4's example is one paragraph of 2 or 3 sentences.

    Args:
        document: the parsed document.
    """
    item = document.item(4)
    if item is None:
        return ["ItemContent: item 4 is missing"]
    findings = []
    if _BLANK_LINE.search(item.example):
        findings.append(
            f"ItemContent: item 4 example is more than one paragraph: {item.example!r}"
        )
    sentences = count_sentences(item.example)
    if not 2 <= sentences <= 3:
        findings.append(
            f"ItemContent: item 4 example has {sentences} sentences, expected 2 or 3: "
            f"{collapse(item.example)!r}"
        )
    return findings


def check_issue_example(document: ChecklistDocument) -> list[str]:
    """Report ItemContent unless item 5's example has one ``#<number>`` and no closer.

    A closing keyword is any of ``CLOSING_KEYWORDS`` as a whole word, in any case.

    Args:
        document: the parsed document.
    """
    item = document.item(5)
    if item is None:
        return ["ItemContent: item 5 is missing"]
    findings = []
    references = _ISSUE_REFERENCE.findall(item.example)
    if len(references) != 1:
        findings.append(
            f"ItemContent: item 5 example needs exactly one #<number> reference, found "
            f"{len(references)}: {item.example!r}"
        )
    keyword = _CLOSING_KEYWORD.search(item.example)
    if keyword:
        findings.append(
            f"ItemContent: item 5 example carries closing keyword {keyword.group(0)!r}: "
            f"{item.example!r}"
        )
    return findings


def check_length(text: str) -> list[str]:
    """Report LengthOutOfRange unless the text has 24 to 36 lines, blanks included.

    Args:
        text: the whole document text.
    """
    count = len(text.splitlines())
    if MIN_LINES <= count <= MAX_LINES:
        return []
    return [f"LengthOutOfRange: {count} lines, expected {MIN_LINES} to {MAX_LINES}"]


def check_excluded_terms(text: str) -> list[str]:
    """Report ExcludedTopic for each excluded word or topic, naming its line.

    Terms match as whole words without regard to case. The repository name
    ``kit-scratch`` is removed before matching, so it alone never counts as ``kit``.

    Args:
        text: the whole document text.
    """
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        searchable = re.sub(
            re.escape(ALLOWED_REPOSITORY_NAME), " ", line, flags=re.IGNORECASE
        )
        for term in EXCLUDED_TERMS:
            pattern = r"(?<![\w-])" + re.escape(term) + r"(?![\w-])"
            if re.search(pattern, searchable, re.IGNORECASE):
                findings.append(f"ExcludedTopic: {term!r} on line {number}: {line!r}")
    return findings


def check_trailing_content(document: ChecklistDocument) -> list[str]:
    """Report TrailingContent for any line after item 5's first that starts at column 0.

    Args:
        document: the parsed document.
    """
    last = document.item(ITEM_COUNT)
    if last is None:
        return [f"TrailingContent: item {ITEM_COUNT} is missing, so its end is unknown"]
    return [
        f"TrailingContent: unindented line after item {ITEM_COUNT}: {line!r}"
        for line in last.continuation_lines
        if line.strip() and not line[0].isspace()
    ]


def check_file_ending(text: str) -> list[str]:
    """Report FileEnding unless the text ends with exactly one newline.

    Args:
        text: the whole document text, line endings untranslated.
    """
    if text.endswith("\n") and not text.endswith("\n\n") and not text.endswith("\r\n"):
        return []
    return [f"FileEnding: text does not end with exactly one newline: {text[-20:]!r}"]


@functools.cache
def _contributing_text() -> str:
    """Read ``CONTRIBUTING.md`` once, with line endings untranslated.

    Raises:
        AssertionError: MissingDocument, when the file is absent at the repository root.
    """
    assert CONTRIBUTING.is_file(), f"MissingDocument: no file at {CONTRIBUTING}"
    return CONTRIBUTING.read_bytes().decode("utf-8")


def _contributing_document() -> ChecklistDocument:
    """Return the parsed ``CONTRIBUTING.md``, failing with MissingDocument if absent."""
    return parse_document(_contributing_text())


def _sample(fifth_example: str = "Related to #12.", item_count: int = 5) -> str:
    """Build a small inline checklist sample for the adverse cases.

    Args:
        fifth_example: the text after item 5's ``Example:``.
        item_count: how many numbered items the sample holds, at most five.
    """
    items = [
        f"{number}. {LEADING_VERBS[number]} the thing.\n\n   Example: `a/b`\n"
        for number in range(1, min(item_count, ITEM_COUNT - 1) + 1)
    ]
    if item_count == ITEM_COUNT:
        items.append(f"{ITEM_COUNT}. Link the issue.\n\n   Example: {fifth_example}\n")
    return "# Title\n\nOne sentence about any tool.\n\n" + "\n".join(items)


def test_document_exists_at_root() -> None:
    """CONTRIBUTING.md exists at the repository root and holds text."""
    text = _contributing_text()

    assert text.strip(), f"MissingDocument: {CONTRIBUTING} is empty"


def test_first_line_is_the_only_title() -> None:
    """The first line is a level-1 heading and no other level-1 heading exists."""
    findings = check_title(_contributing_text())

    assert findings == [], "\n".join(findings)


def test_introduction_is_one_tool_neutral_sentence() -> None:
    """Exactly one sentence, containing the word 'tool', precedes item 1."""
    findings = check_introduction(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_exactly_five_items_in_order() -> None:
    """The document holds exactly five items numbered 1 to 5 in order."""
    findings = check_item_count(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_each_rule_begins_with_its_leading_verb() -> None:
    """Items 1 to 5 begin with Name, Make, Run, Write and Link respectively."""
    findings = check_leading_verbs(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_each_rule_contains_its_required_phrases() -> None:
    """Every rule carries each phrase its row in contract C1 requires."""
    findings = check_required_phrases(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_each_rule_is_one_sentence() -> None:
    """Every item's rule is exactly one sentence."""
    findings = check_rule_sentences(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_each_item_has_exactly_one_example() -> None:
    """Every item carries exactly one ``Example:``."""
    findings = check_example_count(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_branch_example_is_handle_topic_outside_codex() -> None:
    """Item 1's example is one ``handle/topic`` branch not starting with ``codex/``."""
    findings = check_branch_example(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_description_example_is_one_short_paragraph() -> None:
    """Item 4's example is one paragraph of two or three sentences."""
    findings = check_description_example(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_issue_example_has_reference_and_no_closing_keyword() -> None:
    """Item 5's example holds one ``#<number>`` reference and no closing keyword."""
    findings = check_issue_example(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_length_is_within_range() -> None:
    """The file has 24 to 36 lines, blank lines included."""
    findings = check_length(_contributing_text())

    assert findings == [], "\n".join(findings)


def test_no_excluded_topic_appears() -> None:
    """No excluded word or out-of-scope topic appears anywhere in the file."""
    findings = check_excluded_terms(_contributing_text())

    assert findings == [], "\n".join(findings)


def test_nothing_follows_item_five() -> None:
    """No line after item 5's first line starts at column 0."""
    findings = check_trailing_content(_contributing_document())

    assert findings == [], "\n".join(findings)


def test_file_ends_with_one_newline() -> None:
    """The file ends with exactly one newline."""
    findings = check_file_ending(_contributing_text())

    assert findings == [], "\n".join(findings)


def test_sample_with_four_items_reports_item_count() -> None:
    """A sample holding four items is reported as ItemCount."""
    document = parse_document(_sample(item_count=4))

    findings = check_item_count(document)

    assert len(findings) == 1
    assert findings[0].startswith("ItemCount:")


def test_sample_item_without_example_reports_example_count() -> None:
    """A sample item with no ``Example:`` is reported as ExampleCount."""
    text = _sample().replace("5. Link the issue.\n\n   Example: ", "5. Link the issue ")
    document = parse_document(text)

    findings = check_example_count(document)

    assert findings == [
        "ExampleCount: item 5 has 0 examples: '5. Link the issue Related to #12.'"
    ]


def test_sample_item_with_two_examples_reports_example_count() -> None:
    """A sample item with two ``Example:`` lines is reported as ExampleCount."""
    document = parse_document(_sample(fifth_example="#1.\n   Example: #2."))

    findings = check_example_count(document)

    assert findings == ["ExampleCount: item 5 has 2 examples: '5. Link the issue.'"]


def test_sample_rule_of_two_sentences_reports_rule_sentence_count() -> None:
    """A sample rule holding two sentences is reported as RuleSentenceCount."""
    text = _sample().replace("2. Make the thing.", "2. Make the thing. Then stop.")
    document = parse_document(text)

    findings = check_rule_sentences(document)

    assert len(findings) == 1
    assert findings[0].startswith("RuleSentenceCount: item 2 rule has 2 sentences")


def test_sentence_count_ignores_code_spans_and_link_targets() -> None:
    """Full stops inside code spans and link targets do not end a sentence."""
    text = "Run `uv run pytest` and read [the list](CONTRIBUTING.md) first."

    assert count_sentences(text) == 1


def test_sample_naming_the_kit_reports_excluded_topic() -> None:
    """A sample naming 'the kit' is reported as ExcludedTopic with its line."""
    findings = check_excluded_terms("# Title\n\nOpen it with the kit.\n")

    assert findings == ["ExcludedTopic: 'kit' on line 3: 'Open it with the kit.'"]


def test_sample_naming_only_the_repository_is_not_excluded() -> None:
    """A sample naming only ``kit-scratch`` raises no ExcludedTopic finding."""
    findings = check_excluded_terms("# Contributing to kit-scratch\n")

    assert findings == []


def test_sample_issue_example_with_closing_keyword_reports_item_content() -> None:
    """A sample item 5 whose example reads ``Closes #12`` is reported as ItemContent."""
    document = parse_document(_sample(fifth_example="Closes #12"))

    findings = check_issue_example(document)

    assert findings == [
        "ItemContent: item 5 example carries closing keyword 'Closes': 'Closes #12'"
    ]
