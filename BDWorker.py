from datetime import date

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
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Percent_Rate(
                        Id serial PRIMARY KEY,
                        Count integer NOT NULL
                    );''')
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Rental_point(
                        Id serial PRIMARY KEY,
                        Name VARCHAR(100) NOT NULL,
                        Rate_Id integer REFERENCES Percent_Rate(Id),
                        Owner_id integer REFERENCES users(id),
                        Terminal VARCHAR(100),
                        Merchant VARCHAR(100)
                    );''')
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS Schedules(
                        Id serial PRIMARY KEY,
                        work_date date NOT NULL,
                        Point_id integer NULL REFERENCES Rental_point(Id),
                        User_id integer REFERENCES users (Id),
                        isWork boolean,
                        hour_count smallint NOT NULL DEFAULT 0
                    );''')
            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS day_rezult
                    (
                        id serial PRIMARY KEY,
                        date date NOT NULL,
                        point_id serial REFERENCES Rental_point(id),
                        cash integer NOT NULL,
                        non_cash integer NOT NULL,
                        count_of_checks integer NOT NULL,
                        refund integer NOT NULL,
                        how_long_point_iswork integer,
                        app_result integer DEFAULT 0                        
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
            return True if cursor.fetchone() else False


def get_operator_type_by_id(chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM posts WHERE id = (SELECT Post_id FROM users WHERE telegram_chat_id = %s)", (chat_id,))
            post = cursor.fetchone()
            return post[0] if post else None


def get_operator_by_uid(UID):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM posts WHERE id = (SELECT Post_id FROM users WHERE unique_key = %s);", (UID,))
            post = cursor.fetchone()
            return post[0] if post else None

def get_operator_by_id(id : int):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT full_name FROM users WHERE id = %s", (id,))
            return cursor.fetchone()


def update_user_chat_id_by_UID(UID, chat_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE users SET telegram_chat_id = %s WHERE unique_key = %s", (chat_id, UID))
            conn.commit()


def get_schedule_by_tg_id(tg_id, month_number):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT schedules.work_date,schedules.iswork, users.full_name, schedules.point_id, schedules.hour_count
                FROM schedules, users WHERE schedules.user_id = 
                (SELECT Id FROM users WHERE telegram_chat_id = %s)
                AND
                users.telegram_chat_id = %s
                AND
                extract(month from schedules.work_date) = %s
            ''', (tg_id, tg_id, month_number))
            return cursor.fetchall()

def get_schedule_by_tg_id_and_date(tg_id, date: date):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT schedules.work_date,schedules.iswork, users.full_name, schedules.point_id, schedules.hour_count
                    FROM schedules, users WHERE schedules.user_id = 
                    (SELECT Id FROM users WHERE telegram_chat_id = %s)
                    AND
                    users.telegram_chat_id = %s
                    AND
                    schedules.work_date = %s;;
                ''', (tg_id, tg_id, date.isoformat()))
            return cursor.fetchone()

def update_schedule_by_tg_id_and_date(tg_id, date:date, isWork):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(f'''
                UPDATE schedules SET point_id = NULL, iswork = %s WHERE 
                user_id = (SELECT Id FROM users WHERE telegram_chat_id = %s)
                and work_date = %s;''', ( isWork, tg_id, date.isoformat()))
            conn.commit()

def add_schedule_by_tg_id_and_date(tg_id, date:date, isWork):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(f'''
                INSERT INTO schedules(work_date, point_id, user_id, iswork)
                VALUES(%s, NULL, (SELECT Id FROM users WHERE telegram_chat_id = %s), %s);
            ''', (date.isoformat(), tg_id, isWork))
            conn.commit()

def get_rental_point_by_id(rental_point_id : int):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT name FROM rental_point WHERE id = %s
            ''', (rental_point_id,))
            return cursor.fetchone()[0]

def get_all_users():
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT users.id, users.full_name, posts.name, hour_rate.rate 
                FROM users 
                LEFT JOIN posts ON users.Post_id = posts.id 
                LEFT JOIN hour_rate ON posts.hour_id = hour_rate.id
            ''')
            return cursor.fetchall()

def get_user_info_by_id(user_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT users.full_name, posts.name, hour_rate.rate 
                FROM users 
                LEFT JOIN posts ON users.Post_id = posts.id 
                LEFT JOIN hour_rate ON posts.hour_id = hour_rate.id
                WHERE users.id = %s
            ''', (user_id,))
            return cursor.fetchone()

def get_subordinate_rental_points_id_by_tg_id(tg_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT id FROM rental_point WHERE owner_id = (SELECT id FROM users WHERE telegram_chat_id = %s);
            ''', (tg_id,))
            return cursor.fetchall()

def get_operator_id_by_rental_point_id_and_date(rental_point_id : int, date:date):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT user_id FROM schedules WHERE work_date = %s AND point_id = %s;
            ''', (date.isoformat(), rental_point_id))
            return cursor.fetchall()
                 


def get_rental_point_by_id(rental_point_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''SELECT name FROM rental_point WHERE id = %s''', (rental_point_id,))
            return cursor.fetchone()

def get_schedule_by_month_and_rental_point_id(month_number, rental_point_id):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT work_date, user_id
                FROM schedules WHERE 
                point_id = %s
                AND
                extract(month from work_date) = %s
                AND iswork = true
            ''', (rental_point_id, month_number))          
            return cursor.fetchall()

def get_operators_id_by_date(date:date):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT user_id FROM schedules WHERE work_date = %s AND iswork = true;
            ''', (date.isoformat(),))
            return cursor.fetchall()

def remove_operator_by_id_and_date_and_rental_point_id(operator_id:int, date:date, rental_point_id:int):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            UPDATE schedules SET point_id = NULL 
            WHERE work_date = %s
            AND user_id = %s
            AND point_id = %s
            ''', (date.isoformat(), operator_id, rental_point_id))
            conn.commit()

def update_schedules_for_operator_id_by_date_and_rental_point_id(operator_id:int, date:date, rental_point_id:int):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            UPDATE schedules SET point_id = %s 
            WHERE work_date = %s
            AND user_id = %s
            ''', (rental_point_id, date.isoformat(), operator_id))
            conn.commit()

def get_day_result_for_rental_point_id_by_month(rental_point_id:int, date:date):
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            SELECT date, (cash+non_cash+)
            ''')