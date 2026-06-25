from db.connection import get_connection


def count_accidents(
    state_code=None,
    district_code=None,
    year=None,
    is_bicycle=None,
    is_pedestrian=None
):
    query = """
        SELECT COUNT(*)
        FROM roadinsight.accidents
        WHERE 1=1
    """

    params = []

    if state_code is not None:
        query += " AND state_code = %s"
        params.append(state_code)

    if district_code is not None:
        query += " AND district_code = %s"
        params.append(district_code)

    if year is not None:
        query += " AND year = %s"
        params.append(year)

    if is_bicycle is not None:
        query += " AND is_bicycle = %s"
        params.append(is_bicycle)

    if is_pedestrian is not None:
        query += " AND is_pedestrian = %s"
        params.append(is_pedestrian)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            count = cur.fetchone()[0]

    return count


def top_fatal_districts(year, limit=5):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    a.district_code,
                    o.district_name,
                    COUNT(*) AS fatal_accidents

                FROM roadinsight.accidents a

                JOIN roadinsight.official_rates o
                    ON a.district_code = o.district_code

                WHERE a.year = %s
                AND a.category = 1

                GROUP BY
                    a.district_code,
                    o.district_name

                ORDER BY fatal_accidents DESC

                LIMIT %s
            """, (year, limit))

            rows = cur.fetchall()

    return [
        {
            "district_code": row[0],
            "district_name": row[1],
            "fatal_accidents": row[2]
        }
        for row in rows
    ]

def get_earliest_year():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT MIN(year)
                FROM roadinsight.accidents
            """)

            return cur.fetchone()[0]


def get_state_availability(state_code):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    MIN(year),
                    MAX(year)
                FROM roadinsight.accidents
                WHERE state_code = %s
            """, (state_code,))

            min_year, max_year = cur.fetchone()

    return {
        "from_year": min_year,
        "to_year": max_year
    }


def get_personal_injury_accidents(state_code, year):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT COUNT(*)
                FROM roadinsight.accidents
                WHERE state_code = %s
                AND year = %s
                AND category IN (2, 3)
            """, (state_code, year))

            return cur.fetchone()[0]


def get_zero_accident_municipalities_count(state_code, year):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT r.municipality_code
                    FROM roadinsight.regions r
                    WHERE r.state_code = %s
                    AND NOT EXISTS (
                        SELECT 1
                        FROM roadinsight.accidents a
                        WHERE a.municipality_code = r.municipality_code
                        AND a.year = %s
                    )
                ) x
            """, (state_code, year))

            return cur.fetchone()[0]
        
from db.connection import get_connection


def resolve_location(name: str, limit: int = 5):
    """
    STRICT location resolver using DB only.
    No guessing. No indexing. No preprocessing.
    """

    if not name:
        return []

    pattern = f"%{name.lower()}%"

    with get_connection() as conn:
        with conn.cursor() as cur:

            # -------------------------
            # 1. Try district match first
            # -------------------------
            cur.execute("""
                SELECT district_code, name
                FROM roadinsight.regions
                WHERE LOWER(name) LIKE %s
                LIMIT %s
            """, (pattern, limit))

            rows = cur.fetchall()

            if rows:
                return [
                    {
                        "type": "district",
                        "code": r[0],
                        "name": r[1]
                    }
                    for r in rows
                ]

            # -------------------------
            # 2. Fallback: state match
            # -------------------------
            cur.execute("""
                SELECT DISTINCT state_code, name
                FROM roadinsight.regions
                WHERE LOWER(name) LIKE %s
                LIMIT %s
            """, (pattern, limit))

            rows = cur.fetchall()

            return [
                {
                    "type": "state",
                    "code": r[0],
                    "name": r[1]
                }
                for r in rows
            ]

# ... (Keep all your existing functions exactly as they are) ...

def get_zero_accident_municipalities(state_code, year):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT r.name
                FROM roadinsight.regions r
                WHERE r.state_code = %s
                AND NOT EXISTS (
                    SELECT 1
                    FROM roadinsight.accidents a
                    WHERE a.municipality_code = r.municipality_code
                    AND a.year = %s
                )
                ORDER BY r.name ASC
            """, (state_code, year))
            
            rows = cur.fetchall()
            
    # Returns a clean list of strings: ["Name1", "Name2", ...]
    return [row[0] for row in rows]