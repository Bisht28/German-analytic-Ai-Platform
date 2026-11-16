import json
import os
import re

import requests

from config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_API_KEY


# ---------------------------
# OLLAMA CALL WRAPPER
# ---------------------------
def ask_ollama(prompt: str) -> str:
    # A local Ollama server needs no key; Ollama Cloud (https://ollama.com)
    # serves the same API and authenticates with a bearer key.
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else {}

    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        headers=headers,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,

            # IMPORTANT FIX:
            # keep slight randomness for reasoning stability
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "repeat_penalty": 1.05
            }
        },
        timeout=120
    )

    response.raise_for_status()
    data = response.json()
    return data["response"].strip()


# ---------------------------
# RULE-BASED PARSER (NO LLM)
# ---------------------------
# Used where no Ollama server is reachable (the hosted deployment).
# QUERY_PARSER=rules|ollama overrides the default.
QUERY_PARSER = os.getenv("QUERY_PARSER", "rules" if os.getenv("VERCEL") else "ollama")

# Spellings found in questions -> the state name intent_service expects.
# Longer spellings are tried first so "Lower Saxony" is not read as "Saxony".
STATE_ALIASES = {
    "schleswig-holstein": "Schleswig-Holstein",
    "hamburg": "Hamburg",
    "lower saxony": "Lower Saxony",
    "niedersachsen": "Lower Saxony",
    "bremen": "Bremen",
    "north rhine-westphalia": "North Rhine-Westphalia",
    "north rhine westphalia": "North Rhine-Westphalia",
    "nordrhein-westfalen": "North Rhine-Westphalia",
    "nrw": "North Rhine-Westphalia",
    "hesse": "Hesse",
    "hessen": "Hesse",
    "rhineland-palatinate": "Rhineland-Palatinate",
    "rheinland-pfalz": "Rhineland-Palatinate",
    "baden-württemberg": "Baden-Württemberg",
    "baden-wurttemberg": "Baden-Württemberg",
    "bavaria": "Bavaria",
    "bayern": "Bavaria",
    "saarland": "Saarland",
    "berlin": "Berlin",
    "brandenburg": "Brandenburg",
    "mecklenburg-western pomerania": "Mecklenburg-Western Pomerania",
    "mecklenburg-vorpommern": "Mecklenburg-Western Pomerania",
    "saxony-anhalt": "Saxony-Anhalt",
    "sachsen-anhalt": "Saxony-Anhalt",
    "saxony": "Saxony",
    "sachsen": "Saxony",
    "thuringia": "Thuringia",
    "thüringen": "Thuringia",
}


def _find_state(text: str):
    for alias in sorted(STATE_ALIASES, key=len, reverse=True):
        if re.search(rf"(?<![\w-]){re.escape(alias)}(?![\w-])", text):
            return STATE_ALIASES[alias]
    return None


def _find_place(question: str):
    """The capitalised place name after "in", e.g. "in Dresden in 2024"."""
    for match in re.finditer(
        r"\bin\s+((?:[A-ZÄÖÜ][\wäöüß.\-]*)(?:\s+[A-ZÄÖÜ][\wäöüß.\-]*)*)",
        question
    ):
        place = match.group(1).strip(" .?!,")
        if place and place.lower() != "germany":
            return place
    return None


def extract_with_rules(question: str):

    text = question.lower()
    structure = fallback()
    filters = structure["filters"]

    state = _find_state(text)
    filters["state"] = state

    year = re.search(r"\b(20\d{2})\b", text)
    if year:
        filters["year"] = int(year.group(1))

    limit = re.search(r"\btop\s+(\d+)\b", text)
    if limit:
        structure["options"]["limit"] = int(limit.group(1))

    if "pedestrian" in text:
        filters["is_pedestrian"] = True
    if re.search(r"bicycle|cycling|cyclist|\bbike", text):
        filters["is_bicycle"] = True

    if re.search(r"\b(zero|no)\b", text) and "municipalit" in text:
        operation = "zero_accident_municipalities"
    elif "personal injury" in text:
        operation = "personal_injury_accidents"
    elif "fatal" in text and re.search(r"\b(top|highest|most)\b", text):
        operation = "top_fatal_districts"
    elif state and re.search(r"availab|from which year|since when|since which year", text):
        operation = "state_availability"
    elif re.search(r"earliest|first year|oldest", text):
        operation = "earliest_year"
    elif "accident" in text and re.search(r"how many|number of|count|total", text):
        operation = "count_accidents"
        if not state:
            filters["district"] = _find_place(question)
    else:
        return structure

    structure["operation"] = operation
    return structure


# ---------------------------
# CORE EXTRACTION FUNCTION
# ---------------------------
def extract_query_structure(question: str):

    if QUERY_PARSER == "rules":
        return extract_with_rules(question)

    prompt = f"""
You are a STRICT JSON generator.

ABSOLUTE RULES:
- Output MUST be valid JSON
- Output MUST contain "operation"
- Output MUST match schema exactly
- NEVER output arrays at top-level
- NEVER rename keys
- NEVER return extra fields
- NEVER return partial structures

VALID OPERATIONS ONLY:
- earliest_year
- count_accidents
- personal_injury_accidents
- top_fatal_districts
- state_availability
- zero_accident_municipalities

SCHEMA:
{{
  "operation": "",
  "filters": {{
    "state": null,
    "district": null,
    "year": null,
    "is_pedestrian": null,
    "is_bicycle": null,
    "category": null
  }},
  "options": {{
    "limit": null
  }}
}}

HARD RULES:
1. NEVER output "top_fatal_districts": [...]
2. NEVER output arrays anywhere except inside "filters" or "options"
3. NEVER output "result" or custom keys
4. ALWAYS return full JSON object
5. If the question contains the exact phrase "personal injury", you MUST set "operation" to "personal_injury_accidents". Do not use "count_accidents".
6. DO NOT set "is_pedestrian": true unless the question explicitly contains the word "pedestrian".
7. DO NOT set "is_bicycle": true unless the question explicitly contains the word "bicycle" or "cycling".

QUESTION:
{question}

OUTPUT:
"""

    response = ask_ollama(prompt)

    try:
        start = response.find("{")
        end = response.rfind("}") + 1

        if start != -1 and end > start:
            response = response[start:end]

        parsed = json.loads(response)

        # ---------------------------
        # 🔥 HARD FIX LAYER (UNTOUCHED LOGIC)
        # ---------------------------

        # Fix missing operation
        if not isinstance(parsed, dict) or "operation" not in parsed:
            return fallback()

        # Force schema shape (prevents drift)
        normalized = {
            "operation": parsed.get("operation", "unknown"),
            "filters": {
                "state": parsed.get("filters", {}).get("state"),
                "district": parsed.get("filters", {}).get("district"),
                "year": parsed.get("filters", {}).get("year"),
                "is_pedestrian": parsed.get("filters", {}).get("is_pedestrian"),
                "is_bicycle": parsed.get("filters", {}).get("is_bicycle"),
                "category": parsed.get("filters", {}).get("category"),
            },
            "options": {
                "limit": parsed.get("options", {}).get("limit")
            }
        }

        # 🔥 CRITICAL NORMALIZATION FIXES

        # normalize bad states (Berlin case, NRW, etc)
        if normalized["filters"]["state"]:
            normalized["filters"]["state"] = normalized["filters"]["state"].strip()

        return normalized

    except Exception:
        return fallback()


def fallback():
    return {
        "operation": "unknown",
        "filters": {
            "state": None,
            "district": None,
            "year": None,
            "is_pedestrian": None,
            "is_bicycle": None,
            "category": None
        },
        "options": {
            "limit": None
        }
    }