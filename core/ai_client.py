"""Single entry point for all LLM calls.

Groq is used when GROQ_API_KEY is available (environment variable or
Streamlit secrets); otherwise a local Ollama server is used.
"""
import json
import os
import re

import requests
import streamlit as st

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
TIMEOUT = 120

DEFAULT_SYSTEM = (
    "You are StudyMate, a helpful, accurate AI study assistant for college students."
)


class AIError(Exception):
    """Raised with a message that is safe to show to the student."""


def _secret(name):
    value = os.environ.get(name)
    if value and value.strip():
        return value.strip()
    try:
        value = st.secrets.get(name)
    except Exception:
        return None
    return str(value).strip() if value else None


def provider():
    return "groq" if _secret("GROQ_API_KEY") else "ollama"


def provider_label():
    if provider() == "groq":
        return f"Groq · {GROQ_MODEL}"
    return f"Ollama · {OLLAMA_MODEL}"


def ask_ai(prompt, system=DEFAULT_SYSTEM, history=None, temperature=0.4, max_tokens=4096):
    """Send a prompt to the active provider and return the reply text."""
    messages = [{"role": "system", "content": system}]
    for m in history or []:
        if m.get("role") in ("user", "assistant") and m.get("content"):
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": prompt})

    if provider() == "groq":
        text = _call_groq(messages, temperature, max_tokens)
    else:
        text = _call_ollama(messages, temperature, max_tokens)

    text = (text or "").strip()
    if not text:
        raise AIError("The AI returned an empty response. Please try again.")
    return text


def _call_groq(messages, temperature, max_tokens):
    key = _secret("GROQ_API_KEY")
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,
    }
    if "gpt-oss" in GROQ_MODEL:
        payload["reasoning_effort"] = "low"
    try:
        r = requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        raise AIError("The AI service took too long to respond. Please try again.")
    except requests.exceptions.ConnectionError:
        raise AIError("Could not reach the Groq API. Check your internet connection.")
    except requests.exceptions.RequestException:
        raise AIError("Something went wrong while contacting the AI service.")

    if r.status_code == 401:
        raise AIError("The Groq API key was rejected. Check GROQ_API_KEY in your secrets.")
    if r.status_code == 429:
        raise AIError("Groq rate limit reached. Wait a few seconds and try again.")
    if r.status_code != 200:
        detail = ""
        try:
            detail = r.json().get("error", {}).get("message", "")
        except Exception:
            pass
        raise AIError(f"The AI service returned an error ({r.status_code}). {detail}"[:300])
    try:
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        raise AIError("The AI service sent a response StudyMate could not read.")


def _call_ollama(messages, temperature, max_tokens):
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens, "num_ctx": 6144},
    }
    try:
        r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=TIMEOUT * 2)
    except requests.exceptions.Timeout:
        raise AIError("Ollama took too long to respond. Try again, or use a smaller model.")
    except requests.exceptions.ConnectionError:
        raise AIError(
            f"Could not reach Ollama at {OLLAMA_URL}. Start it with `ollama serve`, "
            f"or set GROQ_API_KEY to use Groq instead."
        )
    except requests.exceptions.RequestException:
        raise AIError("Something went wrong while contacting Ollama.")

    if r.status_code == 404:
        raise AIError(f"Model '{OLLAMA_MODEL}' is not installed. Run `ollama pull {OLLAMA_MODEL}`.")
    if r.status_code != 200:
        raise AIError(f"Ollama returned an error ({r.status_code}).")
    try:
        return r.json()["message"]["content"]
    except Exception:
        raise AIError("Ollama sent a response StudyMate could not read.")


def extract_json(text):
    """Pull the first valid JSON object/array out of an LLM reply."""
    if not text:
        return None
    t = text.strip()
    candidates = [t] + [c.strip() for c in re.findall(r"```(?:json)?\s*(.*?)```", t, re.S)]
    for cand in candidates:
        try:
            return json.loads(cand)
        except Exception:
            pass
    decoder = json.JSONDecoder()
    for m in re.finditer(r"[\[{]", t):
        try:
            obj, _ = decoder.raw_decode(t[m.start():])
        except Exception:
            continue
        if isinstance(obj, (list, dict)):
            return obj
    return None


JSON_SYSTEM = (
    "You are a precise assistant that replies with valid JSON only. "
    "No markdown fences, no commentary before or after the JSON."
)


def ask_json(prompt, validate, attempts=2, temperature=0.5):
    """Ask for JSON, validate it, retry once. Returns (data, error_message)."""
    for i in range(attempts):
        p = prompt
        if i > 0:
            p += (
                "\n\nYour previous reply was not valid or did not follow the required format. "
                "Reply again with ONLY the JSON, exactly as specified."
            )
        try:
            raw = ask_ai(p, system=JSON_SYSTEM, temperature=temperature)
        except AIError as e:
            return None, str(e)
        data = extract_json(raw)
        if data is None:
            continue
        try:
            result = validate(data)
        except Exception:
            result = None
        if result:
            return result, None
    return None, "The AI could not produce a usable result this time. Please try again."
