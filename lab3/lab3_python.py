import unittest

'''
Тестируемая функция "process_user" обрабатывает данные пользователя:
    Проверяет валидность имени (строка, не пустая)
    Проверяет валидность возраста (неотрицательный)
    Возвращает словарь с полями: name, age, is_adult, nickname, roles
''' 
def process_user(name, age):
    if not isinstance(name, str) or not name:
        raise ValueError("Invalid name")

    if age < 0:
        raise ValueError("Invalid age")

    return {
        "name": name,
        "age": age,
        "is_adult": age >= 18,
        "nickname": None if len(name) < 3 else name[:3],
        "roles": ["user"] if age < 18 else ["user", "admin"]
    }


'''
Тестовый класс ""TestProcessUser" демонстрирует использование:
    assertEqual / assertNotEqual - проверка равенства
    assertTrue / assertFalse - проверка булевых значений
    assertIs / assertIsNot - проверка идентичности объектов
    assertIsNone / assertIsNotNone - проверка на None
    assertIn / assertNotIn - проверка вхождения в коллекцию
    assertRaises - проверка исключений
'''
class TestProcessUser(unittest.TestCase):

    # assertEqual
    def test_name_and_age(self):
        user = process_user("Alex", 20)
        self.assertEqual(user["name"], "Alex")
        self.assertEqual(user["age"], 20)

    # assertNotEqual
    def test_not_equal(self):
        user = process_user("Alex", 20)
        self.assertNotEqual(user["name"], "Bob")

    # assertTrue
    def test_is_adult_true(self):
        user = process_user("Alex", 20)
        self.assertTrue(user["is_adult"])

    # assertFalse
    def test_is_adult_false(self):
        user = process_user("Tom", 15)
        self.assertFalse(user["is_adult"])

    # assertIs
    def test_boolean_identity(self):
        user = process_user("Alex", 20)
        self.assertIs(user["is_adult"], True)

    # assertIsNot
    def test_is_not(self):
        user = process_user("Tom", 15)
        self.assertIsNot(user["is_adult"], True)

    # assertIsNone
    def test_nickname_none(self):
        user = process_user("Al", 20)
        self.assertIsNone(user["nickname"])

    # assertIsNotNone
    def test_nickname_exists(self):
        user = process_user("Alex", 20)
        self.assertIsNotNone(user["nickname"])

    # assertIn
    def test_role_in(self):
        user = process_user("Alex", 20)
        self.assertIn("admin", user["roles"])

    # assertNotIn
    def test_role_not_in(self):
        user = process_user("Tom", 15)
        self.assertNotIn("admin", user["roles"])

    # assertRaises (неправильное имя)
    def test_invalid_name(self):
        with self.assertRaises(ValueError):
            process_user("", 20)

    # assertRaises (неправильный возраст)
    def test_invalid_age(self):
        with self.assertRaises(ValueError):
            process_user("Alex", -1)

# Запуск тестов
if __name__ == "__main__":
    unittest.main()