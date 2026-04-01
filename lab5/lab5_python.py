import psycopg2

# Класс для работы с базой данных PostgreSQL
class Database:

    # Конструктор класса. Устанавливает соединение с базой данных и создает курсор.
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="python_db",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        self.cur = self.conn.cursor()

    # Создание таблицы users, если она еще не существует
    def create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INT
        );
        """)
        self.conn.commit()

    # CREATE - операция создания (добавления) данных
    def add_user(self, name, age):
        self.cur.execute(
            "INSERT INTO users (name, age) VALUES (%s, %s);",
            (name, age)
        )
        self.conn.commit()

    # READ - операция чтения данных
    def get_users(self):
        self.cur.execute("SELECT * FROM users;")
        return self.cur.fetchall()

    # UPDATE - операция обновления данных
    def update_user(self, user_id, new_age):
        self.cur.execute(
            "UPDATE users SET age = %s WHERE id = %s;",
            (new_age, user_id)
        )
        self.conn.commit()

    # DELETE - операция удаления данных
    def delete_user(self, user_id):
        self.cur.execute(
            "DELETE FROM users WHERE id = %s;",
            (user_id,)
        )
        self.conn.commit()

    # Закрытие соединения с базой данных
    def close(self):
        self.cur.close()
        self.conn.close()



if __name__ == "__main__":
    db = Database()

    db.create_table()

    # CREATE: добавляем двух пользователей
    db.add_user("Alice", 25)
    db.add_user("Bob", 30)

    # READ: получаем и выводим всех пользователей
    print("Все пользователи:")
    users = db.get_users()
    for user in users:
        print(user)

    # UPDATE: обновляем возраст пользователя с ID = 1
    print("\nОбновляем возраст пользователя с id=1")
    db.update_user(1, 26)

    # READ после обновления
    print("\nПосле обновления:")
    print(db.get_users())

    # DELETE: удаляем пользователя с ID = 2
    print("\nУдаляем пользователя с id=2")
    db.delete_user(2)

    # READ после удаления
    print("\nПосле удаления:")
    print(db.get_users())

    # Закрываем соединение с базой данных
    db.close()