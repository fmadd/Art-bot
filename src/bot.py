import telebot
import requests
import oneObj

BOT_TOKEN = "8164726137:AAEoAKbXZsB-4i-MTW3QFwf-qJ-JeDSjlak"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name} {message.from_user.last_name}! 👋  Напиши мне, и я пришлю тебе объект классического искусства!")

@bot.message_handler(commands=['help'])
def send_help_info(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name} {message.from_user.last_name}! 👋 Я бот для творческого самообразования. Ты можешь написать мне /image и я расскажу тебе о произведении искусства.")

@bot.message_handler(commands=['image'])
def send_image(message):
    object = oneObj.get_random_image()
    print(object)
    image_url = object['img']
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    image_data = response.content
    bot.send_photo(message.chat.id, image_data, caption='123')


@bot.message_handler()
def echo(message):
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name} {message.from_user.last_name}! 👋")
    elif message.text.lower() == 'id':
        bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")


bot.polling(none_stop=True)
