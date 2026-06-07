"""核心 Pipeline：小说→剧本三阶段转换流水线。

Stage 1 → 逐章提取角色、事件、地点
Stage 2 → 全局汇总：合并角色 + 排序事件线
Stage 3 → 剧本生成 + 容错重试
"""

import json
import logging
import re
from openai import OpenAI

from .config import get_llm_config
from .models import (
    ChapterExtraction,
    ExtractedEvent,
    Character,
    MergedData,
    MergedCharacter,
    MergedEvent,
    Script,
    FaithfulnessReport,
)
from .prompts import (
    SYSTEM_EXTRACTOR,
    SYSTEM_MERGER,
    SYSTEM_GENERATOR,
    EXTRACTION_USER_TEMPLATE,
    MERGER_USER_TEMPLATE,
    GENERATION_USER_TEMPLATE,
    CORRECTION_USER_TEMPLATE,
)
from .yaml_utils import extract_yaml_from_text, parse_script_yaml, script_to_yaml
from .faithfulness import hard_rule_check

logger = logging.getLogger(__name__)

MAX_RETRIES = 2

# ─── JSON 提取工具 ──────────────────────────────────────────────


def _extract_json(content: str) -> dict:
    """从 LLM 输出中提取 JSON 对象。

    处理 markdown 代码块包裹、纯文本等多层容错。
    """
    content = content.strip()

    # ```json ... ```
    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        content = match.group(1).strip()

    # ``` ... ```
    match = re.search(r"```\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        content = match.group(1).strip()

    # 找第一个 { 和最后一个 }
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        content = content[start : end + 1]

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON, returning empty dict")
        return {}


# ─── Pipeline 主类 ──────────────────────────────────────────────


class NovelToScriptPipeline:
    """小说转剧本三阶段流水线。

    用法:
        pipeline = NovelToScriptPipeline()
        script, report = pipeline.run(chapters, title, author, genre)
    """

    def __init__(self):
        config = get_llm_config()
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    # ── 主入口 ──────────────────────────────────────────────────

    def run(
        self,
        chapters: list[str],
        title: str = "未命名剧本",
        author: str = "未知",
        genre: str = "剧情",
    ) -> tuple[Script, FaithfulnessReport]:
        """执行完整的三阶段转换流水线。

        Args:
            chapters: 章节文本列表（至少 3 章）
            title: 剧本标题
            author: 原作者
            genre: 剧本类型

        Returns:
            (Script 对象, FaithfulnessReport 对象)
        """
        logger.info(f"Pipeline start: {len(chapters)} chapters → script")

        # Stage 1: 逐章提取
        extractions = self._stage1_extract(chapters)
        logger.info(f"Stage 1: {len(extractions)} chapters extracted")

        # Stage 2: 全局汇总
        merged = self._stage2_merge(extractions)
        logger.info(
            f"Stage 2: {len(merged.characters)} chars, "
            f"{len(merged.linear_events)} events"
        )

        # Stage 3: 剧本生成（含容错重试）
        script = self._stage3_generate(merged, title, author, genre)
        logger.info(f"Stage 3: {len(script.scenes)} scenes generated")

        # 硬规则忠实度检查
        report = hard_rule_check(script)
        logger.info(f"Hard check: overall_score={report.overall_score}")

        return script, report

    # ── Stage 1: 逐章提取 ────────────────────────────────────────

    def _stage1_extract(self, chapters: list[str]) -> list[ChapterExtraction]:
        """对每一章独立调用 LLM，提取结构化信息。

        每章独立处理，天然可并行（当前顺序执行，后续可优化）。
        """
        extractions: list[ChapterExtraction] = []

        for i, chapter_text in enumerate(chapters, 1):
            # 长章节截断，保留前 6000 字符（DeepSeek 64K 足够，但控制成本）
            text = chapter_text
            if len(text) > 6000:
                text = text[:6000]
                logger.info(f"Chapter {i}: truncated {len(chapter_text)} → {len(text)} chars")

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": SYSTEM_EXTRACTOR},
                    {
                        "role": "user",
                        "content": EXTRACTION_USER_TEMPLATE.format(
                            chapter_num=i,
                            chapter_text=text,
                        ),
                    },
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            content = response.choices[0].message.content or "{}"
            data = _extract_json(content)

            chars_raw = data.get("characters", [])
            for c in chars_raw:
                if "id" not in c:
                    c["id"] = c.get("name", f"char_{i}")
            chars = [Character(**c) for c in chars_raw]
            events = [ExtractedEvent(**e) for e in data.get("key_events", [])]
            locations = data.get("setting_locations", [])

            extractions.append(
                ChapterExtraction(
                    chapter_index=i,
                    characters=chars,
                    key_events=events,
                    setting_locations=locations,
                )
            )

        return extractions

    # ── Stage 2: 全局汇总 ────────────────────────────────────────

    def _stage2_merge(self, extractions: list[ChapterExtraction]) -> MergedData:
        """将各章提取结果发给 LLM，合并去重、计算重要性、排序事件线。"""
        extractions_json = json.dumps(
            [e.model_dump(exclude_none=True, mode="python") for e in extractions],
            ensure_ascii=False,
            indent=2,
        )

        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": SYSTEM_MERGER},
                {
                    "role": "user",
                    "content": MERGER_USER_TEMPLATE.format(
                        chapter_count=len(extractions),
                        chapter_extractions=extractions_json,
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=self.config.max_tokens,
        )

        content = response.choices[0].message.content or "{}"
        data = _extract_json(content)

        chars = [MergedCharacter(**c) for c in data.get("characters", [])]
        events = [MergedEvent(**e) for e in data.get("linear_events", [])]
        locations = data.get("locations", [])

        return MergedData(characters=chars, linear_events=events, locations=locations)

    # ── Stage 3: 剧本生成（含容错重试）──────────────────────────

    def _stage3_generate(
        self, merged: MergedData, title: str, author: str, genre: str
    ) -> Script:
        """基于汇总数据生成剧本 YAML，失败时自动重试。

        重试策略：将上次的解析错误注入 Prompt，让 LLM 自我修正。
        """
        characters_json = json.dumps(
            [c.model_dump(exclude_none=True, mode="python") for c in merged.characters],
            ensure_ascii=False,
            indent=2,
        )
        events_json = json.dumps(
            [e.model_dump(exclude_none=True, mode="python") for e in merged.linear_events],
            ensure_ascii=False,
            indent=2,
        )
        locations_str = (
            ", ".join(merged.locations) if merged.locations else "由AI根据事件推断"
        )

        last_error = ""
        messages = [
            {"role": "system", "content": SYSTEM_GENERATOR},
            {
                "role": "user",
                "content": GENERATION_USER_TEMPLATE.format(
                    title=title,
                    author=author,
                    genre=genre,
                    characters_json=characters_json,
                    events_json=events_json,
                    locations=locations_str,
                ),
            },
        ]

        for attempt in range(MAX_RETRIES + 1):
            if last_error:
                # 追加修正请求
                messages.append({
                    "role": "user",
                    "content": CORRECTION_USER_TEMPLATE.format(
                        error_message=last_error
                    ),
                })

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            raw = response.choices[0].message.content or ""
            yaml_text = extract_yaml_from_text(raw)

            try:
                script = parse_script_yaml(yaml_text)
                logger.info(f"Script parsed OK (attempt {attempt + 1})")
                return script
            except Exception as e:
                last_error = f"{type(e).__name__}: {str(e)}"
                logger.warning(f"Script parse failed (attempt {attempt + 1}): {last_error}")

        raise RuntimeError(
            f"剧本生成失败：{MAX_RETRIES + 1} 次尝试后仍无法解析 YAML。"
            f"最后一次错误：{last_error}"
        )

    # ── 忠实度 LLM 软检查（可选增强）─────────────────────────────

    def full_faithfulness_check(
        self, original_chapters: list[str], script: Script
    ) -> FaithfulnessReport:
        """执行完整忠实度检查（硬规则 + LLM 软检查）。

        Args:
            original_chapters: 原始章节文本
            script: 生成的剧本

        Returns:
            FaithfulnessReport
        """
        from .faithfulness import (
            llm_faithfulness_check,
            generate_faithfulness_summary,
        )

        summary = generate_faithfulness_summary(original_chapters)
        return llm_faithfulness_check(summary, script, self.client)
