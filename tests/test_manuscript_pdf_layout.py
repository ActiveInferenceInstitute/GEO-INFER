"""Layout tests that read the shipped PDF instead of the settings behind it.

The float-placement defect — a page carrying one figure, its caption, and the
folio, against 1,800-2,000 characters on an ordinary page — was previously
covered by asserting that four ``\\renewcommand`` lines were present in
``manuscript/preamble.md``.  That assertion passed while the defect was still
visible in the PDF: the parameters were relaxed enough for two of the three
figures and the third still cleared ``\\floatpagefraction``.  These tests read
the artifact.

The PDF is a build product under the ignored ``output/`` tree, so the suite
skips when it has not been rendered.  Nothing here is a substitute for the
generator-side bound in ``_assert_leaves_room_for_text``; that one fails
before a figure is written, this one fails after a render that shipped one
anyway.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

import pytest

PDF = Path("output/pdf/GEO-INFER_combined.pdf")
# A float page carries its figure's caption and the folio and nothing else; the
# page this test was written for held one word besides the caption.  A page
# that carries a figure and at least a line of body text besides is a text page
# with a figure on it, which is what the float parameters exist to produce.
# Measured on this manuscript: the float page held 1, the sparsest legitimate
# figure page holds 32 (a figure plus a short closing subsection), and an
# ordinary text page holds 250-350.  The floor sits in that gap.
MINIMUM_NON_CAPTION_WORDS = 15


def _words(text: str) -> list[str]:
    """Normalised word list: ligatures folded, punctuation and folios dropped."""
    folded = unicodedata.normalize("NFKD", text).casefold()
    return [
        word
        for word in re.findall(r"[a-z0-9]+", folded)
        if not word.isdigit()
    ]


def _remaining(page_words: list[str], caption_words: list[str]) -> list[str]:
    """The page's words with one occurrence of each caption word removed."""
    budget = Counter(caption_words)
    kept: list[str] = []
    for word in page_words:
        if budget[word]:
            budget[word] -= 1
            continue
        kept.append(word)
    return kept


def _tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        pytest.skip(f"{name} is not installed")
    return path


@pytest.fixture(scope="module")
def rendered_pdf(repo_root: Path) -> Path:
    pdf = repo_root / PDF
    if not pdf.is_file():
        pytest.skip(f"{PDF.as_posix()} has not been rendered")
    return pdf


def _page_text(pdf: Path, page: int) -> str:
    completed = subprocess.run(
        [_tool("pdftotext"), "-f", str(page), "-l", str(page), str(pdf), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout


def _figure_pages(pdf: Path) -> set[int]:
    completed = subprocess.run(
        [_tool("pdfimages"), "-list", str(pdf)],
        capture_output=True,
        text=True,
        check=True,
    )
    pages: set[int] = set()
    for line in completed.stdout.splitlines()[2:]:
        fields = line.split()
        if fields and fields[0].isdigit():
            pages.add(int(fields[0]))
    return pages


class TestFloatPlacement:
    def test_no_figure_takes_a_page_to_itself(
        self, repo_root: Path, rendered_pdf: Path
    ) -> None:
        registry = json.loads(
            (repo_root / "output" / "figures" / "figure_registry.json").read_text(
                encoding="utf-8"
            )
        )
        captions = [_words(entry["caption"]) for entry in registry["figures"]]
        pages = _figure_pages(rendered_pdf)
        assert pages, "the rendered PDF embeds no figures"
        for page in sorted(pages):
            words = _words(_page_text(rendered_pdf, page))
            # Which caption is on the page is decided by overlap rather than by
            # order, so a moved figure does not silently pass the test.  The
            # count that matters is what is left after the best-matching
            # caption's words are removed once each.
            best = min(captions, key=lambda caption: len(_remaining(words, caption)))
            remaining = _remaining(words, best)
            assert len(remaining) >= MINIMUM_NON_CAPTION_WORDS, (
                f"page {page} carries a figure, its caption, and "
                f"{len(remaining)} other words ({remaining}): it is a float page"
            )


class TestTextBlock:
    def test_no_word_is_set_past_the_right_margin(self, rendered_pdf: Path) -> None:
        # The text block's right edge, read from the render log: \oddsidemargin
        # 19.875pt + 1in + \textwidth 430.005pt.  A word box beyond it is text
        # in the margin — an unbreakable verbatim line or an unbreakable
        # monospace span in a narrow column.  One point of tolerance covers
        # glyph bounding boxes that overhang their advance width.
        right_edge = 19.875 + 72.0 + 430.005 + 1.0
        completed = subprocess.run(
            [_tool("pdftotext"), "-bbox", str(rendered_pdf), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
        page = 0
        offenders: list[str] = []
        for line in completed.stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("<page"):
                page += 1
            elif 'xMax="' in stripped:
                value = float(stripped.split('xMax="')[1].split('"')[0])
                if value > right_edge:
                    offenders.append(f"page {page}: {stripped} at {value:.1f}pt")
        assert not offenders, "\n".join(offenders)
