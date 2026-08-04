FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y \
    curl git wget nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Preinstall Claude Code to avoid downloads inside the container
RUN npm config set registry https://registry.npmmirror.com \
    && npm install -g @anthropic-ai/claude-code@2.1.140 \
    && npm install -g @openai/codex \
    && claude --version \
    && codex --version

#optional: use mirror to speed up docker build
RUN pip install --no-cache-dir \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    pandas==2.2.3 \
    numpy==1.26.4 \
    scipy==1.14.1 \
    statsmodels==0.14.4 \
    openpyxl==3.1.5 \
    xlrd==2.0.1 \
    pdfplumber==0.11.4 \
    anthropic>=0.40.0 \
    openai>=1.0.0 \
    requests==2.32.3 \
    litellm>=1.40.0 \
    pytest==8.4.1

WORKDIR /root

RUN mkdir -p /app /logs/verifier /root/data /verifier /app/workspace

COPY data/stock_returns.csv /root/data/
COPY data/financials.csv /root/data/
COPY data/portfolio_returns.csv /root/data/
COPY data/balance_sheet.csv /root/data/
COPY data/income_statement.csv /root/data/
COPY data/earnings_q1.txt /root/data/
COPY data/earnings_q2.txt /root/data/
COPY data/exchange_rates.csv /root/data/

COPY data/hon.json /root/data/
COPY data/btc.json /root/data/
COPY data/uvv.json /root/data/
COPY data/jnj.json /root/data/
COPY data/msft.json /root/data/
COPY data/nflx.json /root/data/

COPY setup_claw.sh /root/setup_claw.sh
RUN bash /root/setup_claw.sh /app/workspace

COPY claude-settings.json /root/.claude/settings.json

COPY skills /root/.claude/skills
COPY skills /root/.terminus/skills
COPY skills /root/.codex/skills
COPY skills /root/.opencode/skill
COPY skills /root/.goose/skills
COPY skills /root/.factory/skills
COPY skills /root/.agents/skills
COPY skills /root/.gemini/skills

# tasks_spec.json stays on the Harbor host only (judge env injection + verifier upload).
