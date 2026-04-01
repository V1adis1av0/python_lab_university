import psycopg2

try:
    conn = psycopg2.connect(
        dbname="python_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )

    print("Успешное подключение!")

    cur = conn.cursor()

    cur.execute("SELECT version();")
    db_version = cur.fetchone()
    print("Версия PostgreSQL:", db_version)

    cur.close()
    conn.close()

except Exception as e:
    print("Ошибка:", e)