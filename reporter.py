import datetime
import os
from copy import deepcopy
from datetime import timedelta


number_of_pages_in_section = {"Аудиокниги": 31,
                              "Бизнес-литература": 8292,
                              "Букинистика-и-антикварные-издания": 2897,
                              "Детские-книги": 61132,
                              "Календари-2024": 883,
                              "Канцтовары": 20821,
                              "Книги-в-кожаном-переплете": 469,
                              "Книги-для-подростков": 1363,
                              "Книги-с-автографом": 945,
                              "Книжный-развал": 1037,
                              "Научно-популярная-литература": 76427,
                              "Педагогика-и-воспитание": 10336,
                              "Публицистика": 10657,
                              "Религия": 10256,
                              "Самообразование-и-развитие": 10693,
                              "Сувениры.Аксессуары": 6972,
                              "Товары-для-детей": 11147,
                              "Учебная-литература": 37287,
                              "Хобби-и-досуг": 49336,
                              "Хозтовары": 19,
                              "Художественная-литература": 102793,
                              "Эксклюзивная-продукция": 769}

table = """
| Раздел каталога                   | Страниц с 404 ошибкой | % страниц с 404 ошибкой | Страниц с 500 ошибкой | % страниц с 500 ошибкой | Всего страниц товаров в разделе |
|-----------------------------------|:---------------------:|:-----------------------:|:---------------------:|:-----------------------:|:-------------------------------:|
"""


def generate_report(table: str, number_of_pages_in_section: dict[str, int]):
    """
    Generate a report based on the info from .txt files in 404_and_500_errors directory.

    Parameters:
    - table (str): The initial table header to which the report will be appended.
    - number_of_pages_in_section (dict): A dictionary containing sections names and the number of pages in each section.
    """
    directory_path = '404_and_500_errors'
    txt_files = [file for file in os.listdir(directory_path) if file.endswith('.txt')]
    copy_number_of_pages_in_section = deepcopy(number_of_pages_in_section)
    for file in txt_files:
        catalog_section_name = file.split('_')[0]
        with open(os.path.join(directory_path, file), "r") as f:
            count = 0
            for line in f:
                if "https" in line:
                    count += 1
            if file.endswith('404.txt'):
                cnt = count if file.endswith('404.txt') else 0
                table += f"| {catalog_section_name} | {cnt} | {cnt*100/number_of_pages_in_section[catalog_section_name]:.2f} "
            if file.endswith('500.txt'):
                cnt = count if file.endswith('500.txt') else 0
                table += f"| {cnt} | {cnt*100/number_of_pages_in_section[catalog_section_name]:.2f} | {number_of_pages_in_section[catalog_section_name]} |\n"
                copy_number_of_pages_in_section.pop(catalog_section_name)

    for key, value in copy_number_of_pages_in_section.items():
        table += f"| {key} | PENDING | PENDING | PENDING | PENDING | {value} |\n"

    msk_time_now = datetime.datetime.now(datetime.UTC) + timedelta(hours=3)
    with open(f"report-{msk_time_now.strftime('%Y-%m-%d %H-%M-%S')}.md", "w") as file:
        file.write(f"## Отчет на {msk_time_now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write("<br />\n")
        file.write(table)


if __name__ == "__main__":
    generate_report(table, number_of_pages_in_section)
