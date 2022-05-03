import psycopg2
from psycopg2 import Error

def db_connection():
    try:
        connection = psycopg2.connect(user="postgres",
                                      # пароль, который указали при установке PostgreSQL
                                      password="qwerty",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="bitcoin")
        return connection

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
