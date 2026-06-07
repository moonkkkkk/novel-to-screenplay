"""FastAPI 主程序：小说转剧本 API 服务。"""

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .chapter_parser import parse_chapters_simple
from .models import Script
from .pipeline import NovelToScriptPipeline
from .yaml_utils import script_to_yaml, validate_script_hard_rules

app = FastAPI(
    title="小说转剧本 API",
    description="将中文小说文本转换为好莱坞格式 YAML 剧本",
    version="1.0.0",
)

# CORS 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 前端静态文件
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# ─── 请求/响应模型 ──────────────────────────────────────────────


class ConvertRequest(BaseModel):
    """转换请求 — 支持两种输入模式：
    1. chapters: 手动分好的章节列表
    2. raw_text: 整本小说文本，服务端自动识别章节标题切分
    """
    chapters: Optional[list[str]] = Field(
        default=None, description="章节文本列表（手动分章）"
    )
    raw_text: Optional[str] = Field(
        default=None, description="整本小说文本（自动识别章节）"
    )
    title: str = Field(default="未命名剧本", description="剧本标题")
    author: str = Field(default="未知", description="原作者")
    genre: str = Field(
        default="剧情",
        description="类型：剧情/喜剧/悬疑/科幻/动作/爱情",
    )


class ConvertResponse(BaseModel):
    """转换响应"""
    success: bool
    script_yaml: str = Field(default="", description="YAML 格式剧本")
    script_json: str = Field(default="", description="JSON 格式剧本")
    scene_count: int = Field(default=0, description="场景数")
    character_count: int = Field(default=0, description="角色数")
    faithfulness_score: float = Field(default=0.0, description="忠实度评分")
    violations: list[str] = Field(default_factory=list, description="硬规则违规")
    error: Optional[str] = Field(default=None, description="错误信息")


# ─── API 路由 ────────────────────────────────────────────────────


@app.get("/")
async def root():
    """前端主页"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"service": "小说转剧本 API", "version": "1.0.0", "status": "running"}


@app.post("/convert", response_model=ConvertResponse)
async def convert_novel(request: ConvertRequest):
    """将小说转换为剧本。

    支持两种输入模式：
    - chapters: 手动分好的章节列表
    - raw_text: 整本小说文本，服务端自动识别章节切分

    内部执行三阶段流水线：提取 → 汇总 → 生成。
    """
    try:
        # 确定章节列表
        if request.raw_text and request.raw_text.strip():
            chapters = parse_chapters_simple(request.raw_text)
        elif request.chapters:
            chapters = [c for c in request.chapters if c and c.strip()]
        else:
            raise ValueError("请提供 chapters（章节列表）或 raw_text（整本小说文本）")

        if len(chapters) < 3:
            raise ValueError(
                f"需要至少 3 个章节，当前只识别到 {len(chapters)} 章。"
                "请检查文本是否包含章节标题（如'第一章'或'Chapter 1'）"
            )

        # 初始化 Pipeline（每次请求新建实例，避免状态污染）
        pipeline = NovelToScriptPipeline()

        # 执行转换
        script, report = pipeline.run(
            chapters=chapters,
            title=request.title,
            author=request.author,
            genre=request.genre,
        )

        # 生成 YAML 和 JSON
        script_yaml = script_to_yaml(script)
        from .yaml_utils import get_script_json
        script_json = get_script_json(script)

        return ConvertResponse(
            success=True,
            script_yaml=script_yaml,
            script_json=script_json,
            scene_count=len(script.scenes),
            character_count=len(script.characters),
            faithfulness_score=report.overall_score,
            violations=report.hard_rule_violations,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.get("/health")
async def health():
    """详细健康检查"""
    try:
        from .config import get_llm_config
        config = get_llm_config()
        return {
            "status": "ok",
            "llm_provider": config.provider,
            "llm_model": config.model,
            "api_key_configured": bool(config.api_key),
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
        }


@app.get("/schema")
async def get_schema():
    """返回剧本 Schema 描述"""
    return {
        "version": "1.0",
        "description": "好莱坞格式剧本 YAML Schema",
        "top_level_fields": {
            "version": "Schema 版本号",
            "metadata": "剧本元信息（title, author, logline, genre）",
            "characters": "角色列表（id, name, age_range, description, importance_score）",
            "scenes": "场景列表（id, slug, setting, characters_in_scene, actions, dialogues）",
        },
        "slug_format": "INT./EXT. + 地点 + - + 日/夜",
        "timeline_types": ["present", "flashback", "flashforward"],
    }
