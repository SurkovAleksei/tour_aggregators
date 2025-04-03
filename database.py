import sqlite3


def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS tours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price TEXT,
        dates TEXT,
        url TEXT UNIQUE,
        location TEXT,
        tour_type TEXT,
        rating TEXT,
        rating_count TEXT,
        image TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """