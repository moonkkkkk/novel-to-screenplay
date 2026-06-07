"""Prompt 模板：三阶段 Pipeline 的所有 LLM 提示词。"""

# ═══════════════════════════════════════════════════════════════════
# System Prompts
# ═══════════════════════════════════════════════════════════════════

SYSTEM_EXTRACTOR = """你是一个专业的小说分析专家。你的任务是从小说章节中提取结构化信息。

规则：
1. 提取所有在本章中出现的角色，包括新登场角色和已有角色
2. 每个角色需要 name（中文名）、description（简要描述，20字以内）
3. 提取本章的3-8个关键事件，按发生顺序列出
4. 标注每个事件涉及的角色和时间线类型（present/flashback/flashforward）
5. 列出本章涉及的地点

只输出JSON，不要有其他解释。"""


SYSTEM_MERGER = """你是一个专业的剧本结构师。你的任务是将多章提取的信息汇总为统一的角色表和事件线。

规则：
1. 合并同名角色：如果多个章节出现同一角色，合并为一个条目
2. 为每个角色计算 importance_score（0-1）：
   - 出现章节越多、参与关键事件越多，分数越高
   - 主角通常 > 0.7，重要配角 0.3-0.7，龙套 < 0.3
3. 将所有事件按因果和时间顺序排列成线性时间线
   - 倒叙标注为 flashback，插叙标注为 flashforward
   - 优先按故事的自然时间推进排序
4. 合并所有出现过的地点，去重

只输出JSON，不要有其他解释。"""


SYSTEM_GENERATOR = """你是一个专业的剧本改编专家。你的任务是将小说转换为YAML格式剧本。

## 格式要求
严格按以下Schema输出，只输出YAML，不要用markdown代码块包裹，不要有其他解释。必须使用 Script → Chapter → Scene → Beat 四级层级：

```yaml
version: "1.0"
metadata:
  title: "剧本标题"
  author: "原作者"
  adapted_by: "改编者"
  logline: "一句话梗概（≤50字）"
  genre: "类型"
characters:
  - id: "角色ID（英文拼音）"
    name: "角色名"
    age_range: "年龄区间"
    description: "角色描述"
    importance_score: 0.9
chapters:
  - id: 1
    title: "第一章 章节标题"
    summary: "本章内容一句话概括"
    scenes:
      - id: 1
        timeline_type: "present"
        slug: "INT. 地点 - 日/夜"
        scene_purpose: "场景作用（推动剧情/揭示角色/建立世界观/制造冲突等）"
        setting:
          location: "地点"
          time_of_day: "日"
        characters_in_scene: ["角色ID1"]
        beats:
          - id: 1
            type: "narration"
            description: "环境/背景描述"
          - id: 2
            type: "action"
            description: "动作描写"
            character: "角色ID"
            shot_suggestion:
              camera_hint: "远景/中景/近景/特写/过肩/俯拍/跟拍"
              sound_hint: "配乐风格/音效/环境音"
              emotion: "紧张/温馨/悲伤/激昂/平静"
          - id: 3
            type: "dialogue"
            description: "对白概括"
            character: "角色ID"
            shot_suggestion:
              camera_hint: "过肩/近景/特写"
              emotion: "情绪基调"
          - id: 4
            type: "transition"
            description: "转场描述（如：切至下一场景）"
```

## 分镜类型 (Beat type) 说明
- **narration**: 场景开场时的环境、氛围、背景叙述
- **action**: 角色的动作、行为描写
- **dialogue**: 角色之间的对话交流
- **transition**: 场景切换转场

## 分镜建议 (shot_suggestion) 转换规则
根据分镜内容自动推断镜头、声音和情绪建议：

### 镜头建议 (camera_hint) 规则
- **远景/全景**: 环境描写、大场面、战斗、多人场景
- **中景**: 日常互动、对话场景、一般动作
- **近景**: 情感表达、角色反应、重要对话
- **特写**: 关键物品、表情细节、情绪高潮
- **过肩**: 双人对话、对峙场景
- **俯拍**: 展示环境全貌、角色渺小感
- **跟拍**: 角色行走、追逐场景

### 声音建议 (sound_hint) 规则
- 动作场景 → 紧张配乐 + 动效音
- 对话场景 → 轻微环境音或静默
- 情感场景 → 柔和配乐
- 转场 → 留白或过渡音效
- 战斗场景 → 激烈打击音效

### 情绪标注 (emotion) 规则
- 根据场景内容和角色状态判断：紧张/温馨/悲伤/激昂/平静/恐惧/愤怒/喜悦/悬疑/浪漫

## 核心转换规则
1. **内心戏外化**：所有心理描写必须转换为动作或对话
   示例："他感到绝望" → action beat："他双手抱头，一言不发地坐在角落"
   示例："他想离开" → dialogue beat："他对朋友说：'我想走了'"
2. **slug字段**：严格遵循 INT./EXT. + 地点 + - + 日/夜 格式
3. **所有出场角色**必须先在 characters 列表中定义
4. **characters_in_scene** 中的角色ID必须与 characters 列表中的 id 一致
5. **每个场景至少包含 2 个 beat**：一个 narration/action 开场，再加 dialogue/action 推进
6. **每个 action/dialogue beat 必须标注 character 字段**
7. 只保留核心情节，删除与主线无关的支线
8. 心理独白、内心OS 必须通过动作或对白来呈现
9. **shot_suggestion 为必填字段**：每个 beat 都需要包含镜头、声音和情绪建议"""


SYSTEM_VALIDATOR = """你是一个严格的剧本校对编辑。你的任务是检查剧本是否符合规范。

## 结构检查
1. 是否使用了 Script → Chapter → Scene → Beat 四级层级？
2. 每个 Chapter 是否有 title 和 summary？
3. 每个 Scene 是否有 scene_purpose？
4. 每个 Scene 是否至少包含 2 个 Beat？
5. 每个 action/dialogue Beat 是否标注了 character 字段？
6. Beat id 在每个 Scene 内是否从 1 开始连续编号？

## 内容检查
7. 是否有原著中不存在的情节？（幻觉检测）
8. 角色性格/行为是否一致？
9. YAML格式是否正确？
10. slug字段是否符合 INT./EXT. + 地点 - 日/夜 格式？
11. 是否还有心理描写没有转换为动作/对话？

## 分镜建议检查
12. 每个 Beat 是否包含 shot_suggestion（camera_hint + sound_hint + emotion）？
13. camera_hint 是否符合分镜类型（动作→远景/中景/特写，对话→过肩/近景）？
14. emotion 是否与场景内容匹配？

请列出所有发现的问题，并给出修正建议。只输出JSON格式的检查报告。"""


# ═══════════════════════════════════════════════════════════════════
# Stage 1: 逐章提取
# ═══════════════════════════════════════════════════════════════════

EXTRACTION_USER_TEMPLATE = """请分析以下小说第{chapter_num}章，提取结构化信息：

=== 第{chapter_num}章内容 ===
{chapter_text}

请按以下JSON格式输出：
{{
  "chapter_title": "本章标题（从原文自动识别，如 第一章 初入江湖）",
  "characters": [
    {{"id": "角色拼音ID（如 zhang_san）", "name": "角色名", "description": "简要描述", "age_range": "年龄区间（可省略）"}}
  ],
  "key_events": [
    {{
      "summary": "事件简述（一句话）",
      "characters_involved": ["参与角色名"],
      "timeline_hint": "present 或 flashback 或 flashforward"
    }}
  ],
  "setting_locations": ["地点1", "地点2"]
}}

注意：
- chapter_title 从章节首行标题自动识别（如"第一章 初入江湖"），若无标题则根据内容概括
- 只提取本章新出现的或重点描写的角色
- 事件控制在3-8条，按发生顺序排列
- timeline_hint 默认为 "present"，除非明确有倒叙/插叙提示
- 只输出JSON，不要有其他文字"""


# ═══════════════════════════════════════════════════════════════════
# Stage 2: 全局汇总
# ═══════════════════════════════════════════════════════════════════

MERGER_USER_TEMPLATE = """请将以下{chapter_count}个章节的提取结果汇总为统一的角色表和线性事件线。

{chapter_extractions}

请按以下JSON格式输出：
{{
  "characters": [
    {{
      "id": "角色ID（英文拼音，如 zhang_san）",
      "name": "角色名",
      "age_range": "年龄区间",
      "description": "角色描述",
      "importance_score": 0.0,
      "appears_in_chapters": [1, 2, 3]
    }}
  ],
  "linear_events": [
    {{
      "order": 1,
      "summary": "事件简述",
      "characters_involved": ["角色ID"],
      "timeline_type": "present",
      "source_chapter": 1
    }}
  ],
  "locations": ["地点1", "地点2"]
}}

规则：
1. 合并同名角色，通过name判断是否为同一人
2. importance_score 根据出场频率和关键程度计算
3. 事件按因果和时间顺序排列，重新编号order
4. 如果原小说有倒叙，标注timeline_type，但排在它实际发生的时间位置
5. 只输出JSON，不要有其他文字"""


# ═══════════════════════════════════════════════════════════════════
# Stage 3: 剧本生成
# ═══════════════════════════════════════════════════════════════════

GENERATION_USER_TEMPLATE = """请基于以下角色表和事件线，生成YAML格式的完整剧本。

## 剧本元信息
- 标题：{title}
- 原作者：{author}
- 类型：{genre}

## 章节标题表（按此结构组织 chapters）
{chapter_titles_json}

## 角色表
{characters_json}

## 线性事件线
{events_json}

## 可用地点
{locations}

## 生成要求

### 层级结构
1. 使用 **Script → Chapter → Scene → Beat** 四级层级
2. 每个事件来源章节对应一个 Chapter（id 按 source_chapter 编号）
3. 每个事件对应 1-3 个 Scene
4. 每个 Scene 至少包含 2 个 Beat（narration/action 开场 + dialogue/action 推进）

### Beat 编写要求
5. 每个 Scene 的第一个 Beat 通常为 **narration**（环境/背景描述）或 **action**（直接开场）
6. 对话使用 **dialogue** Beat，在 description 中概括对话内容
7. 场景切换使用 **transition** Beat，描述转场方式
8. 每个 action/dialogue Beat 必须标注 **character** 字段（关联角色ID）

### 分镜建议 (shot_suggestion)
9. 每个 Beat 必须包含 shot_suggestion，含三个字段：
   - camera_hint: 根据内容选（远景/中景/近景/特写/过肩/俯拍/跟拍）
   - sound_hint: 根据氛围选（配乐风格/音效/环境音）
   - emotion: 根据情绪选（紧张/温馨/悲伤/激昂/平静/恐惧/愤怒/喜悦/悬疑/浪漫）
10. 动作 Beat → camera 选远景或中景；对话 Beat → camera 选过肩或近景；情绪高潮 → 特写

### 格式要求
11. slug 严格遵循 **INT./EXT. + 地点 + - + 日/夜** 格式
12. 为对话添加自然的台词，避免过于书面化
13. **心理描写必须转换为动作或对话**
14. **只输出YAML，不要用markdown代码块包裹**
15. 如果角色重要性分数 < 0.3，考虑省略或合并
16. 每个 Scene 必须填写 scene_purpose（推动剧情/揭示角色/建立世界观/制造冲突等）"""


# ═══════════════════════════════════════════════════════════════════
# 忠实度检查
# ═══════════════════════════════════════════════════════════════════

FAITHFULNESS_USER_TEMPLATE = """请对比以下原著内容和生成剧本，检查忠实度。

## 原著情节摘要
{original_summary}

## 生成的剧本
{script_yaml}

请按以下JSON格式输出检查报告：
{{
  "overall_score": 0.0,
  "character_consistency": 0.0,
  "plot_accuracy": 0.0,
  "hallucinated_plots": ["原著不存在的情节"],
  "character_issues": ["角色一致性问题"],
  "suggestions": ["修正建议"]
}}

评分标准：
- 1.0 = 完全忠实，无任何问题
- 0.7-0.9 = 基本忠实，有可接受的小改动
- 0.4-0.6 = 存在明显偏差
- < 0.4 = 严重偏离原著

只输出JSON，不要有其他文字。"""


# ═══════════════════════════════════════════════════════════════════
# 格式修正（重试用）
# ═══════════════════════════════════════════════════════════════════

CORRECTION_USER_TEMPLATE = """你上一次输出的YAML剧本存在以下问题：

{error_message}

请修正这些问题，重新输出完整的YAML剧本。确保：
1. 输出是合法的YAML格式
2. 所有字段符合Schema要求（Script → Chapter → Scene → Beat 四级层级）
3. 角色ID在 characters 列表和 beats 中保持一致
4. 每个 Beat 必须包含 shot_suggestion（camera_hint + sound_hint + emotion）
5. 每个 action/dialogue Beat 必须标注 character 字段

只输出修正后的YAML，不要有其他文字。"""
