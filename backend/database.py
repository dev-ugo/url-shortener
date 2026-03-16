"""Database engine and schema initialization helpers."""

from sqlmodel import SQLModel, create_engine

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)


def create_tables() -> None:
    """Create all SQLModel tables if they do not exist."""
    SQLModel.metadata.create_all(engine)
