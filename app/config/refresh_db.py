"""
Database refresh and seeding utilities.

refresh_database() - drops all tables, recreates, and seeds (standalone use).
seed_all()         - idempotent seed called on every app startup.

Run standalone: python -m app.config.refresh_db
"""

import asyncio

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401  # ensures SQLAlchemy model metadata registration
from seed import main as seed_main


def _sync_database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("mysql+aiomysql"):
        return url.replace("mysql+aiomysql", "mysql+pymysql", 1)
    if url.startswith("mysql+asyncmy"):
        return url.replace("mysql+asyncmy", "mysql+pymysql", 1)
    if url.startswith("postgresql+asyncpg"):
        return url.replace("postgresql+asyncpg", "postgresql+psycopg", 1)
    return url


def _build_sync_engine() -> Engine:
    return create_engine(_sync_database_url(), future=True)


def create_tables() -> None:
    engine = _build_sync_engine()
    try:
        Base.metadata.create_all(bind=engine)
    finally:
        engine.dispose()


def seed_all() -> None:
    asyncio.run(seed_main())


def refresh_database() -> None:
    engine = _build_sync_engine()
    try:
        with engine.connect() as conn:
            print("Disabling foreign key checks...")
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0;"))

            table_names = reversed(list(Base.metadata.tables.keys()))
            for table_name in table_names:
                print(f"Dropping table {table_name}...")
                conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`;"))

            print("Re-enabling foreign key checks...")
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
            conn.commit()
    finally:
        engine.dispose()

    create_tables()
    print("All tables recreated successfully.")

    seed_all()
    print("Database refreshed and seeded successfully.")


if __name__ == "__main__":
    refresh_database()
