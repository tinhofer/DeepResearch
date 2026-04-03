"""
Obsidian-compatible markdown export for Deep Research reports.

Converts standard markdown reports into Obsidian-friendly format with:
- YAML frontmatter (tags, date, sources)
- Wikilink-style source references
- Mobile-friendly formatting
"""

import re
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def convert_to_obsidian(report_content: str, task: str, history_infos: list, save_dir: str) -> tuple[str, str]:
    """
    Convert a Deep Research report to Obsidian-compatible markdown.

    Args:
        report_content: The raw markdown report content.
        task: The original research task/query.
        history_infos: List of recorded info dicts with url, title, summary_content.
        save_dir: Directory to save the Obsidian-formatted file.

    Returns:
        Tuple of (obsidian_content, file_path).
    """
    sources = _extract_sources(report_content, history_infos)
    tags = _generate_tags(task)
    title = _extract_title(report_content)

    frontmatter = _build_frontmatter(title, task, tags, sources)
    body = _convert_citations_to_wikilinks(report_content, sources)

    obsidian_content = frontmatter + "\n" + body

    file_path = os.path.join(save_dir, "obsidian_report.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(obsidian_content)

    # Also generate individual source notes
    _generate_source_notes(sources, save_dir)

    logger.info(f"Obsidian report saved at: {file_path}")
    return obsidian_content, file_path


def _extract_title(report_content: str) -> str:
    """Extract the first H1 title from the report."""
    match = re.search(r"^#\s+(.+)$", report_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: first non-empty line
    for line in report_content.split("\n"):
        line = line.strip()
        if line:
            return line[:80]
    return "Deep Research Report"


def _extract_sources(report_content: str, history_infos: list) -> list[dict]:
    """
    Extract sources from the reference list at the end of the report,
    enriched with data from history_infos.
    """
    sources = []
    seen_urls = set()

    # Parse references like [1] Title (URL)
    ref_pattern = re.compile(r"\[(\d+)\]\s*(.+?)(?:\s*\(([^)]+)\))?\s*$", re.MULTILINE)
    for match in ref_pattern.finditer(report_content):
        num = int(match.group(1))
        title = match.group(2).strip()
        url = match.group(3).strip() if match.group(3) else ""

        source = {"num": num, "title": title, "url": url}
        sources.append(source)
        if url:
            seen_urls.add(url)

    # If no references found in the report, fall back to history_infos
    if not sources and history_infos:
        for i, info in enumerate(history_infos):
            url = info.get("url", "unknown")
            if url in seen_urls or url == "unknown":
                continue
            seen_urls.add(url)
            sources.append({
                "num": i + 1,
                "title": info.get("title", "Unknown Source"),
                "url": url,
            })

    return sources


def _generate_tags(task: str) -> list[str]:
    """Generate Obsidian tags from the research task."""
    tags = ["deep-research"]

    # Extract key terms (simple keyword extraction)
    stop_words = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "shall", "can", "about", "into",
        "through", "during", "before", "after", "above", "below", "between",
        "out", "off", "over", "under", "again", "further", "then", "once",
        "that", "this", "these", "those", "it", "its", "how", "what", "which",
        "who", "whom", "where", "when", "why", "all", "each", "every", "both",
        "few", "more", "most", "other", "some", "such", "no", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "because", "as",
        "until", "while", "compose", "report", "write", "create", "provide",
        "include", "encompassing", "substantiated", "examples", "relevant",
        "reflect", "original", "insights", "analysis", "moving", "beyond",
        "mere", "summarization", "existing", "literature", "use", "using",
    }

    words = re.findall(r"[a-zA-Z]+", task.lower())
    seen = set()
    for word in words:
        if word not in stop_words and len(word) > 2 and word not in seen:
            seen.add(word)
            tags.append(word)
        if len(tags) >= 8:  # Cap at 8 tags
            break

    return tags


def _build_frontmatter(title: str, task: str, tags: list[str], sources: list[dict]) -> str:
    """Build YAML frontmatter for Obsidian."""
    date_str = datetime.now().strftime("%Y-%m-%d")

    lines = [
        "---",
        f"title: \"{title}\"",
        f"date: {date_str}",
        f"type: research",
        f"tags:",
    ]
    for tag in tags:
        lines.append(f"  - {tag}")

    if sources:
        lines.append("sources:")
        for src in sources[:20]:  # Limit to 20 sources in frontmatter
            safe_title = src['title'].replace('"', '\\"')
            if src['url']:
                lines.append(f"  - title: \"{safe_title}\"")
                lines.append(f"    url: \"{src['url']}\"")
            else:
                lines.append(f"  - title: \"{safe_title}\"")

    lines.append("---")
    return "\n".join(lines) + "\n"


def _convert_citations_to_wikilinks(report_content: str, sources: list[dict]) -> str:
    """
    Convert bracketed citations [1] to Obsidian-style linked references.

    Inline citations become linked: [1] -> [[Source - Title|[1]]]
    The reference list at the end gets Obsidian external link formatting.
    """
    content = report_content

    # Build a map of citation number -> source
    source_map = {src["num"]: src for src in sources}

    # Convert inline citations [N] to Obsidian links
    def replace_citation(match):
        num = int(match.group(1))
        src = source_map.get(num)
        if src and src.get("url"):
            # Use Obsidian external link format for mobile-friendly tapping
            return f"[\\[{num}\\]]({src['url']})"
        return match.group(0)

    content = re.sub(r"\[(\d+)\]", replace_citation, content)

    # Replace the reference section with Obsidian-formatted links
    # Find the references section (usually at the end)
    ref_section_pattern = re.compile(
        r"(^#{1,3}\s*(?:References?|Sources?|Bibliography)\s*$)(.*)",
        re.MULTILINE | re.DOTALL
    )
    ref_match = ref_section_pattern.search(content)
    if ref_match:
        ref_header = ref_match.group(1)
        ref_body = ref_match.group(2)
        new_refs = [ref_header, ""]
        for src in sources:
            if src.get("url"):
                new_refs.append(f"- \\[{src['num']}\\] [{src['title']}]({src['url']})")
            else:
                new_refs.append(f"- \\[{src['num']}\\] {src['title']}")
            new_refs.append("")
        content = content[:ref_match.start()] + "\n".join(new_refs)

    return content


def _generate_source_notes(sources: list[dict], save_dir: str):
    """
    Generate individual Obsidian source note files in a 'sources' subfolder.
    These can be linked from the main report using wikilinks.
    """
    if not sources:
        return

    sources_dir = os.path.join(save_dir, "sources")
    os.makedirs(sources_dir, exist_ok=True)

    for src in sources:
        # Sanitize title for filename
        safe_name = re.sub(r'[<>:"/\\|?*]', '', src['title'])[:80].strip()
        if not safe_name:
            safe_name = f"Source {src['num']}"

        note_content = f"""---
title: "{src['title']}"
type: source
url: "{src.get('url', '')}"
---

# {src['title']}

"""
        if src.get("url"):
            note_content += f"**URL:** {src['url']}\n\n"

        note_content += f"Referenced in [[obsidian_report|Deep Research Report]]\n"

        note_path = os.path.join(sources_dir, f"{safe_name}.md")
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)

    logger.info(f"Generated {len(sources)} source notes in {sources_dir}")
