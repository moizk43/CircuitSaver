"""
init_db.py
Run this ONCE to create all tables in your Supabase PostgreSQL database.
"""

from app.core.database import engine, Base
from app.db import models


def init_db():
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")


if __name__ == "__main__":
    init_db()