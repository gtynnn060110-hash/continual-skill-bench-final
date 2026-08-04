"""Environment helpers for Claude Code agents (Anthropic API, OpenRouter, Bedrock)."""

from __future__ import annotations

import os

OPENROUTER_BASE_URL = "https://openrouter.ai/api"


def is_openrouter_env(env: dict[str, str]) -> bool:
    """True when exec env should route Claude Code through OpenRouter."""
    flag = env.get("HARBOR_USE_OPENROUTER", "").strip().lower()
    if flag in ("1", "true", "yes"):
        return True

    base = env.get("ANTHROPIC_BASE_URL", "").strip().rstrip("/")
    if base.startswith("https://openrouter.ai"):
        return True

    return bool(env.get("OPENROUTER_API_KEY", "").strip())


def is_openrouter_mode() -> bool:
    """True when Claude Code should talk to OpenRouter's Anthropic-compatible API."""
    return is_openrouter_env(dict(os.environ))


def resolve_openrouter_api_key() -> str:
    return (
        os.environ.get("OPENROUTER_API_KEY", "").strip()
        or os.environ.get("ANTHROPIC_AUTH_TOKEN", "").strip()
    )


def claude_code_auth_env(*, use_bedrock: bool = False) -> dict[str, str]:
    """Return auth-related env vars for Claude Code inside Harbor containers."""
    if use_bedrock:
        return {}

    env: dict[str, str] = {}

    if is_openrouter_mode():
        or_key = resolve_openrouter_api_key()
        if or_key:
            # OpenRouter docs: use AUTH_TOKEN and explicitly blank ANTHROPIC_API_KEY.
            env["ANTHROPIC_AUTH_TOKEN"] = or_key
            env["OPENROUTER_API_KEY"] = or_key
        base = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
        env["ANTHROPIC_BASE_URL"] = base or OPENROUTER_BASE_URL
        # Claude Code checks ANTHROPIC_API_KEY first; must clear it for OpenRouter.
        env["ANTHROPIC_API_KEY"] = ""
        return env

    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get(
        "ANTHROPIC_AUTH_TOKEN"
    )
    if api_key:
        env["ANTHROPIC_API_KEY"] = api_key

    base = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
    if base:
        env["ANTHROPIC_BASE_URL"] = base

    return env


def openrouter_litellm_model(model: str) -> str:
    """Map a Harbor judge model name to LiteLLM's OpenRouter provider prefix."""
    if not is_openrouter_mode():
        return model
    if model.startswith("openrouter/"):
        return model
    if "/" in model:
        return f"openrouter/{model}"
    return f"openrouter/anthropic/{model}"


def scrub_claude_exec_env(env: dict[str, str] | None) -> dict[str, str] | None:
    """Drop empty env values; keep ANTHROPIC_API_KEY='' when using OpenRouter."""
    if not env:
        return env
    openrouter = is_openrouter_env(env)
    scrubbed: dict[str, str] = {}
    for key, value in env.items():
        if value or (openrouter and key == "ANTHROPIC_API_KEY"):
            scrubbed[key] = value
    return scrubbed


def finalize_claude_exec_env(env: dict[str, str] | None) -> dict[str, str] | None:
    """Normalize auth env after merging Harbor --ae overrides."""
    if not env:
        return env

    if not is_openrouter_env(env):
        return scrub_claude_exec_env(env)

    finalized = dict(env)
    or_key = (
        finalized.get("OPENROUTER_API_KEY", "").strip()
        or finalized.get("ANTHROPIC_AUTH_TOKEN", "").strip()
    )
    if or_key:
        finalized["OPENROUTER_API_KEY"] = or_key
        finalized["ANTHROPIC_AUTH_TOKEN"] = or_key
    finalized.setdefault("ANTHROPIC_BASE_URL", OPENROUTER_BASE_URL)
    finalized["ANTHROPIC_API_KEY"] = ""
    return scrub_claude_exec_env(finalized)


def judge_runtime_env_exports() -> list[tuple[str, str]]:
    """Env vars to inject when running the inline sequential judge script."""
    exports: list[tuple[str, str]] = []

    if is_openrouter_mode():
        or_key = resolve_openrouter_api_key()
        if or_key:
            exports.append(("OPENROUTER_API_KEY", or_key))
            exports.append(("ANTHROPIC_AUTH_TOKEN", or_key))
        return exports

    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"):
        value = os.environ.get(name, "").strip()
        if value:
            exports.append((name, value))
    return exports
