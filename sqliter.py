import sqlite3

class SQLiter:

    def __init__(self,database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()