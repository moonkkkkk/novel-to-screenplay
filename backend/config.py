"""配置管理：加载 .env 文件，提供全局配置。"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 加载项目根目录的 .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


@dataclass
class LLMConfig:
    """LLM API 配置"""
    provider: str = "deepseek"
    api_key: str = ""
    base_url: str = ""
    model: str = ""
    temperature: float = 0.3
    max_tokens: int = 4096


def get_llm_config() -> LLMConfig:
    """从环境变量加载 LLM 配置。"""
    provider = os.getenv("LLM_PROVIDER", "deepseek").lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")
    else:
        api_key = os.getenv("DEEPSEEK_API_KEY", "")
        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    temperature = float(os.getenv("TEMPERATURE", "0.3"))
    max_tokens = int(os.getenv("MAX_TOKENS", "4096"))

    return LLMConfig(
        provider=provider,
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
