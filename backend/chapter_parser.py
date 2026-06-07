"""章节解析器：从长文本中自动识别和切分章节。

支持：
- 中文章节标题：第X章、第X节、第一章、第一节
- 英文章节标题：Chapter X、Part X、CHAPTER X
- 数字分隔：1.、1、一、
- 无标题回退：整段视为单章
"""

import re
from typing import Optional


# ─── 章节标题模式 ──────────────────────────────────────────────

# 中文 "第X章" "第一章" "第1章" 等
_CN_CHAPTER = re.compile(
    r"(?:^|\n)\s*[第]?\s*([零一二三四五六七八九十百千\d]+)\s*[章节回]",
    re.MULTILINE,
)

# 英文 "Chapter X" "CHAPTER 1" "Part One" 等
_EN_CHAPTER = re.compile(
    r"(?:^|\n)\s*(?:Chapter|CHAPTER|Part|PART)\s+([IVXLCDM\d]+|[Oo]ne|[Tt]wo|[Tt]hree|[Ff]our|[Ff]ive)",
    re.MULTILINE,
)

# 纯数字标题 "1." "2." "1、" "2、" 等（作为备选）
_NUM_HEADING = re.compile(
    r"(?:^|\n)\s*(\d{1,3})\s*[\.\、\s](?![\d\w])",
    re.MULTILINE,
)


def has_chapter_headings(text: str) -> bool:
    """检测文本是否包含明确的章节标题。

    Args:
        text: 原始小说文本

    Returns:
        True 如果检测到章节标题
    """
    if _CN_CHAPTER.search(text):
        return True
    if _EN_CHAPTER.search(text):
        return True
    return False


def parse_chapters(text: str) -> list[dict]:
    """将长文本按章节标题切分为章节列表。

    优先使用中文/英文章节标题匹配，无匹配时回退为单章。

    Args:
        text: 原始小说文本（可能包含多个章节）

    Returns:
        章节列表，每项为 {"title": str, "content": str}
    """
    if not text or not text.strip():
        return []

    text = text.strip()

    # 选择最佳匹配模式
    matches = list(_CN_CHAPTER.finditer(text))

    if not matches:
        matches = list(_EN_CHAPTER.finditer(text))

    if not matches:
        matches = list(_NUM_HEADING.finditer(text))

    if not matches:
        return [{"title": "全文", "content": text}]

    chapters = []
    for i, match in enumerate(matches):
        # match.start() 是标题起始位（可能含前导 \n）
        raw_start = match.start()
        # 跳到标题所在行的开头
        if text[raw_start] == "\n":
            content_start = raw_start + 1  # 跳过前导换行
        else:
            content_start = raw_start

        if i + 1 < len(matches):
            next_raw = matches[i + 1].start()
            if text[next_raw] == "\n":
                content_end = next_raw
            else:
                # 找下一个标题前的换行
                prev_nl = text.rfind("\n", 0, next_raw)
                content_end = prev_nl if prev_nl != -1 else next_raw
        else:
            content_end = len(text)

        chunk = text[content_start:content_end].strip()
        if not chunk:
            continue

        # 提取标题行
        nl = chunk.find("\n")
        if nl != -1:
            title = chunk[:nl].strip()
        else:
            title = chunk.strip()

        chapters.append({"title": title, "content": chunk})

    # 匹配前的前言 → 序章
    if matches and matches[0].start() > 0:
        preface = text[:matches[0].start()].strip()
        if preface and len(preface) > 20:
            chapters.insert(0, {"title": "序章/前言", "content": preface})

    return chapters if chapters else [{"title": "全文", "content": text}]


def parse_chapters_simple(text: str) -> list[str]:
    """章节解析的简化接口，只返回纯文本列表。

    Args:
        text: 原始小说文本

    Returns:
        章节纯文本列表（标题行保留在内容中）
    """
    result = parse_chapters(text)
    return [c["content"] for c in result]
