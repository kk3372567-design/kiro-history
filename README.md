# Kiro 历史归档（kirocrew export）

> 导出时间：2026-11-10　|　来源：Kiro Crew 本地数据导出　|　仓库用途：供 AI 助手克隆后检索阅读
>
> **给克隆本仓库的 AI 助手**：这是一份个人工作记忆与项目稿归档。请先读本文件，再按下方"推荐阅读顺序"进入对应目录；**不要整文件打开 `sessions/` 下的大 jsonl**（单文件可达 60M+，是原始聊天流水），需要时用关键词 grep 定向取片段即可。

---

## 目录地图

| 路径 | 是什么 | AI 应该怎么读 |
|---|---|---|
| `workspace/` | **核心干货**：用户实际在做的项目稿件与知识库 | ✅ 优先通读。各子目录是独立项目 |
| `memory_stores/` | 用户长期记忆：偏好、项目沉淀 | ✅ 先读 `memory/projects.md`、`memory/preferences.md` |
| `skills/` | 41 个 Kiro skill 定义（md + py） | 按需检索，不是必读 |
| `sessions/` | 16 段历史对话原始记录（jsonl） | ⚠️ 大文件，**grep 检索**，勿全文读 |
| `workspace/knowledge/` `workspace/memory/` | 知识库与记忆 md | ✅ 通读 |
| `memory.db` `memory_index.db` | SQLite 数据库（二进制） | ❌ 二进制，AI 无法直接读；文本记忆已在 md 里 |
| `config.json` `hooks.json` `ui-prefs.json` | 本地配置 | 一般不需要读 |
| `notifications.jsonl` | 通知流水 | 一般不需要读 |
| `MANIFEST.json` | 导出清单 | 需要核对文件来源时读 |

## workspace/ 下的项目

- `爆款编剧/`
- `直播闯深山_终稿/`
- `软饭驸马_v5考试/`
- `TT大赛/`
- `knowledge/` — 知识库
- `memory/` — 工作记忆
- `HEARTBEAT.md`

## 推荐阅读顺序（AI 助手建议）

1. 本文件（README.md）
2. `memory_stores/.../memory/preferences.md` — 用户偏好与工作习惯
3. `memory_stores/.../memory/projects.md` — 用户在推进的项目
4. `workspace/HEARTBEAT.md`、`workspace/memory/`、`workspace/knowledge/`
5. 进入具体项目子目录读稿件
6. 如需追溯某话题的历史讨论，再到 `sessions/` 用关键词 grep

## 备注

- 仓库为 **private**，含私人对话与稿件，仅 owner 可访问。
- `sessions/*.attachments/` 内存放历史对话中的图片附件（png 等）。
- 二进制 `.db` 文件保留是为了完整归档，AI 阅读时直接跳过即可。
