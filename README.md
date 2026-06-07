# AI 小说转剧本工具

将中文小说文本转换为好莱坞格式 YAML 剧本，基于 LLM 的三阶段 Pipeline。

## 项目简介

本项目是一个 NLP + LLM 应用，核心是将小说的叙事文本自动转换为剧本的结构化格式。
输入 3 个以上章节的中文小说，输出符合好莱坞标准（INT./EXT. Slug）的 YAML 剧本。

### 核心特性

- **三阶段 Pipeline**：逐章提取 -> 全局汇总 -> 剧本生成，借鉴 R2 (ICLR 2025) 论文两阶段框架
- **非线性叙事支持**：通过 timeline_type 字段处理倒叙（flashback）和插叙（flashforward）
- **内心戏外化**：Prompt 规则自动将心理描写转换为动作/对话
- **忠实度检查**：借鉴 HAR（幻觉感知修正）思想，硬规则 + LLM 软检查双重保障
- **多角色协作**：借鉴 HoLLMwood (EMNLP 2024) 论文，Writer / Editor / Actor 角色分工

## 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI 0.104.1 | 轻量异步、自动 API 文档 |
| LLM | DeepSeek API (兼容 OpenAI SDK) | 中文支持好、成本低 |
| 数据模型 | Pydantic v2 | 类型安全、自动校验 |
| 输出格式 | YAML + JSON | 人类可读、手写友好 |
| 前端 | 原生 HTML/CSS/JS | 零构建、浏览器直接打开 |

## 依赖清单

### Python 依赖 (backend/requirements.txt)

| 包名 | 版本 | 用途 |
|------|------|------|
| fastapi | 0.104.1 | Web 框架，REST API |
| uvicorn | 0.24.0 | ASGI 服务器 |
| openai | 1.6.1 | LLM API 客户端（DeepSeek 兼容） |
| python-dotenv | 1.0.0 | 环境变量管理 |
| pyyaml | 6.0.1 | YAML 解析与序列化 |

### 前端依赖

无。纯原生 HTML/CSS/JS，无需 npm install 或构建步骤。

### 外部服务

| 服务 | 用途 | 说明 |
|------|------|------|
| DeepSeek API | LLM 推理 | 需要 API Key（platform.deepseek.com） |
| OpenAI API (备选) | LLM 推理 | 可选，在 .env 中切换 provider |

## 原创功能说明

以下为本项目自主实现的核心功能：

1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成 + 容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试
2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试2. **多层 YAML 容错机制** (backend/yaml_utils.py)：四道防线提取 LLM 输出（yaml 代码块 -> 无标记 -> version: 定位 -> JSON 转 YAML），失败后自动重试
3.1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试 **硬规则校验系统** (backend/yaml_utils.py + backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖3. **硬规则校验系统** (backend/yaml_utils.py   backend/faithfulness.py)：角色 ID 交叉检查、场景 ID 连续性、关键角色覆盖
4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）+ 软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想4. **忠实度双重检查** (backend/faithfulness.py)：硬规则层（代码）  软检查层（LLM），借鉴 R2 的 HAR 思想
5. **Prompt Engineering** (backend/prompts.py)：四角色 System Prompt 设计，内置内心戏外化、slug 格式等核心规则
6. **中间数据模型** (backend/models.py)：ChapterExtraction -> MergedData -> Script 完整数据流转6. **中间数据模型** (backend/models.py)：ChapterExtraction -> MergedData -> Script 完整数据流转6. **中间数据模型** (backend/models.py)：ChapterExtraction -> MergedData -> Script 完整数据流转6. **中间数据模型** (backend/models.py)：ChapterExtraction -> MergedData -> Script 完整数据流转

## 项目结构

```
novel-to-screenplay/
├── backend/
│   ├── __init__.py          # 包声明
│   ├── app.py               # FastAPI 主程序
│   ├── config.py            # LLM 配置管理
│   ├── models.py            # Pydantic 数据模型
│   ├── prompts.py           # Prompt 模板
│   ├── pipeline.py          # 核心三阶段 Pipeline
│   ├── yaml_utils.py        # YAML 工具
│   ├── faithfulness.py      # 忠实度检查
│   └── requirements.txt     # Python 依赖
├── frontend/
│   ├── index.html           # 前端页面
│   ├── style.css            # 样式
│   └── script.js            # 前端逻辑
├── .env.example             # 环境变量模板
├── .gitignore
└── README.md
```

## 快速开始

### 1. 环境准备

```bash   ”“bash   “bash”;“bash```bash   ”“bash   “bash”;“bash
conda create -n novel2script python=3.11Conda create -n novel2script python=3.11
conda activate novel2script激活novel2scriptconda create -n novel2script python=3.11 conda create -n novel2script python=3.11
pip install -r backend/requirements.txtPIP install -r backend/requirements.txtPIP install -r backend/requirements。txtPIP install -r backend/requirements.txt
```

### 2. 配置 API Key1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试   ”“bash### 2. 配置 API Key1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试### 2. 配置 API Key1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试### 2. 配置 API Key1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试   ”“bash### 2. 配置 API Key1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试### 2. 配置 API Key1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试1. **三阶段分层 Pipeline** (backend/pipeline.py)：Stage 1 逐章独立提取 -> Stage 2 LLM 全局汇总去重排序 -> Stage 3 剧本生成   容错重试

```bash   ”“bash   “bash”;“bash```bash   ”“bash   “bash”;“bash```bash   ”“bash   “bash”;“bash```bash   ”“bash   “bash”;“bash
cp .env.example .env   图为.env。例如.env   图为.env。例如.env
# 编辑 .env 填入 DeepSeek API Key
```

### 3. 启动后端

```bash   ”“bash   “bash”;“bash```bash   ”“bash   “bash”;“bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000uvicorn后端。App: App——reload——host 0.0.0.0——port 8000uvicorn后端。App: App——reload——host 0.0.0.0——port 8000uvicornApp: App——reload——host 0.0.0.0—&mdash；端口8000
```

### 4. 打开前端

浏览器直接打开 frontend/index.html，访问 http://localhost:8000/docs 查看 API 文档。

## API 文档

### POST /convert

请求：chapters（至少3章）、title、author、genre
响应：script_yaml、script_json、scene_count、character_count、faithfulness_score、violations

### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查### GET /health — LLM 配置状态检查
### GET /schema — 剧本 Schema 字段说明### GET /schema — 剧本 Schema 字段说明### GET /schema — 剧本 Schema 字段说明### GET /schema — 剧本 Schema 字段说明

## YAML Schema

```yaml   “‘yaml   ’”yaml “ &lsquo yaml
version: "1.0"   版本:“1.0”;version: "1.0"   版本:“1.0”;
metadata:
  title: "剧本标题"   title: "剧本标题"title: "剧本标题"   title: "剧本标题"
  author: "原作者"   author: "原作者"author: "原作者"   author: "原作者"
  logline: "一句话梗概"   logline: "一句话梗概"logline: "一句话梗概"   logline: "一句话梗概"
  genre: "剧情"   genre: "剧情"genre: "剧情"   genre: "剧情"
characters:   人物:
  - id: "角色ID"   - id: "角色ID"- id: "角色ID"   - id: "角色ID"
    name: "角色名"   name: "角色名"name: "角色名"   name: "角色名"
    age_range: "25-35"   age_range:“25-35"Age_range:“25-35；
    description: "角色描述"   description: "角色描述"description: "角色描述"   description: "角色描述"
    importance_score: 0.9
scenes:   场景:
  - id: 1   —id: 1- id: 1   —id: 1
    timeline_type: "present"   timeline_type:“present"Timeline_type: "present"；
    slug: "INT. 咖啡馆 - 日"slug: "INT. 咖啡馆 - 日"slug: "INT. 咖啡馆 - 日"slug: "INT. 咖啡馆 - 日"
    setting:   设置:
      location: "咖啡馆"   location: "咖啡馆"location: "咖啡馆"   location: "咖啡馆"
      time_of_day: "日"   Time_of_day: "；time_of_day: "；
    characters_in_scene: ["角色ID"]characters_in_scene: ["角色ID"]
    actions:   行动:
      - description: "动作描述"   - description: "动作描述"
    dialogues:   对话:
      - character: "角色ID"   - character: "角色ID"
        lines:PIP install -r backend/requirements.txtPIP install -r backend/requirements.txt
          - text: "台词"   - text: "台词"
            parenthetical: "表演提示"   parenthetical: "表演提示"
```

## 理论基础

借鉴以下论文：
- R2 (Reader-Rewriter) — ICLR 2025：两阶段框架 + HAR 幻觉修正- R2 (Reader-Rewriter) — ICLR 2025：两阶段框架   HAR 幻觉修正
- HoLLMwood — EMNLP 2024：多角色协作 Writer/Editor/Actor- HoLLMwood — EMNLP 2024：多角色协作 Writer/Editor/Actor
- BookWorld — ACL 2025：角色特征提取- BookWorld — ACL 2025：角色特征提取

## Demo 视频
https://www.bilibili.com/video/BV1XDE86sEyS/?vd_source=ac515e44ce8936f88f0b97a89bbb6b41
   ”“bash   ”“bash   ”“bash   ”“bash”“bash   ”“bash   ”“bash   ”“bash
