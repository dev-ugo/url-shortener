"""Application configuration constants."""

import os


DATABASE_URL = "sqlite:////app/data/links.db"
SLUG_LENGTH = 6
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
