from services.analytics_service import (
    get_earliest_year,
    count_accidents,
    get_state_availability,
    get_personal_injury_accidents,
    get_zero_accident_municipalities_count,
    get_zero_accident_municipalities,
    top_fatal_districts,
    resolve_location
)

from db.repository import resolve_district_code


GERMAN_STATE_CODES = {
    "schleswig-holstein": "01",
    "hamburg": "02",
    "lower saxony": "03",
    "bremen": "04",
    "north rhine-westphalia": "05",
    "nrw": "05",
    "hesse": "06",
    "rhineland-palatinate": "07",
    "baden-württemberg": "08",
    "baden-wurttemberg": "08",
    "bavaria": "09",
    "saarland": "10",
    "berlin": "11",
    "brandenburg": "12",
    "mecklenburg-western pomerania": "13",
    "saxony": "14",
    "saxony-anhalt": "15",
    "thuringia": "16"
}


def execute_query_structure(structure):

    operation = structure.get("operation")
    filters = structure.get("filters", {})
    options = structure.get("options", {})

    # -------------------------
    # EARLIEST YEAR
    # -------------------------
    if operation == "earliest_year":
        return get_earliest_year()

    # -------------------------
    # STATE AVAILABILITY
    # -------------------------
    if operation == "state_availability":

        state = filters.get("state")

        if not state:
            return "STATE_MISSING"

        state_code = GERMAN_STATE_CODES.get(state.lower())

        if not state_code:
            return f"STATE_NOT_SUPPORTED: {state}"

        return get_state_availability(state_code)

    # -------------------------
    # PERSONAL INJURY ACCIDENTS
    # -------------------------
    if operation == "personal_injury_accidents":
        state = filters.get("state")
        year = filters.get("year")
        
        if not state:
            return "STATE_MISSING"
        if not year:
            return "YEAR_MISSING"

        state_code = GERMAN_STATE_CODES.get(state.lower())
        if not state_code:
            return f"STATE_NOT_SUPPORTED: {state}"

        return get_personal_injury_accidents(state_code=state_code, year=year)

    # -------------------------
    # ZERO ACCIDENT MUNICIPALITIES
    # -------------------------
    if operation == "zero_accident_municipalities":

        state = filters.get("state")

        if not state:
            return "STATE_MISSING"

        state_code = GERMAN_STATE_CODES.get(state.lower())

        if not state_code:
            return f"STATE_NOT_SUPPORTED: {state}"

        return get_zero_accident_municipalities(
            state_code=state_code,
            year=filters.get("year")
        )

    # -------------------------
    # TOP FATAL DISTRICTS
    # -------------------------
    if operation == "top_fatal_districts":

        year = filters.get("year")

        if not year:
            return "YEAR_MISSING"

        limit = options.get("limit") or 5

        return top_fatal_districts(
            year=year,
            limit=limit
        )

    # -------------------------
    # COUNT ACCIDENTS (STRICT RESOLVER)
    # -------------------------
    if operation == "count_accidents":

        state_code = None
        district_code = None

        state = filters.get("state")
        district = filters.get("district")

        # 🛠️ FIX FOR ISSUE 2: If Berlin/Hamburg is provided as state, isolate to State Code
        if state and state.lower() in ["berlin", "hamburg", "bremen"]:
            state_code = GERMAN_STATE_CODES.get(state.lower())
        else:
            # STRICT STATE RESOLUTION FOR GENERAL STATES
            if state:
                candidates = resolve_location(state)
                state_matches = [c for c in candidates if c["type"] == "state"]

                if len(state_matches) == 1:
                    state_code = state_matches[0]["code"]
                elif len(state_matches) > 1:
                    return {
                        "type": "ambiguity",
                        "field": "state",
                        "candidates": state_matches
                    }

            # STRICT DISTRICT RESOLUTION
            if district:
                candidates = resolve_location(district)
                district_matches = [c for c in candidates if c["type"] == "district"]

                if len(district_matches) == 1:
                    district_code = district_matches[0]["code"]
                elif len(district_matches) > 1:
                    return {
                        "type": "ambiguity",
                        "field": "district",
                        "candidates": district_matches
                    }

        return count_accidents(
            state_code=state_code,
            district_code=district_code,
            year=filters.get("year"),
            is_pedestrian=1 if filters.get("is_pedestrian") else None,
            is_bicycle=1 if filters.get("is_bicycle") else None
        )

    # -------------------------
    # FALLBACK
    # -------------------------
    return f"OPERATION_NOT_SUPPORTED: {operation}"