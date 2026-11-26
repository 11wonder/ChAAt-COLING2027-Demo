# -*- coding: utf-8 -*-
"""OpenAI 兼容接口封装（DeepSeek / 通义千问 / OpenAI / Ollama 通用）。"""

import requests
from openai import OpenAI


def build_client(base_url, api_key, timeout=90.0):
    """按 OpenAI 兼容协议构造客户端；base_url 为空时默认连 OpenAI 官方。"""
    key = (api_key or "").strip() or "not-needed"
    url = (base_url or "").strip() or None
    return OpenAI(base_url=url, api_key=key, timeout=timeout, max_retries=0)


def chat(
    client,
    model,
    user_text,
    system=None,
    temperature=0.0,
    max_tokens=1024,
    extra_body=None,
):
    """单轮对话，返回文本内容。"""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_text})
    base = {"model": model, "messages": messages}
    if temperature is not None:
        base["temperature"] = temperature
    if "dashscope" in str(getattr(client, "base_url", "") or ""):
        # DashScope 默认可能开启联网检索；显式关闭。
        base["extra_body"] = {"enable_search": False}
    if extra_body:
        base["extra_body"] = {**base.get("extra_body", {}), **extra_body}
    try:
        resp = client.chat.completions.create(**base, max_tokens=max_tokens)
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "max_tokens" in msg and "max_completion_tokens" in msg:
            try:
                resp = client.chat.completions.create(
                    **base, max_completion_tokens=max_tokens
                )
            except Exception as exc2:  # noqa: BLE001
                if "temperature" not in str(exc2):
                    raise
                base.pop("temperature", None)
                resp = client.chat.completions.create(
                    **base, max_completion_tokens=max_tokens
                )
        elif "temperature" in msg:
            base.pop("temperature", None)
            resp = client.chat.completions.create(**base, max_tokens=max_tokens)
        else:
            raise
    return (resp.choices[0].message.content or "").strip()


def build_answer_prompt(q):
    """把题目转成发给模型的指令。"""
    if q.get("type") == "fill_blank":
        return q["question"] + "\n请只输出答案本身，不要解释，不要加标点。"
    if q.get("type") == "multiple_select":
        opts = "\n".join(q.get("options", []))
        return (
            q["question"]
            + "\n"
            + opts
            + "\n请只输出所有正确选项字母（例如 AC），不要解释。"
        )
    opts = "\n".join(q.get("options", []))
    return q["question"] + "\n" + opts + "\n请只输出选项字母（例如 A）。"


def ollama_chat(
    base_url,
    model,
    user_text,
    system=None,
    temperature=0.0,
    max_tokens=256,
    timeout=120,
):
    """走 Ollama 原生 /api/chat，并显式关闭 thinking。

    OpenAI 兼容端点的 think 参数不生效，思考模型会把 token 全花在
    reasoning 上、content 为空，因此本地模型单独走原生接口。
    """
    host = (base_url or "http://localhost:11434").rstrip("/")
    if host.endswith("/v1"):
        host = host[:-3]
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user_text})
    resp = requests.post(
        host + "/api/chat",
        json={
            "model": model,
            "messages": messages,
            "think": False,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return (data.get("message", {}).get("content") or "").strip()
