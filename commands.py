import os
import telebot
from dotenv import load_dotenv
from database import save_user
from descriptions import start_descriptions
from vpn.generator import generation

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    """
    Стартовое сообщение пользователю телеграм бота
    :param message: Сообщение пользователя
    :return:
    """
    chat_id = message.chat.id
    save_user(message.from_user)
    bot.send_message(chat_id, start_descriptions)


@bot.message_handler(commands=["configs"])
def send_config(message):
    """
    По запросу отправляет пользователю конфиг созданный генератором
    :param message: Сообщение пользователя
    """
    chat_id = message.chat.id
    generation()
    file_path = "vpn/configs/config.conf"
    try:
        with open(file_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption="Ваш документ сосал?")
        bot.send_message(chat_id, "Файл успешно отправлен!")
    except FileNotFoundError:
        bot.send_message(chat_id, "Файл не найден. Укажите корректный путь.")
    except Exception as e:
        bot.send_message(chat_id, f"Произошла ошибка: {e}")


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    """
    Возвращает пользовательский айди в чат
    :param message: Сообщение пользователя
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, message.from_user.username)


bot.infinity_polling()
