import psycopg2

import Config


def get_db_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )


def Create_all_tables():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            print("Проверка таблиц...")

            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS hour_rate (
                        id SERIAL PRIMARY KEY,
                        rate INTEGER               
                    );''')
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (  
                        id SERIAL PRIMARY KEY,          
                        name VARCHAR(20),
                        hour_id INTEGER REFERENCES hour_rate(id)
                    );''')

            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR(100),
                        Post_id INTEGER REFERENCES posts(id),
                        telegram_chat_id BIGINT UNIQUE,
                        unique_key TEXT UNIQUE
                    );''')
        conn.commit()
        print("Таблицы созданы либо существуют")
    finally:
        conn.close()


def Add_User(full_name, operator_type, chat_id, hashed_key):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT id FROM posts WHERE name = '{operator_type}'")
            Post_id = cursor.fetchone()

            cursor.execute(
                "INSERT INTO users (full_name, Post_id, telegram_chat_id, unique_key) VALUES (%s, %s, %s, %s)",
                (full_name, Post_id, chat_id, hashed_key)
            )


def have_TG_id(chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT telegram_chat_id FROM users WHERE telegram_chat_id = %s", (chat_id,))
            if cursor.fetchone() is not None:
                return True
            else:
                return False


def get_operator_type_by_id(chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT Post_id FROM users WHERE telegram_chat_id = %s", (chat_id,))
            user = cursor.fetchone()
            if user:
                cursor.execute(
                    "SELECT name FROM posts WHERE id = (SELECT Post_id FROM users WHERE telegram_chat_id = %s)",
                    (chat_id,))
                return cursor.fetchone()


def get_user_by_uid(UID):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT unique_key, Post_id FROM users WHERE unique_key = %s", (UID,))
            user = cursor.fetchone()
            if user:
                unique_key, Post_id = user
                cursor.execute(f"SELECT name FROM posts WHERE id = {Post_id}")
                return cursor.fetchone()
            else:
                return None


def update_user_chat_id_by_UID(UID, chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET telegram_chat_id = %s WHERE unique_key = %s", (chat_id, UID))
            conn.commit()
