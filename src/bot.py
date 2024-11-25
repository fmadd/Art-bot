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




def send_art_info(message, data):
    description = data['description']

    books_info = "📚 Книги по искусству Древнего Египта:\n"
    for book in data['books']:
        books_info += f"• {book['title']}\nАвтор: {book['author']}\nСсылка: {book['url']}\n\n"
    
    videos_info = "🎥 Видео и лекции:\n"
    for video in data['videos']:
        videos_info += f"• {video['title']} ({video['time']})\nСсылка: {video['url']}\n\n"
    
    places_info = "🏛️ Интересные места:\n"
    for place in data['interesting_places']:
        places_info += f"• {place['title']}\nОписание: {place['description']}\nАдрес: {place['address']}\nВремя работы: {place['museum schedule']}\nСсылка: {place['url']}\n\n"

    full_message = f"🎨 Полезная информация\n\n{description}\n\n{books_info}\n{videos_info}\n{places_info}"
    
    def send_message_in_parts(chat_id, text, max_length=4096):
        while len(text) > max_length:
            split_pos = text.rfind('\n', 0, max_length)
            if split_pos == -1:  
                split_pos = text.rfind(' ', 0, max_length)
            if split_pos == -1: 
                split_pos = max_length

            part = text[:split_pos].strip()
            bot.send_message(chat_id, part)

            text = text[split_pos:].strip()

        if text:
            bot.send_message(chat_id, text)

    send_message_in_parts(message.chat.id, full_message)

bot = telebot.TeleBot(API_TOKEN)

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
            exhibitions_list = [f"{exhibition['title']}\n\n{exhibition['description']}\n\nАдресс: {exhibition['address']}\n\nДата: {exhibition['date']}\n\nРассписание музея: {exhibition['museum schedule']}\n\nСсылка: {exhibition['url']}\n\n"
                                for exhibition in exhibitions['exhibitions']]
            response = f"Выставки по направлению {message.text.capitalize()}:\n\n" + "\n\n".join(exhibitions_list)
        else:
            response = f"Извините, никаких выставок по направлению {message.text.capitalize()} не найдено."
        bot.send_message(user_id, response)

    elif state == 'waiting_for_direction_materials':
        materials = load_materials(message.text)
        if materials:
            send_art_info(message, materials)
        else:
            response = f"Извините, никаких материалов по направлению {message.text.capitalize()} не найдено."
            bot.send_message(user_id, response)

    # Удаляем состояние после обработки
    #user_states.pop(user_id, None)

if __name__ == '__main__':
    bot.polling(none_stop=True)

