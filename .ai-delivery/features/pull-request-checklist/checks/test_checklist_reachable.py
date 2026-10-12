"""Integration checks for the pull request checklist and its README link (MAX-47).

These checks prove that the two separately built units join up: the last paragraph of
the repository's ``README.md`` links to a file that sits inside the repository root and
holds the checklist, meaning a level-1 title and exactly five items numbered 1 to 5.
Every failure message names its condition from contract C4's error taxonomy
(MissingDocument, LinkTargetMismatch or UnresolvedLink) and quotes the offending text.

The module lives outside pytest's default collection on purpose (ADR-001), so that a
plain ``uv run pytest`` from the repository root still collects nothing. Run it by
path::

    PYTHONDONTWRITEBYTECODE=1 uv run pytest -p no:cacheprovider --import-mode=importlib \\
        .ai-delivery/features/pull-request-checklist/checks/test_checklist_reachable.py

It re-parses what it needs instead of importing the two unit modules, so that no check
module depends on another. The checks follow the link from a given root directory, so
the adverse cases run against pytest's per-test ``tmp_path`` rather than the real tree.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
README_NAME = "README.md"
CONTRIBUTING_NAME = "CONTRIBUTING.md"
ITEM_NUMBERS = [1, 2, 3, 4, 5]

_BLANK_LINE = re.compile(r"\n[ \t]*\n")
_INLINE_LINK_TARGET = re.compile(r"\[[^\[\]]*\]\(([^()\s]*)\)")
_ITEM_START = re.compile(r"(\d+)\. ")


def last_paragraph(text: str) -> str:
    """Return the last non-empty paragraph of ``text`` with its whitespace collapsed.

    Paragraphs are separated by blank lines. Returns an empty string when the text holds
    no paragraph at all.

    Args:
        text: the full Markdown text.
    """
    paragraphs = [part for part in _BLANK_LINE.split(text) if part.strip()]
    return " ".join(paragraphs[-1].split()) if paragraphs else ""


def pointer_target(readme_text: str) -> tuple[str | None, list[str]]:
    """Return the one link target in the README's last paragraph, and any findings.

    Args:
        readme_text: the full README text.

    Returns:
        The target and an empty list when the last paragraph holds exactly one inline
        link; otherwise None and a LinkTargetMismatch finding.
    """
    paragraph = last_paragraph(readme_text)
    targets = _INLINE_LINK_TARGET.findall(paragraph)
    if len(targets) != 1:
        return None, [
            (
                f"LinkTargetMismatch: README's last paragraph holds {len(targets)} "
                f"links, expected 1: {paragraph!r}"
            )
        ]
    return targets[0], []


def resolve_inside(root: Path, target: str) -> tuple[Path | None, list[str]]:
    """Resolve a link ``target`` against ``root``, refusing anything outside the root.

    Args:
        root: the repository root the link is relative to.
        target: the link target taken from README text.

    Returns:
        The resolved path and an empty list when the target names a regular file inside
        ``root``; otherwise None and an UnresolvedLink finding.
    """
    resolved_root = root.resolve()
    candidate = (resolved_root / target).resolve()
    if not candidate.is_relative_to(resolved_root):
        return None, [
            f"UnresolvedLink: target {target!r} escapes the repository root: {candidate}"
        ]
    if not candidate.is_file():
        return None, [f"UnresolvedLink: target {target!r} is not a file: {candidate}"]
    return candidate, []


def checklist_findings(text: str, target: str) -> list[str]:
    """Report UnresolvedLink unless ``text`` holds the checklist's title and five items.

    Args:
        text: the linked file's text.
        target: the link target, quoted in findings.
    """
    lines = text.splitlines()
    first = lines[0] if lines else ""
    findings = []
    if not first.startswith("# ") or not first[2:].strip():
        findings.append(
            f"UnresolvedLink: {target!r} does not open with a level-1 title: {first!r}"
        )
    numbers = [int(match.group(1)) for match in map(_ITEM_START.match, lines) if match]
    if numbers != ITEM_NUMBERS:
        findings.append(
            f"UnresolvedLink: {target!r} does not hold the checklist; its items are "
            f"numbered {numbers}, expected {ITEM_NUMBERS}"
        )
    return findings


def reachable_findings(root: Path, readme_text: str) -> list[str]:
    """Follow the README's last link from ``root`` and report every problem on the way.

    Args:
        root: the repository root the link is relative to.
        readme_text: the full README text.

    Returns:
        An empty list when the link reaches a file inside ``root`` holding the
        checklist; otherwise the findings that stopped it.
    """
    target, findings = pointer_target(readme_text)
    if target is None:
        return findings
    path, findings = resolve_inside(root, target)
    if path is None:
        return findings
    return checklist_findings(path.read_text(encoding="utf-8"), target)


def _real_readme_text() -> str:
    """Read the repository's ``README.md``, failing with MissingDocument if absent."""
    readme = REPO_ROOT / README_NAME
    assert readme.is_file(), f"MissingDocument: no file at {readme}"
    return readme.read_text(encoding="utf-8")


def _checklist_text(item_count: int) -> str:
    """Build a small checklist sample holding ``item_count`` numbered items.

    Args:
        item_count: how many items, numbered from 1, the sample holds.
    """
    items = [
        f"{number}. Do thing {number}.\n\n   Example: {number}\n"
        for number in range(1, item_count + 1)
    ]
    return "# Checklist\n\nOne sentence about any tool.\n\n" + "\n".join(items)


def _readme_text(target: str) -> str:
    """Build a README sample whose last paragraph links to ``target``.

    Args:
        target: the link target the sample's last sentence carries.
    """
    return f"# Sample\n\nA purpose statement.\n\nRead the [checklist]({target}).\n"


def test_readme_link_reaches_the_checklist() -> None:
    """The README's last link reaches a root file holding the title and five items."""
    findings = reachable_findings(REPO_ROOT, _real_readme_text())

    assert findings == [], "\n".join(findings)


def test_readme_link_resolves_to_the_root_contributing_file() -> None:
    """The file the README's last link resolves to is the root ``CONTRIBUTING.md``."""
    target, target_findings = pointer_target(_real_readme_text())
    assert target is not None, "\n".join(target_findings)

    path, path_findings = resolve_inside(REPO_ROOT, target)

    assert path == (REPO_ROOT / CONTRIBUTING_NAME).resolve(), (
        f"UnresolvedLink: {target!r} resolves to {path}, expected the root "
        f"{CONTRIBUTING_NAME}; {path_findings}"
    )


def test_linked_file_holds_the_checklist() -> None:
    """The root ``CONTRIBUTING.md`` opens with a title and holds items 1 to 5."""
    contributing = REPO_ROOT / CONTRIBUTING_NAME
    assert contributing.is_file(), f"MissingDocument: no file at {contributing}"

    findings = checklist_findings(
        contributing.read_text(encoding="utf-8"), CONTRIBUTING_NAME
    )

    assert findings == [], "\n".join(findings)


def test_missing_target_reports_unresolved_link(tmp_path: Path) -> None:
    """A README linking to a file absent from the root reports UnresolvedLink."""
    findings = reachable_findings(tmp_path, _readme_text(CONTRIBUTING_NAME))

    assert len(findings) == 1
    assert findings[0].startswith(
        f"UnresolvedLink: target {CONTRIBUTING_NAME!r} is not"
    )


def test_target_outside_the_root_reports_unresolved_link(tmp_path: Path) -> None:
    """A target that escapes the root is refused even when the outside file exists."""
    root = tmp_path / "repository"
    root.mkdir()
    (tmp_path / CONTRIBUTING_NAME).write_text(_checklist_text(5), encoding="utf-8")

    findings = reachable_findings(root, _readme_text(f"../{CONTRIBUTING_NAME}"))

    assert len(findings) == 1
    assert "escapes the repository root" in findings[0]
    assert findings[0].startswith("UnresolvedLink:")


def test_target_with_four_items_reports_unresolved_link(tmp_path: Path) -> None:
    """A linked file holding four items does not count as the checklist."""
    (tmp_path / CONTRIBUTING_NAME).write_text(_checklist_text(4), encoding="utf-8")

    findings = reachable_findings(tmp_path, _readme_text(CONTRIBUTING_NAME))

    assert findings == [
        (
            f"UnresolvedLink: {CONTRIBUTING_NAME!r} does not hold the checklist; its "
            f"items are numbered [1, 2, 3, 4], expected {ITEM_NUMBERS}"
        )
    ]


def test_readme_without_a_link_reports_link_target_mismatch(tmp_path: Path) -> None:
    """A README whose last paragraph holds no link stops at LinkTargetMismatch."""
    readme = "# Sample\n\nRead the checklist in CONTRIBUTING.md.\n"

    findings = reachable_findings(tmp_path, readme)

    assert len(findings) == 1
    assert findings[0].startswith("LinkTargetMismatch:")
