"""忠实度检查模块：硬规则校验 + LLM 软检查。

借鉴 R² 的 HAR（幻觉感知修正）思想：
- 硬规则（代码）：100%可靠的结构性检查
- 软检查（LLM）：内容级别的忠实度评估
"""

import json
import re
from openai import OpenAI

from .config import get_llm_config
from .models import Script, FaithfulnessReport
from .prompts import SYSTEM_VALIDATOR, FAITHFULNESS_USER_TEMPLATE
from .yaml_utils import validate_script_hard_rules, script_to_yaml


def hard_rule_check(script: Script) -> FaithfulnessReport:
    """执行硬规则校验（不涉及LLM）。

    Args:
        script: 剧本对象

    Returns:
        FaithfulnessReport（仅包含 hard_rule_violations）
    """
    violations = validate_script_hard_rules(script)
    return FaithfulnessReport(
        overall_score=1.0 if not violations else 0.7,
        hard_rule_violations=violations,
    )


def llm_faithfulness_check(
    original_summary: str,
    script: Script,
    client: OpenAI,
) -> FaithfulnessReport:
    """调用LLM检查剧本忠实度。

    Args:
        original_summary: 原著情节摘要（用于对比）
        script: 生成的剧本
        client: OpenAI 客户端

    Returns:
        FaithfulnessReport 综合报告
    """
    # 1. 先做硬规则检查
    hard_violations = validate_script_hard_rules(script)

    # 2. LLM 软检查 — 摘要附加结构统计
    summary_with_stats = original_summary
    if script:
        summary_with_stats += (
            f"\n\n剧本结构统计：{script.chapter_count}章, "
            f"{script.scene_count}个场景, {script.beat_count}个分镜, "
            f"{len(script.characters)}个角色"
        )

    config = get_llm_config()
    script_yaml = script_to_yaml(script)

    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": SYSTEM_VALIDATOR},
                {
                    "role": "user",
                    "content": FAITHFULNESS_USER_TEMPLATE.format(
                        original_summary=summary_with_stats,
                        script_yaml=script_yaml,
                    ),
                },
            ],
            temperature=0.2,
            max_tokens=1024,
        )

        content = response.choices[0].message.content or "{}"
        content = _extract_json(content)

        data = json.loads(content)
        report = FaithfulnessReport(**data)

    except (json.JSONDecodeError, Exception) as e:
        # LLM 输出不稳定时降级为仅硬规则检查
        report = FaithfulnessReport(
            overall_score=0.5,
            suggestions=[f"LLM检查失败，仅完成硬规则校验: {str(e)}"],
        )

    # 3. 合并硬规则违规
    report.hard_rule_violations = hard_violations

    # 如果有硬规则违规，下调评分
    if hard_violations:
        report.overall_score = min(report.overall_score, 0.8)

    return report


def generate_faithfulness_summary(original_chapters: list[str], script: Script | None = None) -> str:
    """为忠实度检查生成原著摘要。

    简单策略：取每章前500字拼接，足够LLM做对比。
    可选包含剧本结构统计。

    Args:
        original_chapters: 原始章节文本列表
        script: 生成的剧本（可选，用于附加结构统计）

    Returns:
        摘要文本
    """
    parts = []
    for i, chapter in enumerate(original_chapters, 1):
        # 取每章的开头和结尾各300字
        head = chapter[:300] if len(chapter) > 300 else chapter
        tail = chapter[-300:] if len(chapter) > 600 else ""
        parts.append(f"第{i}章开头: {head}")
        if tail:
            parts.append(f"第{i}章结尾: {tail}")

    # 附加剧本结构统计
    if script:
        parts.append(
            f"\n剧本结构统计：{script.chapter_count}章, "
            f"{script.scene_count}个场景, {script.beat_count}个分镜, "
            f"{len(script.characters)}个角色"
        )

    return "\n\n".join(parts)


def _extract_json(content: str) -> str:
    """从LLM输出中提取JSON块。"""
    content = content.strip()

    # ```json ... ```
    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # ``` ... ```
    match = re.search(r"```\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 找到第一个 { 和最后一个 }
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
        return content[start:end + 1]

    return content
