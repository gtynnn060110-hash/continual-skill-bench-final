FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    curl git wget nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Preinstall Claude Code to avoid downloads inside the container
RUN npm config set registry https://registry.npmmirror.com \
    && npm install -g @anthropic-ai/claude-code@2.1.140 \
    && npm install -g @openai/codex \
    && claude --version \
    && codex --version

# optional: use mirror to speed up docker build
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    pandas==2.2.3 \
    numpy==1.26.4 \
    scipy==1.14.1 \
    statsmodels==0.14.4 \
    openpyxl==3.1.5 \
    xlrd==2.0.1 \
    pdfplumber==0.11.4 \
    python-docx==1.1.2 \
    anthropic>=0.40.0 \
    openai>=1.0.0 \
    litellm>=1.40.0 \
    requests==2.32.3

WORKDIR /root

RUN mkdir -p /app /app/workspace /logs/verifier /root/data

COPY data/ /root/data/

# Copy claw-bench input data (office-100) into /app/workspace/ so agents
# find input files at workspace/ and write output files there too.
RUN cp /root/data/* /app/workspace/


# Copy base skills (create-skill, modify-skill always available)
COPY skills /root/.claude/skills
COPY skills /root/.terminus/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills
