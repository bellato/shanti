# -*- coding: utf-8 -*-

# import urllib.request  не подошёл так как не умеет работать с кирилическими url
import requests
from bs4 import BeautifulSoup
import re
import time

import config
from db_api import CManageDB


class CParser:
    def __init__(self):
        self.full_lots = {}
        self.lots = {}
        self.lot = {}
        self.url = config.URL
        self.db = CManageDB()

    # качаем страничку и возращаем таблицу лотов
    def get_page(self):
        html_page = requests.get(self.url).text
        soup = BeautifulSoup(html_page, 'lxml')
        table_auction = soup.find('table')
        return table_auction

    # метод создания словаря одного лота
    def new_lot(self, link, id_lot, product, base_price, buyer, current_price, hours_ago):
        self.lot['link_vk'] = link  # https://vk.com/wall-12345678_123456
        self.lot['id_lot'] = id_lot
        self.lot['title'] = product
        self.lot['money'] = base_price
        self.lot['name'] = buyer
        self.lot['money2'] = current_price
        self.lot['hours_ago'] = hours_ago

    # получения id из vk ссылки с помощью регулярки
    def get_id(self, link):
        pattern = r'[0-9]+[\_][0-9]+'
        id_l = int(re.findall(pattern, link)[0])
        return str(id_l)

    # удаление лишних пробелов из полученых данных
    def clean_product_price(self, raw):
        raw_str = raw.split('  ')
        for i in range(len(raw_str)):
            if '' in raw_str:
                raw_str.remove('')
        return raw_str[0].strip(), raw_str[1].replace('\xa0', ' ').strip()

    # получение имени последнего сделавшего ставку и его ставки
    def get_buyer_current_price(self, str_html_lot):
        buyer = str_html_lot[2].text.strip()
        current_price = str_html_lot[3].text.strip()
        hours_ago = str_html_lot[4].text.strip()
        return buyer, current_price, hours_ago

    # наполнение словаря лотов из таблицы лотов с сайта
    def parse(self, html_data):
        try:
            for html_lot in html_data.find_all('tr')[1:]:
                str_html_lot = html_lot.find_all('td')
                vk_link = html_lot.find_all('a')[0].get('href')  # https://vk.com/wall-12345678_123456
                id_lot = self.get_id(vk_link)
                raw_product_price = str_html_lot[1].text
                product, price = self.clean_product_price(raw_product_price)
                buyer, current_price, hours_ago = self.get_buyer_current_price(str_html_lot)
                self.new_lot(vk_link, id_lot, product, price, buyer, current_price, hours_ago)
                self.lots[id_lot] = self.lot.copy()
                self.lot.clear()
        except AttributeError:
            pass

    def add_lot_in_db(self, lot):
        self.db.add_lot_row(lot)
        self.db.add_history_row(lot, time.time())

    # метод вывода лотов на момент запуска скрипта и добавление их в словарь и бд текущих, актуальных лотов
    def add_print_lots(self):
        for _, lot in self.lots.items():
            self.print_lot(lot)
            self.add_lot_in_db(lot)
            self.add_lot(lot)
        self.lots.clear()

    # проверка на появление новых лотов и добавление их в словарь текущих, актуальных лотов
    def check_new_lots(self):
        for id_l, lot in self.lots.items():
            if id_l not in self.full_lots:
                self.print_lot(lot)
                self.add_lot_in_db(lot)
                self.add_lot(lot)
                print('всего {} лотов'.format(len(self.full_lots)))

    # проверка ушедших лотов и удаление их из словаря текущих, актуальных лотов
    def check_sold_lot(self):
        for id_l, lot in self.full_lots.copy().items():
            if id_l not in self.lots:
                self.full_lots.pop(id_l)
                self.db.change_sold_lot(lot)

    # проверка изменения последнего поставившего
    def check_buyer(self):
        for id_l, lot in self.lots.items():
            if self.full_lots[id_l]['money2'] != lot['money2']:
                print('{} сделал ставку на {} {} {}'.format(lot['name'], lot['title'], lot['money2'], lot['hours_ago']))
                self.full_lots[id_l] = lot
                self.db.add_history_row(lot, time.time())

    # добавление лотов в словарь текущих, актуальных лотов
    def add_lot(self, lot):
        self.full_lots[lot['id_lot']] = lot

    # печать лота
    def print_lot(self, lot):
        print('{} - {} - Обычная цена: {} руб. - {} - {} руб.'.format(lot['id_lot'], lot['title'], lot['money'],
                                                                      lot['name'], lot['money2']))

    # основной цикл программы
    def mainloop(self):
        page = self.get_page()
        self.parse(page)
        self.db.create_tables()
        self.add_print_lots()
        print('всего {} лотов'.format(len(self.full_lots)))
        while True:
            time.sleep(600)
            page = self.get_page()
            self.parse(page)
            self.check_new_lots()
            self.check_sold_lot()
            self.check_buyer()
            self.lots.clear()


if __name__ == '__main__':
    try:
        pars = CParser()
        pars.mainloop()
    except KeyboardInterrupt:
        pars.db.cursor.close()

'''
сделал благодаря 
https://www.youtube.com/watch?v=KPXPr-KS-qk&index=16&list=WL&t=0s
'''
