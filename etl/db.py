"""Database connection, from environment variables (see .env.example)."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()

SCHEMA = "project"


def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "envdb"),
    )
    # search_path is set on every connection. Running "SET search_path" once
    # is not enough: each new connection starts again from the default schema.
    return create_engine(url, connect_args={"options": f"-csearch_path={SCHEMA},public"})
