from mysql.connector import connect, Error
import Config




def add_users(TG_id, FIO, rate):
    try:
        with connect(
                host="localhost",
                user=Config.BD_Login,
                password=Config.BD_Password,
                database="kuti_tg_database",
        ) as connection:
            sql = f"INSERT INTO TG_Users (TG_id,First_Second_Name,Rate) VALUES ({TG_id},\"{FIO}\",{rate})"
            print(sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                connection.commit()
    except Error as e:
        print(e)

def get_user(id):
    try:
        with connect(
                host="localhost",
                user=Config.BD_Login,
                password=Config.BD_Password,
                database="kuti_tg_database",
        ) as connection:
            sql = f"select * from TG_Users WHERE TG_id = {id}"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
    except Error as e:
        print(e)