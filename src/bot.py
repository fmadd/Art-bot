API_TOKEN = "8164726137:AAEoAKbXZsB-4i-MTW3QFwf-qJ-JeDSjlak"
import telebot
from telebot import types
import json
import os

# Функция для загрузки данных

def format(direction):
    return direction.replace(" ", "_")

def load_art_directions():
    with open('data/art_directions.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_materials(direction):
    materials_path = f'data/materials/{format(direction)}.json'
    if os.path.exists(materials_path):
        with open(materials_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_exhibitions(direction):
    exhibitions_path = f'data/exhibitions/{format(direction)}.json'
    if os.path.exists(exhibitions_path):
        with open(exhibitions_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Загрузка данных направлений искусства
art_directions = load_art_directions()
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exhibitions_button = types.KeyboardButton("Выставки")
    materials_button = types.KeyboardButton("Материалы")
    markup.add(exhibitions_button, materials_button)
    bot.send_message(message.chat.id, "Привет! Я искусствоведческий бот. Пожалуйста, выберите, что вас интересует:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Выставки", "Материалы"])
def main_menu(message):
    if message.text == "Выставки":
        user_states[message.chat.id] = 'waiting_for_direction_exhibitions'
        show_directions(message.chat.id, "выставок")
    elif message.text == "Материалы":
        user_states[message.chat.id] = 'waiting_for_direction_materials'
        show_directions(message.chat.id, "материалов")

def show_directions(chat_id, action):
    directions_list = "\n".join(art_directions.keys())
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for direction in art_directions.keys():
        markup.add(direction.capitalize())
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    
    bot.send_message(chat_id, f"Введите направление искусства для получения {action}:\n{directions_list}", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in art_directions.keys() or message.text == "Назад")
def handle_user_direction(message):
    user_id = message.chat.id

    if message.text == "Назад":
        start(message)  # Возврат в главное меню
        user_states.pop(user_id, None)
        return
    
    # Проверяем состояние и загружаем соответствующие данные
    state = user_states.get(user_id)
    
    if state == 'waiting_for_direction_exhibitions':
        exhibitions = load_exhibitions(message.text)
        if exhibitions:
            exhibitions_list = [f"{exhibition['name']}: {exhibition['description']} (дата: {exhibition['date']})"
                                for exhibition in exhibitions['exhibitions']]
            response = f"Выставки по направлению {message.text.capitalize()}:\n" + "\n".join(exhibitions_list)
        else:
            response = f"Извините, никаких выставок по направлению {message.text.capitalize()} не найдено."
        bot.send_message(user_id, response)

    elif state == 'waiting_for_direction_materials':
        materials = load_materials(message.text)
        if materials:
            materials_list = [f"{item['type']}: {item['title']} (Автор: {item.get('author', 'Не указан')}, URL: {item['url']})"
                              for item in materials['materials']]
            response = f"Материалы по направлению {message.text.capitalize()}:\n" + "\n".join(materials_list)
        else:
            response = f"Извините, никаких материалов по направлению {message.text.capitalize()} не найдено."
        bot.send_message(user_id, response)

    # Удаляем состояние после обработки
    #user_states.pop(user_id, None)

if __name__ == '__main__':
    bot.polling(none_stop=True)
'''ункционал бота можно разделить на две основные части.

Во-первых, бот сможет по каждому из направлений, выбранных пользователем, давать краткую характеристику, а также при запросе подбирать искусствоведческие материалы, которые помогли бы пользователю углубить свои знания об искусстве этого направления, и рекомендовать музеи, в которых можно ознакомиться с произведениями искусства этого направления.

Во-вторых, бот сможет выдавать список актуальных выставок, проходящих в Москве, и их описания, а также при запросе подбирать искусствоведческие материалы, которые помогли бы пользователю подготовиться к посещению этих выставок.'''