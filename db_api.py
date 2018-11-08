# -*- coding: utf-8 -*-
import sqlite3


class CManageDB:
    def __init__(self):
        self.conn = sqlite3.connect("db_shanti.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute('create table if not exists all_lots(id_lot integer primary key unique, vk_link text, '
                            'title text, money text, flag integer)')

        self.cursor.execute('create table if not exists history (id_lot_table integer references all_lots (id_lot), '
                            'name text, money2 text, datetime real)')

        self.conn.commit()

    def add_lot_row(self, lot):
        self.cursor.execute('insert into all_lots(id_lot, vk_link, title, money, flag) '
                            'select :id_lot, :vk_link, :title, :money, :flag where not exists '
                            '(select 1 from all_lots where id_lot = :id_lot)',
                            {"id_lot": lot['id_lot'], "vk_link": lot['link_vk'],
                             "title": lot['title'], "money": lot['money'],
                             "flag": 1})
        self.conn.commit()

    def add_history_row(self, lot, datetime):
        self.cursor.execute('insert into history (id_lot_table, name, money2, datetime) '
                            'values (:id_lot, :name, :money2, :datetime)',
                            {"id_lot": lot['id_lot'], "name": lot['name'],
                             "money2": lot['money2'], "datetime": datetime})
        self.conn.commit()

    def get_actual_lot(self):
        self.cursor.execute('select * from all_lots where flag = 1')
        return self.cursor.fetchall()

    def change_sold_lot(self, lot):
        self.cursor.execute('update all_lots set flag = 0 where id_lot = :id', {"id": lot['id_lot']})
        self.conn.commit()

    def get_history_lot(self):
        pass


if __name__ == '__main__':
    db = CManageDB()
    a = db.get_actual_lot()
    db.cursor.close()
    print(*a, sep='\n')
