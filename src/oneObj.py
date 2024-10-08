import requests
import json
from bs4 import BeautifulSoup as BS
import random

def get_random_image():
    with open('../data/objects.json', "r") as f:
        objects = json.loads(f.readline())['objects']
        n = len(objects)

    name = objects[random.randint(1, n + 1)]
    url = f"https://ar.culture.ru/ru/subject/{name}"
    response = requests.get(url)

    if response.status_code == 200:
        html = BS(response.content, 'html.parser')

        title = html.find('h1', class_='subject_info_block__title')
        if title:
            title = title.text.strip()
        else:
            title = 'Название не указано'

        author = html.find('a', class_='subject_info_block__author')
        if author:
            author = author.text.strip()
        else:
            author = 'Автор не указан'

        creation_time = html.find('div', class_='subject_info_block__group_value')
        if creation_time:
            creation_time = creation_time.text.strip()
        else:
            creation_time = 'Время создание не указано'

        size = html.find_all('div', class_='subject_info_block__group_value')[1]
        if size: size = size.text.strip()
        else:
            size = 'Размер не указан'

        technique = html.find_all('div', class_='subject_info_block__group_value')[2]
        if technique: technique = technique.text.strip()
        else:
            technique = 'Техника не указана'

        description = html.find_all('div', class_='editable_block with_editor_panel')

        if len(description) == 0:
            description = ['Описание не указано']

        img = html.find('div', id='points_wrapper').find('img', id='point_test_image')['data-src']

        print("Название:", title)
        print("Картинка:", img)
        print("Автор:", author)
        print("Время создания:", creation_time)
        print("Размер:", size)
        print("Техника:", technique)
        print("Описание:", *[des for des in description])
        return dict({"name": title, "img": img, "author": author, "creation_time": creation_time, "size": size, "technique": technique, "description": [des for des in description]})
    else:
        return dict({})