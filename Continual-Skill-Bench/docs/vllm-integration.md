# SkillsBench 接入可训练模型（vLLM）指南

## 一、模型接入控制点

### 1. 核心调用链

```
实验配置 (experiments/configs/*.yaml)
    ↓ model_name, kwargs (api_base, api_key)
Harbor AgentFactory
    ↓ 实例化时传入
HarborTerminus2WithSkills (libs/terminus_agent/agents/terminus_2/harbor_terminus_2_skills.py)
    ↓ 构造 LiteLLM
LiteLLM (libs/terminus_agent/llms/lite_llm.py)
    ↓ litellm.completion(api_base=..., api_key=...)
litellm.completion() → 实际 API 调用
```

### 2. 关键文件

| 文件 | 作用 |
|------|------|
| `libs/terminus_agent/agents/terminus_2/harbor_terminus_2_skills.py` | Agent 构造函数接收 `model_name`, `api_base`, `api_key`，创建 LiteLLM 客户端 |
| `libs/terminus_agent/llms/lite_llm.py` | 将 `api_base`、`api_key` 传给 `litellm.completion()` |
| `experiments/configs/*.yaml` | 实验配置：`agents[].model_name`、`agents[].kwargs` |

### 3. Agent 构造函数参数

```python
# harbor_terminus_2_skills.py
def __init__(
    self,
    logs_dir: Path,
    model_name: str | None = None,
    api_base: str | None = None,   # ← 自定义 API 地址
    api_key: str | None = None,    # ← API 密钥（可选）
    **kwargs,
):
    self._llm = LiteLLM(
        model_name=self._model_name,
        api_base=api_base,   # 传给 LiteLLM
        api_key=api_key,
    )
```

Harbor 从 YAML 的 `kwargs` 中取出 `api_base`、`api_key` 传给构造函数。

---

## 二、接入 vLLM 本地服务

### 1. 启动 vLLM 服务

```bash
# 示例：使用 vLLM 启动本地模型（OpenAI 兼容 API）
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/model \
    --host 0.0.0.0 \
    --port 8000

python -m vllm.entrypoints.openai.api_server --model /data/wyd/models/Qwen2.5-3B-Instruct --port 8000 --gpu-memory-utilization 0.5

CUDA_VISIBLE_DEVICES=3 \
VLLM_ALLOW_LONG_MAX_MODEL_LEN=1 \
python -m vllm.entrypoints.openai.api_server \
  --model /data/wyd/models/Qwen2.5-3B-Instruct \
  --served-model-name Qwen2.5-3B-Instruct \
  --port 8000 \
  --gpu-memory-utilization 0.5 \
  --max-model-len 131072 \
  --hf-overrides '{"rope_scaling":{"rope_type":"yarn","factor":4.0,"original_max_position_embeddings":32768},"max_position_embeddings":131072}'
```

或使用已训练好的 checkpoint：

```bash
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/your/finetuned-checkpoint \
    --host 0.0.0.0 \
    --port 8000
```

vLLM 默认提供 `http://0.0.0.0:8000/v1` 的 OpenAI 兼容端点。

### 2. 实验配置（YAML）

在 `experiments/configs/` 下新建或修改配置，例如 `vllm_local.yaml`：

```yaml
agents:
  - name: terminus-2-skills-vllm
    import_path: libs.terminus_agent.agents.terminus_2.harbor_terminus_2_skills:HarborTerminus2WithSkills
    model_name: hosted_vllm/your-model-name   # 或 openai/your-model-name
    kwargs:
      api_base: "http://localhost:8000/v1"     # vLLM 服务地址
      api_key: "token-abc123"                 # vLLM 若需鉴权则填写，否则可留空或删掉
```

**model_name 说明**：

- `hosted_vllm/<model>`：LiteLLM 的 vLLM 专用前缀
- `openai/<model>`：通用 OpenAI 兼容端点，配合 `api_base` 也可用

vLLM 服务端返回的 `model` 字段需与这里的 `model_name` 后缀一致。若 vLLM 启动时未指定 `--served-model-name`，默认使用 HuggingFace 模型名（如 `meta-llama/Llama-3-8B-Instruct`）。可先 `curl http://localhost:8000/v1/models` 查看实际 model id。

### 2.1 使用 Codex agent 连接 vLLM

如果想测试 Harbor 自带的 `codex` agent，也可以让 Codex CLI 走本地 vLLM 的 OpenAI 兼容接口。

对应配置文件示例：`experiments/configs/vllm_codex_local.yaml`

```yaml
agents:
  - name: codex
    model_name: openai/Qwen2.5-3B-Instruct
```

注意：

- `codex` agent 读取的是环境变量 `OPENAI_BASE_URL`，不是 `agents[].kwargs.api_base`
- `model_name` 最后的模型 id 必须和 `/v1/models` 返回值一致
- 本地 vLLM 对 Codex CLI 的兼容性通常不如 `terminus-2-skills + LiteLLM` 稳定，建议先做最小验证
- `codex` setup 需要在容器内安装 Node.js 和 Codex CLI，建议将 `environment.override_memory_mb` 提高到 `8192` 或更高，并先用 `n_concurrent_trials: 1`

### 3. 环境变量方式（可选）

若希望用环境变量覆盖，可在 agent 中扩展逻辑（当前 `HarborTerminus2WithSkills` 未实现），或通过 Harbor 的 `env` 传入：

```yaml
agents:
  - name: terminus-2-skills-vllm
    import_path: libs.terminus_agent.agents.terminus_2.harbor_terminus_2_skills:HarborTerminus2WithSkills
    model_name: hosted_vllm/your-model-name
    env:
      VLLM_API_BASE: "http://localhost:8000/v1"
    kwargs:
      api_base: "http://localhost:8000/v1"   # 从 env 读取需改 agent 代码
```

### 4. 运行实验

```bash
cd /home/wyd/datasets/skillsbench

# 激活 harbor 环境
source ../../harbor/.venv/bin/activate

export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
export NO_PROXY=localhost,127.0.0.1,host.docker.internal,172.17.0.1,10.10.41.13
export no_proxy=localhost,127.0.0.1,host.docker.internal,172.17.0.1,10.10.41.13
harbor jobs start -c experiments/configs/vllm_local.yaml
```

若使用 `codex` agent，则运行前额外设置：

```bash
export OPENAI_BASE_URL=http://10.10.41.13:8000/v1
export OPENAI_API_KEY=EMPTY
harbor jobs start -c experiments/configs/vllm_codex_local.yaml
```

---

## 三、可训练模型流程

1. **训练**：使用 SimPO 等框架（如 `tasks/simpo-code-reproduction/environment/SimPO/`）训练模型
2. **导出**：得到 checkpoint 或合并后的模型目录
3. **部署**：用 vLLM 加载 checkpoint 并启动 API 服务
4. **评测**：在 skillsbench 中配置 `api_base` + `model_name`，运行 harbor jobs

---

## 四、常见问题

### Q: 如何确认 vLLM 服务正常？

```bash
curl http://localhost:8000/v1/models
```

### Q: Connection refused / Connection timed out / RetryError？

**原因 1：Agent 在 Docker 容器内运行**，`localhost:8000` 指向容器内部，无法访问宿主机上的 vLLM。

- `Connection refused`：目标地址无服务或不可达
- `Connection timed out`：TCP 连接超时（如 600s），常见于 `172.17.0.1` 在容器网络下不可达

改用宿主机实际 IP（vLLM 启动日志中的 `distributed_init_method=tcp://` 后的 IP）：
```yaml
api_base: "http://10.10.41.13:8000/v1"            # 宿主机实际 IP（推荐）
# 或
api_base: "http://172.17.0.1:8000/v1"            # Linux Docker bridge 网关
# 或
api_base: "http://host.docker.internal:8000/v1"  # Docker 20.10+ Linux
```

**原因 2：HTTP_PROXY 拦截了本地请求**。运行前设置：
```bash
export NO_PROXY=localhost,127.0.0.1,host.docker.internal,172.17.0.1,10.10.41.13
```

**原因 3：AgentSetupTimeoutError**。10 个 trial 并行启动时资源争用，`docker exec` 易超时。可：
- 降低 `n_concurrent_trials` 至 2–3
- 增加 `override_setup_timeout_sec: 600`

### Q: 跨机器访问 vLLM？

将 `api_base` 改为 vLLM 所在机器的实际地址，例如：

```yaml
api_base: "http://192.168.1.100:8000/v1"
```

### Q: 使用代理？

```bash
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897
```

### Q: 与 OpenAI 等 API 共存？

不同 agent 可配置不同 `model_name` 和 `kwargs`，例如一个用 OpenAI，一个用 vLLM：

```yaml
agents:
  - name: openai
    model_name: openai/gpt-5.4
    kwargs: {}
  - name: vllm-local
    import_path: libs.terminus_agent.agents.terminus_2.harbor_terminus_2_skills:HarborTerminus2WithSkills
    model_name: hosted_vllm/your-model
    kwargs:
      api_base: "http://localhost:8000/v1"
```
