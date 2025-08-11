import telebot

from database import save_user
from descriptions import start_descriptions

API_TOKEN = '8151060080:AAF5PSdJvYWfX5gDX_1cdJEEbepkSan3laY'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.from_user)
    bot.reply_to(message , start_descriptions)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
