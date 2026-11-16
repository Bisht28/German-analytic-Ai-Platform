"""Vercel serverless entrypoint: serves the FastAPI backend under /api/*."""
import os
import sys

# The backend uses imports relative to its own folder (config, db, services...).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app  # noqa: E402,F401
