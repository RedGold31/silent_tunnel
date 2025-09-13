import os
import io
import telebot
from telebot import types
from dotenv import load_dotenv
from database import save_user
from descriptions import start_descriptions
from vpn.generator import generation

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message) -> None:
    """
    Стартовое сообщение пользователю телеграм бота
    :param message: Сообщение пользователя
    :return:
    """
    chat_id = message.chat.id
    save_user(message.from_user)
    bot.send_message(chat_id, start_descriptions)


@bot.message_handler(commands=["configs"])
def send_config(message) -> None:
    """
    По запросу отправляет пользователю конфиг созданный генератором
    :param message: Сообщение пользователя
    """
    chat_id = message.chat.id
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("wg-quick", callback_data="wg"))
    kb.add(types.InlineKeyboardButton("JSON", callback_data="json"))
    bot.send_message(message.chat.id, "Выберите формат конфига:", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call) -> None:
    """
    Обработка нажатия inline-кнопки
    """
    bot.answer_callback_query(call.id)

    wg = call.data == "wg"
    cfg_text = generation(wg=wg)
    f = io.BytesIO(cfg_text.encode("utf-8"))
    f.name = "config.conf" if wg else "config.json"
    bot.send_document(call.message.chat.id, f)


@bot.message_handler(func=lambda message: True)
def echo_message(message) -> None:
    """
    Возвращает пользовательский айди в чат
    :param message: Сообщение пользователя
    """
    chat_id = message.chat.id
    bot.send_message(chat_id, message.from_user.username)


bot.infinity_polling()
