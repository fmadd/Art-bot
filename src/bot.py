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

def load_art_exhibitions():
    with open('data/art_exhibitions.json', 'r', encoding='utf-8') as f:
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

# def escape_markdown(text):
#     escape_chars = ['\\', '`',  '_', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '.', '!']
#     for char in escape_chars:
#         text = text.replace(char, f'\{char}')
#     return text

def send_materials(message, data, material_type):
    content = ''
    if material_type == "Видео":
        pcontent = "🎥 Видео и лекции:\n"
        for video in data.get('videos', []):
            content += f"• [{video['title']}]({video['url']})\n\n"
    elif material_type == "Книги":
        pcontent = "📚 Книги:\n"
        for book in data.get('books', []):
            content += f"• [{book['title']}]({book['url']})\nАвтор: {book['author']}\n\n"
    elif material_type == "Места":
        pcontent = "🏛️ Интересные места:\n"
        if len(data.get('interesting_places', [])) != 0: 
            for place in data.get('interesting_places', []):
                content += f"• [{place['title']}]({place['url']})\nОписание: {place['description']}\nАдрес: {place['address']}\nВремя работы: {place['museum schedule']}\n\n"
    print(material_type)
    if content:
        content = pcontent + content
        bot.send_message(message.chat.id, content, parse_mode='Markdown', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, "Извините, ничего не найдено.")

bot = telebot.TeleBot(API_TOKEN)

art_directions = load_art_directions()
art_exhibitions = load_art_exhibitions()
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
        user_states[str(message.chat.id)] = 'waiting_for_direction_exhibitions'
        show_directions(message.chat.id, "выставок")
    elif message.text == "Материалы":
        user_states[str(message.chat.id)] = 'waiting_for_direction_materials'
        show_directions(message.chat.id, "материалов")

def show_directions(chat_id, action):
    state = user_states[str(chat_id)]

    if state == 'waiting_for_direction_exhibitions':
        directions_list = "• "
        directions_list += "\n• ".join(art_directions.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for direction in art_directions.keys():
            markup.add(direction.capitalize())
    elif state == 'waiting_for_direction_materials':
        directions_list = "• "
        directions_list += "\n• ".join(art_exhibitions.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for direction in art_exhibitions.keys():
            markup.add(direction.capitalize())

    
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    
    bot.send_message(chat_id, f"Введите направление искусства для получения {action}:\n{directions_list}", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in art_directions.keys() or message.text == "Назад")
def handle_user_direction(message):
    user_id = str(message.chat.id) 

    if message.text == "Назад":
        start(message)  
        user_states.pop(user_id, None)
        return
    
    state = user_states[user_id]
    print(user_states, user_id, state)
    if state == 'waiting_for_direction_exhibitions':
        exhibitions = load_exhibitions(message.text)
        if exhibitions:
            bot.send_message(user_id, f"Выставки по направлению {message.text.capitalize()}:")
            for exhibition in exhibitions['exhibitions']:
                
                exhibition_details = (
                    f" *{exhibition['title']}*.\n\n"
                    f"🏛️ {exhibition['description']}\n\n"
                    f"📍 Адресс: {exhibition['address']}.\n\n"
                    f"📆 Дата: {exhibition['date']}.\n\n"
                    f"🕐 Расписание музея: {exhibition['museum schedule']}.\n\n"
                    
                )
                escaped_exhibition_details = exhibition_details #escape_markdown(exhibition_details)
                escaped_exhibition_details += f"🎟️ [Купить билеты]({exhibition['url']})\n\n"
                bot.send_message(user_id, escaped_exhibition_details, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            response = f"Извините, никаких выставок по направлению {message.text.capitalize()} не найдено."
            bot.send_message(user_id, response)


    elif state == 'waiting_for_direction_materials':
        materials = load_materials(message.text)
        if materials:

            user_states[user_id + '_direction'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Видео", "Книги", "Места", "Назад")
            bot.send_message(user_id, "Выберите, что вы хотите получить:", reply_markup=markup)
            user_states[user_id] = 'waiting_for_material_type'
        else:
            response = f"Извините, никаких материалов по направлению {message.text.capitalize()} не найдено."
            bot.send_message(user_id, response)

@bot.message_handler(func=lambda message: message.text in ["Видео", "Книги", "Места", "Назад"])
def handle_material_type(message):
    user_id = str(message.chat.id)  

    if message.text == "Назад":
        start(message) 
        user_states.pop(user_id, None)
        return

    # Получаем направление, выбранное пользователем
    direction = user_states.get(user_id + '_direction')
    print(direction)
    if direction:
        materials = load_materials(direction)
        if materials:
            send_materials(message, materials, message.text)  # Отправляем материалы по выбранному типу
        else:
            bot.send_message(user_id, "Извините, материалов по выбранному направлению не найдено.")
    
    user_states.pop(user_id, None)

if __name__ == '__main__':
    bot.polling(none_stop=True)
