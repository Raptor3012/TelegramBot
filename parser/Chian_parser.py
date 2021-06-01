import logging
import requests
from bs4 import BeautifulSoup
import csv
from time import sleep
import random
from fake_useragent import UserAgent


CSV = 'flats.csv'
PAGES = 100
HOST = 'https://chelyabinsk.cian.ru/'
URL = 'https://chelyabinsk.cian.ru/snyat-kvartiru-chelyabinskaya-oblast/'
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
        all_characteristics = soup.find('main', class_='a10a3f92e9--offer_card_page--3-GaL')
        # Данные по адресу
        address_block = all_characteristics.find('div', class_="a10a3f92e9--geo--18qoo")\
            .find('span', itemprop='name')\
            .get('content').split(',')
        len_address_block = len(address_block)
        if len_address_block == 5:
            characteristic['region'] = address_block[0]
            characteristic['city'] = address_block[1].strip()
            characteristic['district'] = address_block[2].strip()
            if 'р-н' in characteristic['district']:
                characteristic['district'] = characteristic['district'].replace('р-н', '').strip()
            characteristic['mikrodistrict'] = None
            characteristic['street'] = address_block[3].strip()
            if 'ул.' in characteristic['street']:
                characteristic['street'] = characteristic['street'].replace('ул.', '').strip()
            characteristic['building'] = address_block[4].strip()
        elif len_address_block == 6:
            characteristic['region'] = address_block[0]
            characteristic['city'] = address_block[1].strip()
            characteristic['district'] = address_block[2].strip()
            if 'р-н' in characteristic['district']:
                characteristic['district'] = characteristic['district'].replace('р-н', '').strip()
            characteristic['mikrodistrict'] = address_block[3].strip()
            characteristic['street'] = address_block[4].strip()
            if 'ул.' in characteristic['street']:
                characteristic['street'] = characteristic['street'].replace('ул.', '').strip()
            characteristic['building'] = address_block[5].strip()
        else:
            characteristic['region'] = None
            characteristic['city'] = None
            characteristic['district'] = None
            characteristic['mikrodistrict'] = None
            characteristic['street'] = None
            characteristic['building'] = None
            characteristic['area'] = None
            characteristic['floor'] = None
            characteristic['num_of_rooms'] = None
            characteristic['price'] = None
            characteristic['picture'] = None
            return characteristic
        # Данные по квартире
        flat_block = all_characteristics.find('div', class_="a10a3f92e9--info-block--3cWJy")
        flat_block_keys = [block.get_text() for block in flat_block.find_all('div', class_='a10a3f92e9--info-title--2bXM9')]
        flat_block_values = [block.get_text() for block in flat_block.find_all('div', class_='a10a3f92e9--info-value--18c8R')]
        d = {}
        for i in range(len(flat_block_values)):
            flat_block_values[i] = flat_block_values[i].replace('\xa0', ' ')
            d[flat_block_keys[i]] = flat_block_values[i]
        if d['Общая']:
            characteristic['area'] = d['Общая'].split()[0]
        if d['Этаж']:
            characteristic['floor'] = d['Этаж'].split()[0]
        house_title_block = all_characteristics.find(class_='a10a3f92e9--title--2Widg').get_text().split(',')
        characteristic['num_of_rooms'] = house_title_block[0].split()[0]
        if 'Студия' in characteristic['num_of_rooms']:
            characteristic['num_of_rooms'] = 'Студия'
        else:
            characteristic['num_of_rooms'] = characteristic['num_of_rooms'][0]
        price_block = all_characteristics.find(itemprop='price').get('content')
        price = ''.join([char if char.isnumeric() else '' for char in price_block])
        characteristic['price'] = price
        picture = soup.find('img')['src']
        if picture:
            characteristic['picture'] = picture
        else:
            characteristic['picture'] = None
        print(characteristic)
        return characteristic
    else:
        return None



def get_content(html):
    """Здесь идет цикл, в котором я получаю URL квартиры, потом проваливаюсь внутрь
    каждой квартиры и вытягиваю все характеристики в функции get_characteristics"""
    flats = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all(class_='_93444fe79c--container--2pFUD _93444fe79c--cont--1Ddh2')
    random.shuffle(items)
    n = 0
    for item in items:
        print(f'Парсится квартира номер {n+1}')
        url_of_flat = item.find('a', class_='_93444fe79c--link--39cNw').get('href')
        print(url_of_flat)
        sleep(random.uniform(8, 20))
        characteristics = get_characteristics(url_of_flat)
        flats.append(
            {
                'region': characteristics['region'],
                'city': characteristics['city'],
                'district': characteristics['district'],
                'mikrodistrict': characteristics['mikrodistrict'],
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
        writer.writerow(['region', 'city', 'district',
                         'mikrodistrict', 'street', 'building',
                         'area', 'floor', 'num_of_rooms',
                         'price', 'url', 'picture'])
        for item in items:
            writer.writerow([item['region'],
                             item['city'],
                             item['district'],
                             item['mikrodistrict'],
                             item['street'],
                             item['building'],
                             item['area'],
                             item['floor'],
                             item['num_of_rooms'],
                             item['price'],
                             item['url'],
                             item['picture']])


def get_list_of_pages(url):

    return pages_list

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
                url = f'https://chelyabinsk.cian.ru/cat.php?deal_type=rent&engine_version=2&offer_type=flat&p={page}&region=5048&type=4'
                html = get_html(url)
            flats.extend(get_content(html.text))
            to_csv(flats, CSV)
    else:
        print('Error')


def main():
    parser()


if __name__ == '__main__':
    main()






