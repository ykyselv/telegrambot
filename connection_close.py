def connection_close(cursor, connection):
    cursor.close()
    connection.close()
    print("Соединение с PostgreSQL закрыто")
