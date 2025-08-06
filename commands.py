import telebot

API_TOKEN = '8151060080:AAF5PSdJvYWfX5gDX_1cdJEEbepkSan3laY'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Привет мудилаffавава\
""")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
