# Agent 日志结构说明

## 日志根目录

所有 agent 的交互日志都写在 **jobs 目录** 下：

```
<jobs_dir>/<job_name>/<task_name>__<trial_id>/agent/
```

例如：
- `../jobs/vllm_local_test/civ6-adjacency-optimizer__MEHVtn4/agent/`
- `../jobs/combined_earthquake_test_03180949/civ6-adjacency-optimizer__NvG3eWx/agent/`

---

## 为什么 vLLM 用 episode，Codex 用不同结构？

**根本原因：两类 agent 的实现方式不同。**

| Agent 类型 | 实现方式 | 日志结构 |
|-----------|----------|----------|
| **terminus-2-skills**（vLLM） | 自定义 agent，在 Python 中直接调用 LLM，循环执行 | `episode-0/`, `episode-1/`, ... |
| **codex** | Harbor 内置 agent，在容器内启动 Codex CLI，由 CLI 自行写日志 | `codex.txt`, `sessions/`, `command-*/`, ... |

---

## terminus-2-skills（vLLM）的 episode 结构

**实现位置**：`libs/terminus_agent/agents/terminus_2/harbor_terminus_2_skills.py`

该 agent 在 `run()` 中显式创建 episode 目录并写入日志：

```python
# 第 367-371 行
episode_dir = self.logs_dir / f"episode-{episode}"
episode_dir.mkdir(parents=True, exist_ok=True)
prompt_path = episode_dir / "prompt.txt"    # 发给模型的 prompt
response_path = episode_dir / "response.txt" # 模型返回的 response
```

**目录结构**：

```
agent/
├── episode-0/
│   ├── prompt.txt       # 第 0 轮发给 LLM 的完整 prompt
│   ├── response.txt     # 第 0 轮 LLM 的原始输出
│   └── prompt_template.txt  # 仅 episode-0 有，初始模板
├── episode-1/
│   ├── prompt.txt
│   └── response.txt
├── ...
└── trajectory.json      # 完整轨迹 [{episode, prompt, response}, ...]
```

每一轮「调用 LLM → 解析输出 → 执行命令 → 更新 prompt」对应一个 episode。

---

## Codex 的 sessions/command 结构

**实现位置**：Harbor 内置 `harbor.agents.installed.codex.Codex`（继承 `BaseInstalledAgent`）

Codex agent 不直接调 LLM，而是在容器里启动 **Codex CLI**。日志由 Codex CLI 自己写入，格式是 Cursor/Codex IDE 的会话格式。

**目录结构**：

```
agent/
├── codex.txt            # Codex CLI 的 JSONL 输出（含 usage 等）
├── command-0/           # 第 1 个命令的执行目录
├── command-1/           # 第 2 个命令的执行目录
├── sessions/
│   └── 2026/03/18/
│       └── rollout-*.jsonl   # 会话事件流（turn.started, item.completed 等）
├── setup/                # 环境初始化
├── shell_snapshots/      # 终端状态快照
├── memories/             # agent 记忆
├── skills/               # 已加载的 skills
├── trajectory.json       # Harbor 汇总的轨迹
└── state_5.sqlite        # Codex 内部状态
```

`codex.txt` 是模型交互的主日志；`sessions/` 下的 `rollout-*.jsonl` 是细粒度事件流（如 `command_execution`、`agent_message`）。

---

## 如何查看模型输出

| Agent | 模型输出位置 |
|-------|--------------|
| **terminus-2-skills (vLLM)** | `agent/episode-*/response.txt` |
| **codex** | `agent/codex.txt`（JSONL），以及 `agent/sessions/.../rollout-*.jsonl` 中的 `agent_message`、`command_execution` 等 |

---

## 修改 terminus-2-skills 的日志格式

如需调整 episode 的写入方式，可修改：

`libs/terminus_agent/agents/terminus_2/harbor_terminus_2_skills.py` 第 365-406 行附近的日志逻辑。
