import sqlite3
import csv

class SQLiter:

    def __init__(self, database_file):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def fill_base(self, csv_file):
        """Открываем заранее сохраненный csv и заполняем базу"""
        with open(csv_file, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='|')
            for row in reader:
                """Костыль :)"""
                if 'Челябинск' not in row:
                    continue
                # print(row)
                self.cursor.execute("""INSERT OR REPLACE into FlatInfo (city,district,mikrodistrict,street,building,area,flor,num_of_rooms,price,url,picture)\
                                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",\
                                    (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))
            self.connection.commit()

    def find_in_base(self, arguments):
        if arguments['rooms'] > "3":
            sql = "SELECT city,district,mikrodistrict,street,building,area,flor,num_of_rooms,price,url,picture \
                                FROM FlatInfo" \
                  " WHERE price>=? and price<=? and district=? and num_of_rooms='Более 3-к' and flor=?"
            self.cursor.execute(sql, (
            arguments['min_price'], arguments['max_price'], arguments['district'], arguments['flor']))
        else:
            sql = "SELECT city,district,mikrodistrict,street,building,area,flor,num_of_rooms,price,url,picture \
                    FROM FlatInfo" \
                  " WHERE price>=? and price<=? and district=? and num_of_rooms=? and flor=?"
            self.cursor.execute(sql, (
                arguments['min_price'],arguments['max_price'],arguments['district'],arguments['rooms'],
                arguments['flor']))

        rows = self.cursor.fetchall()

        for row in rows:
            print(row)
        return rows

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()