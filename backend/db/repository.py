from db.connection import get_connection


def get_system_stats():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT COUNT(*)
                FROM roadinsight.accidents
            """)
            total_accidents = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(DISTINCT state_code)
                FROM roadinsight.accidents
            """)
            states = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(DISTINCT district_code)
                FROM roadinsight.accidents
            """)
            districts = cur.fetchone()[0]

            cur.execute("""
                SELECT COUNT(*)
                FROM roadinsight.regions
            """)
            municipalities = cur.fetchone()[0]

            cur.execute("""
                SELECT MIN(year), MAX(year)
                FROM roadinsight.accidents
            """)
            min_year, max_year = cur.fetchone()

    return {
        "total_accidents": total_accidents,
        "states": states,
        "districts": districts,
        "municipalities": municipalities,
        "years": [min_year, max_year]
    }


def resolve_district_code(location_name: str):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT district_code
                FROM roadinsight.regions
                WHERE LOWER(name) = LOWER(%s)
                LIMIT 1
            """, (location_name,))

            row = cur.fetchone()

            if row:
                return row[0]

            cur.execute("""
                SELECT district_code
                FROM roadinsight.regions
                WHERE LOWER(name) = LOWER(%s)
                LIMIT 1
            """, (f"{location_name}, Stadt",))

            row = cur.fetchone()

            if row:
                return row[0]

    return None