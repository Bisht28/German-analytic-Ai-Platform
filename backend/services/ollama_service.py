import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:latest"


# ---------------------------
# OLLAMA CALL WRAPPER
# ---------------------------
def ask_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
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
# CORE EXTRACTION FUNCTION
# ---------------------------
def extract_query_structure(question: str):

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