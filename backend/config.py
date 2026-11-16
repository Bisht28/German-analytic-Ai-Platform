from dotenv import load_dotenv
import os

load_dotenv()

# Hosted Postgres (e.g. Neon) is configured with a single connection string.
# When it is unset, the individual DB_* settings are used (local development).
DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "roadinsight"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:latest")

# Only needed for Ollama Cloud (OLLAMA_URL=https://ollama.com); a local
# Ollama server takes no key.
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
