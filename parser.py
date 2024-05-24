import asyncio
import os
import requests
import datetime
from time import sleep
from datetime import timedelta
from aiohttp import ClientSession
from lxml import etree
from io import StringIO


def fetcher(catalog_section_name: str, catalog_section_url: str, page_number: int) -> list:
    """
    Fetches products URLs from a given catalog section URL corresponding to a specific page number.

    Args:
        catalog_section_name (str): The name of the catalog section.
        catalog_section_url (str): The URL of the catalog section.
        page_number (int): The specific page number to fetch data from.

    Returns:
        list: A list of URLs corresponding to product links on the page.
    """
    parser = etree.HTMLParser()
    page_url = f"{catalog_section_url}?page={page_number}"
    page = requests.get(page_url)
    print(page.status_code)
    if page.status_code != 200:
        sleep(5)
        page = requests.get(page_url)
        print(page.status_code)
        if page.status_code != 200:
            with open('log.txt', 'a') as file:
                msk_time_now = datetime.datetime.now(datetime.UTC) + timedelta(hours=3)
                file.write(
                    f"{msk_time_now.strftime('%Y-%m-%d %H:%M:%S')} Error fetching {page.url}: {page.status_code} {page.reason}\n")
    with open(f'{os.path.join("404_and_500_errors", f"{catalog_section_name}_403_ddos.txt")}', 'a') as file:
        file.write(f"----------\nОбработка страницы {page_number}\n----------\n")
    with open(f'{os.path.join("404_and_500_errors", f"{catalog_section_name}_404.txt")}', 'a') as file:
        file.write(f"----------\nОбработка страницы {page_number}\n----------\n")
    with open(f'{os.path.join("404_and_500_errors", f"{catalog_section_name}_500.txt")}', 'a') as file:
        file.write(f"----------\nОбработка страницы {page_number}\n----------\n")
    print(f'-------- {page_url} --------')
    html = page.text
    tree = etree.parse(StringIO(html), parser=parser)
    refs = tree.xpath("//a[@class='product-card__image-link base-link']")
    return ['https://www.bookvoed.ru' + link.get('href', '') for link in refs]


async def fill_queue(links: list[str]):
    """
    Asynchronously fills a queue with the provided list of URLs.

    Args:
        links (list): A list of products URLs to be put into the queue.
    """
    for link in links:
        await links_queue.put(link)


async def worker(links_queue: asyncio.Queue, catalog_section_name: str):
    """
    Asynchronous function that processes URLs from a queue to check response statuses.

    Args:
        links_queue (asyncio.Queue): A queue containing  products URLs to process.
        catalog_section_name (str): The name of the catalog section being processed.
    """
    current_url = await links_queue.get()
    try:
        async with ClientSession() as session:
            async with session.get(current_url) as response:
                if response.status == 403:
                    print("403")
                    with open(f'{os.path.join("404_and_500_errors", f"{catalog_section_name}_403_ddos.txt")}', 'a') as file:
                        file.write(f"{current_url}\n")
                if response.status == 404:
                    with open(f'{os.path.join("404_and_500_errors", f"{catalog_section_name}_404.txt")}', 'a') as file:
                        file.write(f"{current_url}\n")
                if response.status == 500:
                    with open(f'{os.path.join("404_and_500_errors", f"{catalog_section_name}_500.txt")}', 'a') as file:
                        file.write(f"{current_url}\n")
    except Exception as e:
        with open('log.txt', 'a') as file:
            # msk_time_now = datetime.utcnow() + timedelta(hours=3)
            msk_time_now = datetime.datetime.now(datetime.UTC) + timedelta(hours=3)
            file.write(f"{msk_time_now.strftime('%Y-%m-%d %H:%M:%S')} Error fetching {current_url}: {e}\n")
    finally:
        links_queue.task_done()

# CATALOG_SECTIONS_URLS = [("Книги-с-автографом", "https://www.bookvoed.ru/catalog/knigi-s-avtografom-4435", 16),
#                         ("Художественная-литература", "https://www.bookvoed.ru/catalog/fiction-1592", 1689),
#                         ("Детские-книги", "https://www.bookvoed.ru/catalog/detskie-knigi-1159", 1011),
#                         ("Товары-для-детей", "https://www.bookvoed.ru/catalog/detstov-1338", 186),
#                         ("Книги-для-подростков", "https://www.bookvoed.ru/catalog/knigi-dlya-podrostkov-3351", 23),
#                         ("Бизнес-литература", "https://www.bookvoed.ru/catalog/business-1671", 138),
#                         ("Самообразование-и-развитие", "https://www.bookvoed.ru/catalog/samoobrazovanie-i-razvitie-4560", 178),
#                         ("Хобби-и-досуг", "https://www.bookvoed.ru/catalog/khobbi-i-dosug-4056", 817),
#                         ("Учебная-литература", "https://www.bookvoed.ru/catalog/school-1492", 621),
#                         ("Педагогика-и-воспитание", "https://www.bookvoed.ru/catalog/pedagogika-i-vospitanie-4743", 172),
#                         ("Научно-популярная-литература", "https://www.bookvoed.ru/catalog/estestvennye-nauki-1347", 1269),
#                         ("Публицистика", "https://www.bookvoed.ru/catalog/publitsistika-1426", 177),
#                         ("Религия", "https://www.bookvoed.ru/catalog/religiya-1437", 171),
#                         ("Эксклюзивная-продукция", "https://www.bookvoed.ru/catalog/eksklyuzivnaya-produktsiya-3656", 13),
#                         ("Канцтовары", "https://www.bookvoed.ru/catalog/kantstovary-1919", 344),
#                         ("Календари-2024", "https://www.bookvoed.ru/catalog/kalendari-2024-4788", 15),
#                         ("Сувениры.Аксессуары", "https://www.bookvoed.ru/catalog/suvenirnaya-produktsiya-2182", 117),
#                         ("Книги-в-кожаном-переплете", "https://www.bookvoed.ru/catalog/knigi-v-kozhanom-pereplete-2729", 8),
#                         ("Книжный-развал", "https://www.bookvoed.ru/catalog/knizhnyy-razval-3646", 18),
#                         ("Букинистика-и-антикварные-издания", "https://www.bookvoed.ru/catalog/bukinistika-i-antikvarnye-izdaniya-4772", 49),
#                         ("Хозтовары", "https://www.bookvoed.ru/catalog/khoztovary-3668", 1),
#                         ("Аудиокниги", "https://www.bookvoed.ru/catalog/audio-1693", 1)]

CATALOG_SECTIONS_URLS = [("Товары-для-детей", "https://www.bookvoed.ru/catalog/detstov-1338", 186),
                         ("Книги-с-автографом", "https://www.bookvoed.ru/catalog/knigi-s-avtografom-4435", 16),
                         ("Книги-для-подростков", "https://www.bookvoed.ru/catalog/knigi-dlya-podrostkov-3351", 23)]


if __name__ == "__main__":
    for item in CATALOG_SECTIONS_URLS:
        for _ in range(1, item[2] + 1):
            links = fetcher(item[0], item[1], _)
            links_queue = asyncio.Queue()
            asyncio.run(fill_queue(links))
            while not links_queue.qsize() == 0:
                asyncio.run(worker(links_queue, item[0]))
