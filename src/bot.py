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


def send_materials(message, data, material_type):
    print(material_type)
    content = ''
    if material_type == "Видео":
        pcontent = "🎥 Видео и лекции:\n\n"
        for video in data.get('videos', []):
            content += f"• [{video['title']}]({video['url']}).\n\n"
    elif material_type == "Книги":
        pcontent = "📚 Книги:\n\n"
        for book in data.get('books', []):
            content += f"• [{book['title']}]({book['url']}).\n"
            if(book['author']): content += f"Автор: {book['author']}.\n"
            content += "\n"
    elif material_type == "Краткое описание":
       
        pcontent = "📄 Описание:\n\n"
        dat = data.get('description', [])
        print(dat)
        content = f"{dat}\n\n"
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
    exhibitions_button = types.KeyboardButton("Места для посещения")
    materials_button = types.KeyboardButton("Материалы")
    markup.add(exhibitions_button, materials_button)
    bot.send_message(message.chat.id, "Привет! Я искусствоведческий бот. Пожалуйста, выберите, что вас интересует:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Места для посещения", "Материалы"])
def main_menu(message):
    if message.text == "Места для посещения":
        user_states[str(message.chat.id)] = 'waiting_for_direction_exhibitions'
        show_directions(message.chat.id, "выставок")
    elif message.text == "Материалы":
        user_states[str(message.chat.id)] = 'waiting_for_direction_materials'
        show_directions(message.chat.id, "материалов")

def show_directions(chat_id, action):
    state = user_states[str(chat_id)]

    if state == 'waiting_for_direction_exhibitions':
        directions_list = "• "
        directions_list += "\n• ".join(art_exhibitions.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for direction in art_exhibitions.keys():
            markup.add(direction)
    elif state == 'waiting_for_direction_materials':
        directions_list = "• "
        directions_list += "\n• ".join(art_directions.keys())
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for direction in art_directions.keys():
            markup.add(direction)

    
    back_button = types.KeyboardButton("Назад")
    markup.add(back_button)
    
    bot.send_message(chat_id, f"Выберите интересующее Вас направление/период в искусстве :\n\n{directions_list}", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in art_directions.keys() or message.text in art_exhibitions.keys()or message.text == "Назад")
def handle_user_direction(message):
    user_id = str(message.chat.id) 

    if message.text == "Назад":
        start(message)  
        user_states.pop(user_id, None)
        return
    
    state = user_states[user_id]
    if state == 'waiting_for_direction_exhibitions':
        exhibitions = load_exhibitions(message.text)
        if exhibitions:
            bot.send_message(user_id, f"Места для посещения по направлению {message.text}:")
            for exhibition in exhibitions['exhibitions']:
                exhibition_details = (
                    f"*{exhibition['title']}*\n\n"
                    f"🏛️ {exhibition['description']}\n\n"
                )

                if exhibition['full_description']:
                    exhibition_details += f"📎 [Подробнее]({exhibition['full_description']}).\n\n"

                exhibition_details += (
                    f"📍 Адрес: {exhibition['address']}.\n\n"
                )

                if 'date' in exhibition:
                    exhibition_details += (
                    f"📆 Дата: {exhibition['date']}.\n\n"
                    )

                exhibition_details += (
                    f"🕐 Расписание: {exhibition['museum schedule']}.\n\n"
                )

                if exhibition['url']:
                    exhibition_details += f"🎟️ [Купить билеты]({exhibition['url']}).\n\n"

                # Если есть изображения, отправляем их вместе с описанием
                if 'img' in exhibition and exhibition['img']:
                    print(exhibition['img'])
                    image_path = exhibition['img']
                    with open(image_path, 'rb') as photo:
                        print(image_path)
                        bot.send_photo(
                            user_id, 
                            photo, 
                            caption=exhibition_details, 
                            parse_mode='Markdown'  # Это может не сработать в caption
                        )
                else:
                    bot.send_message(user_id, exhibition_details, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            response = f"Извините, никаких мест по направлению {message.text.capitalize()} не найдено."
            bot.send_message(user_id, response)


    elif state == 'waiting_for_direction_materials':
        materials = load_materials(message.text)
        if materials:

            user_states[user_id + '_direction'] = message.text
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("Видео", "Книги", "Краткое описание", "Назад")
            bot.send_message(user_id, "Выберите, что вы хотите получить:", reply_markup=markup)
            user_states[user_id] = 'waiting_for_material_type'
        else:
            response = f"Извините, никаких материалов по направлению {message.text.capitalize()} не найдено."
            bot.send_message(user_id, response)

@bot.message_handler(func=lambda message: message.text in ["Видео", "Книги", "Краткое описание", "Назад"])
def handle_material_type(message):
    user_id = str(message.chat.id)  
    print(message)
    if message.text == "Назад":
        start(message) 
        user_states.pop(user_id, None)
        return

    # Получаем направление, выбранное пользователем
    direction = user_states.get(user_id + '_direction')
    if direction:
        materials = load_materials(direction)
        if materials:
            send_materials(message, materials, message.text)  # Отправляем материалы по выбранному типу
        else:
            bot.send_message(user_id, "Извините, материалов по выбранному направлению не найдено.")
    
    user_states.pop(user_id, None)

if __name__ == '__main__':
    while(True):
        try:
            bot.polling(none_stop=True)
        except:
            continue
