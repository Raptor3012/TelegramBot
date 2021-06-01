import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
import random


CSV = 'flats.csv'
PAGES = 100
HOST = 'https://arenda-022.ru'
URL = 'https://arenda-022.ru/chelyabinsk/kvartira'
HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.41 YaBrowser/21.5.0.579 Yowser/2.5 Safari/537.36'
    }


def get_html(url, user_agent=None, proxy=None, params=None):
    """Ну тут все понятно, получаем html разметку со страницы"""
    response = requests.get(url, headers=HEADERS, proxies=proxy, params=params)
    return response


def get_characteristics(url, params=''):
    """Тут я беру характеристики квартиры со страницы квартиры."""
    consist = ''
    characteristic = {}
    html = get_html(url)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        # Данные по адресу
        price_block = soup.find(class_='detail-view2 table table-striped table-condensed')
        odd_blocks = price_block.find_all(class_="odd")
        characteristic['city'] = odd_blocks[0].find('td').get_text()
        characteristic['num_of_rooms'] = odd_blocks[1].find('td').get_text()
        if 'Более' in characteristic['num_of_rooms']:
            pass
        else:
            characteristic['num_of_rooms'] = characteristic['num_of_rooms'][0]
        address = odd_blocks[2].find('td').get_text().split()
        if len(address) == 3:
            characteristic['microdistrict'] = address[0]
            characteristic['street'] = address[1]
            characteristic['building'] = address[2]
        elif len(address) == 2:
            characteristic['microdistrict'] = None
            characteristic['street'] = address[0]
            characteristic['building'] = address[1]
        else:
            characteristic['microdistrict'] = None
            characteristic['street'] = None
            characteristic['building'] = None
        even_blocks = soup.find_all(class_="even")
        characteristic['district'] = even_blocks[1].find('td').get_text()
        characteristic['price'] = even_blocks[2].find('td').get_text().replace('руб.', '').replace(' ', '')
        params = soup.find_all(class_='detail-view table table-striped table-condensed')
        characteristic['floor'] = params[0].find(class_='even').find('td').get_text()[0]
        characteristic['area'] = params[0].find_all(class_='odd')[1].find('td').get_text().split(' ')[0]
        try:
            picture_block = soup.find(class_='fotorama').find('a').get('href')
            characteristic['picture'] = HOST + picture_block
        except:
            characteristic['picture'] = None
        return characteristic


def get_content(html):
    """Здесь идет цикл, в котором я получаю URL квартиры, потом проваливаюсь внутрь
    каждой квартиры и вытягиваю все характеристики в функции get_characteristics"""
    flats = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='categories-container')
    random.shuffle(items)
    n = 0
    for item in items:
        print(f'Парсится квартира номер {n+1}')
        url_of_flat = item.find('a').get('href')
        print(HOST + url_of_flat)
        sleep(random.uniform(8, 20))
        characteristics = get_characteristics(HOST + url_of_flat)
        flats.append(
            {
                'city': characteristics['city'],
                'district': characteristics['district'],
                'microdistrict': characteristics['microdistrict'],
                'street': characteristics['street'],
                'building': characteristics['building'],
                'area': characteristics['area'],
                'floor': characteristics['floor'],
                'num_of_rooms': characteristics['num_of_rooms'],
                'price': characteristics['price'],
                'url': url_of_flat,
                'picture': characteristics['picture']
            }

        )
        n += 1
    return flats


def to_csv(items, path):
    """Записываю все в csv"""
    with open(path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['city', 'district',
                         'microdistrict', 'street', 'building',
                         'area', 'floor', 'num_of_rooms',
                         'price', 'url', 'picture'])
        for item in items:
            writer.writerow([item['city'],
                             item['district'],
                             item['microdistrict'],
                             item['street'],
                             item['building'],
                             item['area'],
                             item['floor'],
                             item['num_of_rooms'],
                             item['price'],
                             item['url'],
                             item['picture']])


def parser():
    """Сама функция парсера"""
    flats = []
    html = get_html(URL)
    if html.status_code == 200:
        for page in range(1, PAGES+1):
            print(f'Парсится страница номер {page}')
            if page == 1:
                html = get_html(URL)
            else:
                url = f'https://arenda-022.ru/chelyabinsk/kvartira?p=2{page}'
                html = get_html(url)
            flats.extend(get_content(html.text))
            to_csv(flats, CSV)
    else:
        print('Error')


def main():
    parser()


if __name__ == '__main__':
    main()






