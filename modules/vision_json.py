from __future__ import annotations

import base64, io, json, os, re
from typing import Iterable
from PIL import Image


def _secret(name: str):
    try:
        import streamlit as st
        return st.secrets.get(name, "")
    except Exception:
        return os.getenv(name, "")


def _b64(image: Image.Image) -> str:
    b = io.BytesIO(); image.convert("RGB").save(b, format="PNG", optimize=True)
    return base64.b64encode(b.getvalue()).decode()


def _parse(raw: str):
    raw = str(raw or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    # tolerate prose around a JSON object
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        raw = m.group(0)
    return json.loads(raw)


def call_vision_json(prompt: str, images: Iterable[Image.Image], provider: str = "gemini"):
    images = list(images)
    if provider == "gemini":
        from google import genai
        key = os.getenv("GEMINI_API_KEY") or _secret("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        model = os.getenv("GEMINI_MODEL") or _secret("GEMINI_MODEL") or "gemini-3.6-flash"
        client = genai.Client(api_key=key)
        parts = [{"type": "text", "text": prompt}]
        for image in images:
            parts.append({"type": "image", "image_url": "data:image/png;base64," + _b64(image)})
        try:
            r = client.interactions.create(
                model=model,
                input=parts,
                response_format={"type": "text", "mime_type": "application/json"},
            )
            raw = getattr(r, "output_text", None) or str(r)
            return _parse(raw)
        except Exception:
            # SDK-compatible fallback for environments where Interactions image parts differ.
            from google.genai import types
            content = [prompt]
            for image in images:
                bio = io.BytesIO(); image.convert("RGB").save(bio, format="PNG")
                content.append(types.Part.from_bytes(data=bio.getvalue(), mime_type="image/png"))
            r = client.models.generate_content(model=model, contents=content)
            return _parse(getattr(r, "text", None) or str(r))

    from openai import OpenAI
    configs = {
        "openrouter": ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "https://openrouter.ai/api/v1", "openrouter/free"),
        "groq": ("GROQ_API_KEY", "GROQ_MODEL", "https://api.groq.com/openai/v1", "qwen/qwen3.6-27b"),
        "ollama": ("OLLAMA_API_KEY", "OLLAMA_MODEL", _secret("OLLAMA_BASE_URL") or "http://localhost:11434/v1", "gemma3:12b"),
        "openai": ("OPENAI_API_KEY", "OPENAI_MODEL", None, "gpt-5.6-luna"),
    }
    if provider not in configs:
        raise RuntimeError(f"Unsupported vision provider: {provider}")
    key_name, model_name, base_url, default_model = configs[provider]
    key = os.getenv(key_name) or _secret(key_name) or ("ollama" if provider == "ollama" else "")
    if not key:
        raise RuntimeError(f"{key_name} is not configured")
    model = os.getenv(model_name) or _secret(model_name) or default_model
    content = [{"type": "text", "text": prompt}]
    for image in images:
        content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + _b64(image)}})
    kwargs = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0,
    }
    if provider == "openai":
        kwargs["response_format"] = {"type": "json_object"}
    r = OpenAI(api_key=key, base_url=base_url).chat.completions.create(**kwargs)
    return _parse(r.choices[0].message.content)
