#!/usr/bin/env python3
"""Validate the homepage content before publishing.

No third-party dependencies: this must run on a stock macOS Python.
Exit code 0 = ok (warnings allowed), 1 = blocking problem.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ABOUT = ROOT / "_pages" / "about.md"
CONFIG = ROOT / "_config.yml"
NAV = ROOT / "_data" / "navigation.yml"

REQUIRED_HEADINGS = {
    "About me": r"^# 👦 About me\s*$",
    "Research Interests": r"^# 🔎 Research Interests\s*$",
    "Publications": r"^# 📝 Publications\s*$",
    "Honors and Awards": r"^# 🎖 Honors and Awards\s*$",
    "Educations": r"^# 📖 Educations\s*$",
}
NEWS_HEADING = r"^# 📰 News\s*$"

errors: list[str] = []
warnings: list[str] = []


def section_bounds(text: str, heading_pattern: str) -> tuple[int, int] | None:
    """Return (start, end) offsets of a level-1 section."""
    match = re.search(heading_pattern, text, flags=re.MULTILINE)
    if not match:
        return None
    start = match.start()
    next_heading = re.search(r"^# ", text[match.end():], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(text)
    return start, end


def main() -> int:
    if not ABOUT.exists():
        print(f"ERROR: missing {ABOUT}", file=sys.stderr)
        return 1

    text = ABOUT.read_text(encoding="utf-8")

    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.DOTALL)
    if not front:
        errors.append("_pages/about.md: missing or malformed YAML front matter")
    elif "permalink: /" not in front.group(1):
        warnings.append("_pages/about.md: front matter does not set `permalink: /`")

    positions: dict[str, int] = {}
    for name, pattern in REQUIRED_HEADINGS.items():
        match = re.search(pattern, text, flags=re.MULTILINE)
        if not match:
            errors.append(f"_pages/about.md: missing section `{name}`")
        else:
            positions[name] = match.start()

    news = section_bounds(text, NEWS_HEADING)
    if news:
        news_text = text[news[0]:news[1]]
        if not re.search(r"""id\s*=\s*['"]-news['"]""", news_text):
            errors.append("News section is missing the anchor `id='-news'`")
        if "Publications" in positions and not (
            positions.get("Research Interests", -1) < news[0] < positions["Publications"]
        ):
            warnings.append("News section is not between Research Interests and Publications")
    else:
        if NAV.exists() and "News" in NAV.read_text(encoding="utf-8"):
            warnings.append("navigation.yml links to News, but the News section does not exist yet")

    ordered = [positions[name] for name in
               ("About me", "Research Interests", "Publications", "Honors and Awards", "Educations")
               if name in positions]
    if ordered != sorted(ordered):
        errors.append("_pages/about.md: top-level sections are out of order")

    if re.search(r"^(<<<<<<<|=======|>>>>>>>)", text, flags=re.MULTILINE):
        errors.append("_pages/about.md: merge conflict markers found")

    pub_start = positions.get("Publications")
    honors_start = positions.get("Honors and Awards")
    pub_block = text[pub_start:honors_start] if pub_start is not None and honors_start else ""
    pub_lines = [line.strip() for line in pub_block.splitlines()
                 if line.lstrip().startswith('- <span style="color:')]
    seen: dict[str, int] = {}
    for line in pub_lines:
        key = re.sub(r"\s+", " ", line)
        seen[key] = seen.get(key, 0) + 1
    for line, count in seen.items():
        if count > 1:
            errors.append(f"duplicate publication entry ({count}x): {line[:100]}")

    titles = re.findall(r':\s*"([^"]{8,})"\s*:', pub_block)
    title_counts: dict[str, int] = {}
    for title in titles:
        key = re.sub(r"\W+", " ", title.lower()).strip()
        title_counts[key] = title_counts.get(key, 0) + 1
    for _key, count in title_counts.items():
        if count > 1:
            warnings.append(f"possible duplicate publication title ({count}x)")

    empty_links = text.count("]()")
    if empty_links:
        warnings.append(f"{empty_links} empty Markdown link target(s), e.g. `[Paper]()`")

    if "{{" in text or "{%" in text:
        pass  # Liquid is expected and rendered by GitHub Pages.

    for path, label in ((CONFIG, "_config.yml"),):
        if not path.exists():
            warnings.append(f"{label}: file not found")
            continue
        cfg = path.read_text(encoding="utf-8")
        if not re.search(r"^title\s*:", cfg, flags=re.MULTILINE):
            warnings.append(f"{label}: missing `title`")
        if not re.search(r"^author\s*:", cfg, flags=re.MULTILINE):
            warnings.append(f"{label}: missing `author`")

    print(f"OK: {ABOUT.relative_to(ROOT)}")
    print(f"  sections: {', '.join(positions) if positions else 'none'}")
    print(f"  publications: {len(pub_lines)}")
    print(f"  news: {'yes' if news else 'not yet'}")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
