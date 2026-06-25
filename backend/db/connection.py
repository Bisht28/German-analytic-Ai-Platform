from psycopg_pool import ConnectionPool
from config import DB_CONFIG

DATABASE_URL = (
    f"host={DB_CONFIG['host']} "
    f"port={DB_CONFIG['port']} "
    f"dbname={DB_CONFIG['dbname']} "
    f"user={DB_CONFIG['user']} "
    f"password={DB_CONFIG['password']}"
)

pool = ConnectionPool(conninfo=DATABASE_URL)

def get_connection():
    return pool.connection()