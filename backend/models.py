"""数据模型：定义剧本 Schema 和 Pipeline 中间数据结构。"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ─── YAML Schema 模型 ────────────────────────────────────────────


class ScriptMetadata(BaseModel):
    """剧本元信息"""
    title: str = Field(..., description="剧本标题")
    author: str = Field(..., description="原作者")
    adapted_by: Optional[str] = Field(default=None, description="改编者")
    logline: str = Field(..., description="一句话梗概（≤50字）")
    genre: str = Field(..., description="类型：剧情/喜剧/悬疑/科幻/动作/爱情")
    page_count: Optional[int] = Field(default=None, description="预估页数")


class Character(BaseModel):
    """角色"""
    id: str = Field(..., description="角色ID（英文/拼音，如 zhang_san）")
    name: str = Field(..., description="角色名")
    age_range: Optional[str] = Field(default=None, description="年龄区间（如 25-35）")
    description: str = Field(..., description="角色描述")
    importance_score: Optional[float] = Field(default=None, description="重要度评分 0-1")


class Setting(BaseModel):
    """场景设置"""
    location: str = Field(..., description="地点")
    time_of_day: str = Field(..., description="日/夜/黄昏/黎明")


class Action(BaseModel):
    """动作描写"""
    description: str = Field(..., description="动作描述")


class DialogueLine(BaseModel):
    """单句台词"""
    text: str = Field(..., description="台词文本")
    parenthetical: Optional[str] = Field(default=None, description="表演提示")


class Dialogue(BaseModel):
    """对话块"""
    character: str = Field(..., description="说话角色ID")
    lines: list[DialogueLine] = Field(default_factory=list, description="台词行")


class Scene(BaseModel):
    """场景"""
    id: int = Field(..., description="场景序号")
    timeline_type: Optional[str] = Field(
        default="present", description="present / flashback / flashforward"
    )
    slug: str = Field(..., description="标题，如 INT. 咖啡馆 - 日")
    setting: Setting = Field(..., description="场景设置")
    characters_in_scene: list[str] = Field(default_factory=list, description="出场角色ID列表")
    actions: list[Action] = Field(default_factory=list, description="动作描写")
    dialogues: list[Dialogue] = Field(default_factory=list, description="对话")


class Script(BaseModel):
    """完整剧本"""
    version: str = Field(default="1.0", description="Schema版本号")
    metadata: ScriptMetadata = Field(..., description="元信息")
    characters: list[Character] = Field(default_factory=list, description="角色列表")
    scenes: list[Scene] = Field(default_factory=list, description="场景列表")


# ─── Pipeline 中间数据模型 ──────────────────────────────────────


class ExtractedEvent(BaseModel):
    """单章提取的关键事件"""
    summary: str = Field(..., description="事件简述")
    characters_involved: list[str] = Field(default_factory=list, description="涉及角色")
    timeline_hint: Optional[str] = Field(
        default=None, description="时间线提示（倒叙/插叙/正常）"
    )


class ChapterExtraction(BaseModel):
    """Stage 1 输出：单章提取结果"""
    chapter_index: int = Field(..., description="章节序号（从1开始）")
    characters: list[Character] = Field(default_factory=list, description="本章出现的新角色")
    key_events: list[ExtractedEvent] = Field(default_factory=list, description="本章关键事件")
    setting_locations: list[str] = Field(default_factory=list, description="本章涉及的地点")


class MergedCharacter(BaseModel):
    """汇总后的角色（含重要性评分）"""
    id: str = Field(..., description="角色ID")
    name: str = Field(..., description="角色名")
    age_range: Optional[str] = Field(default=None)
    description: str = Field(..., description="角色描述")
    importance_score: float = Field(default=0.5, description="综合重要度 0-1")
    appears_in_chapters: list[int] = Field(default_factory=list, description="出现章节")


class MergedEvent(BaseModel):
    """汇总后的事件（已按时间线排序）"""
    order: int = Field(..., description="排序后的序号")
    summary: str = Field(..., description="事件简述")
    characters_involved: list[str] = Field(default_factory=list)
    timeline_type: str = Field(default="present", description="present/flashback/flashforward")
    source_chapter: int = Field(..., description="来源章节")


class MergedData(BaseModel):
    """Stage 2 输出：全局汇总结果"""
    characters: list[MergedCharacter] = Field(default_factory=list)
    linear_events: list[MergedEvent] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list, description="全部地点")


# ─── 忠实度检查模型 ──────────────────────────────────────────────


class FaithfulnessReport(BaseModel):
    """忠实度检查报告"""
    overall_score: float = Field(..., description="综合忠实度 0-1")
    character_consistency: float = Field(default=1.0, description="角色一致性")
    plot_accuracy: float = Field(default=1.0, description="情节准确度")
    hallucinated_plots: list[str] = Field(default_factory=list, description="疑似幻觉的情节")
    character_issues: list[str] = Field(default_factory=list, description="角色一致性问题")
    suggestions: list[str] = Field(default_factory=list, description="修正建议")
    hard_rule_violations: list[str] = Field(default_factory=list, description="硬规则违规")
