from psycopg_pool import ConnectionPool
from config import DATABASE_URL, DB_CONFIG

if DATABASE_URL:
    # Hosted database, reached from short-lived serverless instances:
    # hold no idle connections and keep the per-instance cap small.
    pool = ConnectionPool(conninfo=DATABASE_URL, min_size=0, max_size=3)
else:
    pool = ConnectionPool(
        conninfo=(
            f"host={DB_CONFIG['host']} "
            f"port={DB_CONFIG['port']} "
            f"dbname={DB_CONFIG['dbname']} "
            f"user={DB_CONFIG['user']} "
            f"password={DB_CONFIG['password']}"
        )
    )


def get_connection():
    return pool.connection()
