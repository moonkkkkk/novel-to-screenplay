"""数据模型：定义剧本 Schema 和 Pipeline 中间数据结构。

层级：Script → Chapter → Scene → Beat（四级）
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════
# 枚举类型
# ═══════════════════════════════════════════════════════════════════

class BeatType(str, Enum):
    """分镜类型"""
    ACTION = "action"          # 动作
    DIALOGUE = "dialogue"      # 对白
    NARRATION = "narration"    # 旁白
    TRANSITION = "transition"  # 转场


# ═══════════════════════════════════════════════════════════════════
# YAML Schema 模型 — Script 层级
# ═══════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════
# 分镜 (Beat) 层级 — 最小故事单元
# ═══════════════════════════════════════════════════════════════════

class ShotSuggestion(BaseModel):
    """分镜提示：镜头与声音建议"""
    camera_hint: Optional[str] = Field(
        default=None,
        description="镜头建议（远景/中景/近景/特写/过肩/俯拍/跟拍等）"
    )
    sound_hint: Optional[str] = Field(
        default=None,
        description="声音建议（配乐风格/音效/环境音/静默等）"
    )
    emotion: Optional[str] = Field(
        default=None,
        description="本段情绪基调（紧张/温馨/悲伤/激昂/平静等）"
    )


class Beat(BaseModel):
    """分镜：剧本的最小叙事单元

    一个 Scene 由多个 Beat 组成。
    每个 Beat 描述一个独立的动作、一段对白、一段旁白或一个转场。
    """
    id: int = Field(..., description="分镜序号（场景内唯一）")
    type: BeatType = Field(..., description="分镜类型")
    description: str = Field(..., description="内容描述")
    character: Optional[str] = Field(
        default=None,
        description="关联角色ID（action/dialogue 类型必填，narration/transition 可选）"
    )
    shot_suggestion: Optional[ShotSuggestion] = Field(
        default=None,
        description="镜头与声音建议"
    )


# ═══════════════════════════════════════════════════════════════════
# 向后兼容保留（旧 API 仍可工作）
# ═══════════════════════════════════════════════════════════════════

class Action(BaseModel):
    """动作描写（向后兼容，推荐使用 Beat(type=action)）"""
    description: str = Field(..., description="动作描述")


class DialogueLine(BaseModel):
    """单句台词（向后兼容）"""
    text: str = Field(..., description="台词文本")
    parenthetical: Optional[str] = Field(default=None, description="表演提示")


class Dialogue(BaseModel):
    """对话块（向后兼容，推荐使用 Beat(type=dialogue)）"""
    character: str = Field(..., description="说话角色ID")
    lines: list[DialogueLine] = Field(default_factory=list, description="台词行")


# ═══════════════════════════════════════════════════════════════════
# 场景 (Scene) 层级
# ═══════════════════════════════════════════════════════════════════

class Scene(BaseModel):
    """场景"""
    id: int = Field(..., description="场景序号（章内唯一）")
    timeline_type: Optional[str] = Field(
        default="present", description="present / flashback / flashforward"
    )
    slug: str = Field(..., description="标题，如 INT. 咖啡馆 - 日")
    setting: Setting = Field(..., description="场景设置")
    scene_purpose: Optional[str] = Field(
        default=None,
        description="场景作用（推动剧情/揭示角色/建立世界观/制造冲突等）"
    )
    characters_in_scene: list[str] = Field(default_factory=list, description="出场角色ID列表")
    beats: list[Beat] = Field(default_factory=list, description="分镜列表（推荐）")
    # 向后兼容：旧 API 的 actions/dialogues 继续保留
    actions: list[Action] = Field(default_factory=list, description="动作描写（向后兼容）")
    dialogues: list[Dialogue] = Field(default_factory=list, description="对话（向后兼容）")


# ═══════════════════════════════════════════════════════════════════
# 章节 (Chapter) 层级 — 按小说章节划分
# ═══════════════════════════════════════════════════════════════════

class Chapter(BaseModel):
    """章节：对应原小说的一个章节，包含若干场景"""
    id: int = Field(..., description="章节序号（从1开始）")
    title: str = Field(..., description="章节标题（如 第一章 初入江湖）")
    summary: Optional[str] = Field(default=None, description="章节内容摘要")
    scenes: list[Scene] = Field(default_factory=list, description="本章场景列表")


# ═══════════════════════════════════════════════════════════════════
# 完整剧本 (Script) 层级
# ═══════════════════════════════════════════════════════════════════

class Script(BaseModel):
    """完整剧本

    支持两种模式：
    1. 新层级：chapters[].scenes[].beats[] — Script → Chapter → Scene → Beat
    2. 向后兼容：scenes[] — Script → Scene（旧项目无缝迁移）
    """
    version: str = Field(default="1.0", description="Schema版本号")
    metadata: ScriptMetadata = Field(..., description="元信息")
    characters: list[Character] = Field(default_factory=list, description="角色列表")
    chapters: list[Chapter] = Field(default_factory=list, description="章节列表（推荐）")
    # 向后兼容
    scenes: list[Scene] = Field(default_factory=list, description="场景列表（向后兼容）")

    def all_scenes(self) -> list[Scene]:
        """获取所有场景（兼容新旧两种模式）"""
        if self.chapters:
            result: list[Scene] = []
            for ch in self.chapters:
                result.extend(ch.scenes)
            return result
        return self.scenes

    def all_beats(self) -> list[Beat]:
        """获取所有分镜"""
        beats: list[Beat] = []
        for scene in self.all_scenes():
            beats.extend(scene.beats)
        return beats

    @property
    def chapter_count(self) -> int:
        """章节数"""
        return len(self.chapters) if self.chapters else (len(self.scenes) > 0 and 1 or 0)

    @property
    def scene_count(self) -> int:
        """场景总数"""
        return len(self.all_scenes())

    @property
    def beat_count(self) -> int:
        """分镜总数"""
        return len(self.all_beats())


# ═══════════════════════════════════════════════════════════════════
# Pipeline 中间数据模型
# ═══════════════════════════════════════════════════════════════════

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
    chapter_title: Optional[str] = Field(default=None, description="章节标题")
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


# ═══════════════════════════════════════════════════════════════════
# 忠实度检查模型
# ═══════════════════════════════════════════════════════════════════

class FaithfulnessReport(BaseModel):
    """忠实度检查报告"""
    overall_score: float = Field(..., description="综合忠实度 0-1")
    character_consistency: float = Field(default=1.0, description="角色一致性")
    plot_accuracy: float = Field(default=1.0, description="情节准确度")
    beat_quality: float = Field(default=1.0, description="分镜质量（Beat 级别）")
    hallucinated_plots: list[str] = Field(default_factory=list, description="疑似幻觉的情节")
    character_issues: list[str] = Field(default_factory=list, description="角色一致性问题")
    suggestions: list[str] = Field(default_factory=list, description="修正建议")
    hard_rule_violations: list[str] = Field(default_factory=list, description="硬规则违规")
