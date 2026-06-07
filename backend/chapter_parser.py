"""章节标题自动识别。

支持中文（「第X章」）和英文（「Chapter X」）章节标题切分。
"""

import re

# ── 正则模式 ───────────────────────────────────────────────────────

# 中文章节标题: 第1章 / 第一章 / 第 一 章
_CN_PATTERN = re.compile(
    r"第\s*[\d一二三四五六七八九十百千万]+\s*[章节回卷篇]",
)

# 英文章节标题: Chapter 1 / CHAPTER I / Chapter One
_EN_PATTERN = re.compile(
    r"Chapter\s+\d+",
    re.IGNORECASE,
)


# ── 公开接口 ───────────────────────────────────────────────────────


def has_chapter_headings(text: str) -> bool:
    """检测文本是否包含章节标题。"""
    return bool(_CN_PATTERN.search(text) or _EN_PATTERN.search(text))


def parse_chapters_simple(text: str) -> list[str]:
    """根据章节标题切分文本，返回章节列表。

    Args:
        text: 整本小说文本

    Returns:
        章节文本列表（含标题）。每章开头保留原标题。
        如未识别到章节标题，整段文本视为单章。
    """
    # 收集所有中文章节标题的 span
    all_spans = []
    for m in _CN_PATTERN.finditer(text):
        all_spans.append((m.start(), m.end(), "cn"))

    # 收集所有英文章节标题的 span
    for m in _EN_PATTERN.finditer(text):
        all_spans.append((m.start(), m.end(), "en"))

    # 无章节标题 → 单章
    if not all_spans:
        return [text.strip()]

    # 按位置排序
    all_spans.sort(key=lambda x: x[0])

    chapters = []
    for i, (start, end, _kind) in enumerate(all_spans):
        next_start = all_spans[i + 1][0] if i + 1 < len(all_spans) else len(text)
        chapter_text = text[start:next_start].strip()
        if chapter_text:
            chapters.append(chapter_text)

    # 标题之前的文本作为前言（可选，若较短则拼入第一章）
    if all_spans and all_spans[0][0] > 0:
        preamble = text[: all_spans[0][0]].strip()
        if preamble:
            if len(chapters) > 0 and len(preamble) < len(chapters[0]):
                chapters[0] = preamble + "\n\n" + chapters[0]
            else:
                chapters.insert(0, preamble)

    return chapters
