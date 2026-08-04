# Math agent image — standalone build from ubuntu:24.04.
# tasks_spec.json is NOT baked into the image — Harbor injects it at runtime.
FROM ubuntu:24.04

ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG http_proxy
ARG https_proxy
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}

RUN rm -f /root/tasks_spec.json

ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:/usr/local/bin:${PATH}"

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl ca-certificates bash procps xz-utils \
        python3 python3-pip python3-numpy python3-sympy \
        nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Preinstall Claude Code to avoid first-run downloads in trial runtime.
RUN npm config set registry https://registry.npmmirror.com \
    && npm install -g @anthropic-ai/claude-code@2.1.140 \
    && npm install -g @openai/codex \
    && claude --version \
    && codex --version

RUN python3 -m pip install --break-system-packages --no-cache-dir \
      -i https://pypi.tuna.tsinghua.edu.cn/simple \
        pandas==2.2.3 \
        numpy==1.26.4 \
        scipy==1.14.1 \
        statsmodels==0.14.4 \
        openpyxl==3.1.5 \
        anthropic>=0.40.0 \
        openai>=1.0.0 \
        litellm>=1.40.0 \
        requests==2.32.3 \
        pytest==8.4.1


WORKDIR /root

RUN mkdir -p /app /logs/verifier /root/data /verifier /app/workspace









COPY claude-settings.json /root/.claude/settings.json

COPY skills /root/.claude/skills
COPY skills /root/.terminus/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
