"""YAML 工具：提取、解析、验证和修复 LLM 输出的 YAML 内容。"""

import json
import re
import yaml
from typing import Optional

from .models import Script


def extract_yaml_from_text(content: str) -> str:
    """从 LLM 输出中提取 YAML 内容。

    处理以下情况：
    1. markdown 代码块包裹 ```yaml ... ```
    2. markdown 代码块包裹 ``` ... ```
    3. 纯 YAML 文本（从 version: 开始）
    4. 纯 JSON 文本（先转 YAML）

    Args:
        content: LLM 的原始输出文本

    Returns:
        提取出的 YAML 文本（去除代码块标记）
    """
    content = content.strip()

    # 情况1: ```yaml ... ```
    match = re.search(r"```yaml\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 情况2: ``` ... ```（无语言标记）
    match = re.search(r"```\s*\n(.*?)\n```", content, re.DOTALL)
    if match:
        inner = match.group(1).strip()
        # 判断是否为 YAML/JSON
        if inner.startswith("version:") or inner.startswith("{"):
            return inner
        # 可能是 YAML 但以其他字段开头
        if ":" in inner.split("\n")[0]:
            return inner

    # 情况3: 寻找 version: 开头
    version_match = re.search(r"^(version:\s)", content, re.MULTILINE)
    if version_match:
        return content[version_match.start():].strip()

    # 情况4: 尝试从 { 开头的 JSON 提取
    json_match = re.search(r"^(\{.*\})$", content, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            return yaml.dump(data, allow_unicode=True, sort_keys=False)
        except json.JSONDecodeError:
            pass

    # 返回原始内容作为最后手段
    return content


def parse_script_yaml(yaml_text: str) -> Script:
    """解析 YAML 文本为 Script 模型。

    Args:
        yaml_text: YAML 文本

    Returns:
        Script 对象

    Raises:
        yaml.YAMLError: YAML 语法错误
        ValueError: 数据校验失败
    """
    data = yaml.safe_load(yaml_text)

    if data is None:
        raise ValueError("YAML 解析结果为空，请检查格式")

    if not isinstance(data, dict):
        raise ValueError(f"YAML 解析结果应为字典，实际为 {type(data).__name__}")

    # 补充默认值
    if "version" not in data:
        data["version"] = "1.0"

    # 确保 characters 存在
    if "characters" not in data:
        data["characters"] = []

    # 确保 scenes 存在
    if "scenes" not in data:
        data["scenes"] = []

    return Script(**data)


def validate_script_hard_rules(script: Script) -> list[str]:
    """硬规则校验剧本，返回违规列表。

    规则：
    1. 角色ID交叉检查：dialogues 和 characters_in_scene 中的角色必须在 characters 列表中
    2. 场景ID连续性检查
    3. 关键角色覆盖检查

    Args:
        script: 剧本对象

    Returns:
        违规描述列表（空列表表示全部通过）
    """
    violations: list[str] = []

    # 收集所有已定义的角色ID
    defined_ids: set[str] = {c.id for c in script.characters}

    # 规则1: 角色ID交叉检查
    for scene in script.scenes:
        # 检查 characters_in_scene
        for cid in scene.characters_in_scene:
            if cid not in defined_ids:
                violations.append(
                    f"场景 {scene.id}: characters_in_scene 中的 '{cid}' 未在 characters 列表中定义"
                )

        # 检查 dialogues
        for dialogue in scene.dialogues:
            if dialogue.character not in defined_ids:
                violations.append(
                    f"场景 {scene.id}: dialogue 角色 '{dialogue.character}' 未在 characters 列表中定义"
                )

    # 规则2: 场景ID连续性
    scene_ids = sorted([s.id for s in script.scenes])
    expected_ids = list(range(1, len(scene_ids) + 1))
    if scene_ids != expected_ids:
        violations.append(
            f"场景ID不连续：期望 {expected_ids}，实际 {scene_ids}"
        )

    # 规则3: 关键角色（importance_score > 0.5）必须在至少一个场景中出现
    key_characters = [
        c for c in script.characters
        if c.importance_score and c.importance_score > 0.5
    ]
    all_scene_characters: set[str] = set()
    for scene in script.scenes:
        all_scene_characters.update(scene.characters_in_scene)
        for dialogue in scene.dialogues:
            all_scene_characters.add(dialogue.character)

    for char in key_characters:
        if char.id not in all_scene_characters:
            violations.append(
                f"关键角色 '{char.name}' (importance_score={char.importance_score}) 未在任何场景中出现"
            )

    return violations


def script_to_yaml(script: Script) -> str:
    """将 Script 对象序列化为规范 YAML 文本。

    使用自定义序列化，确保输出格式符合 Schema 设计。

    Args:
        script: 剧本对象

    Returns:
        格式化的 YAML 字符串
    """
    # Pydantic model_dump 转换为字典
    data = script.model_dump(exclude_none=True, mode="python")

    # 使用 pyyaml 序列化
    return yaml.dump(
        data,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        indent=2,
        width=120,
    )


def get_script_json(script: Script) -> str:
    """将 Script 对象序列化为 JSON，方便前端展示。

    Args:
        script: 剧本对象

    Returns:
        格式化的 JSON 字符串
    """
    return json.dumps(
        script.model_dump(exclude_none=True, mode="python"),
        ensure_ascii=False,
        indent=2,
    )
