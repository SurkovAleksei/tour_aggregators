import sqlite3
from sqlite3 import Error

#Cоединение с БД
def create_connection(db_file="tours.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
    return conn

#Создание БД
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
    try:
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
    except Error as e:
        print(f"Ошибка создания таблицы: {e}")

#Добавляет тур в БД
def insert_tour(conn, tour):
    sql = '''INSERT OR IGNORE INTO tours(
                name, price, dates, url, location, 
                tour_type, rating, rating_count, image, description
             ) VALUES(?,?,?,?,?,?,?,?,?,?)'''
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            tour['name'], tour['price'], tour['dates'], tour['url'],
            tour['location'], tour['tour_type'], tour['rating'],
            tour['rating_count'], tour['image'], tour['description']
        ))
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(f"Ошибка вставки данных: {e}")
        return None

#Получение данных из БД
def get_tours(conn, limit=10):
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tours ORDER BY id DESC LIMIT ?", (limit,))
        return cur.fetchall()
    except Error as e:
        print(f"Ошибка получения данных: {e}")
        return []