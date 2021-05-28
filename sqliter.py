import sqlite3
import csv

class SQLiter:

    def __init__(self, database_file):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def fill_base(self, csv_file):
        with open(csv_file, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                if 'Челябинск' not in row:
                    continue
                print(row[0])
                self.cursor.re

    def input_or_update_data(self, row):


    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()