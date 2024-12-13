from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests

# Токен Telegram бота
TELEGRAM_TOKEN = "7937493118:AAHhVBdgP6rpeGhs9D3hlkmqX3eS0uopb5Q"

# API для получения курсов валют
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/"

# Команда /start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для конвертации валют. \n"
        "Используй /help, чтобы узнать, что я умею."

# Команда /help
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Вот что я умею:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/rates - Посмотреть актуальные курсы валют\n"
        "/track - Настроить список отслеживаемых валют\n"
        "/convert - Конвертировать сумму из одной валюты в другую"
    )
@bot.message_handler(commands=['convert'])
def converter(message):
    bot.send_message(message.chat.id, 'Сколько конвертируем?')
    bot.register_next_step_handler(message, summa)

def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Перепроверьте данные. Нам нужно число:')
        bot.register_next_step_handler(message, summa)
        return

    if amount >= 1:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/RUB', callback_data='usd/rub')
        btn4 = types.InlineKeyboardButton('RUB/USD', callback_data='rub/usd')
        btn5 = types.InlineKeyboardButton('EUR/RUB', callback_data='eur/rub')
        btn6 = types.InlineKeyboardButton('RUB/EUR', callback_data='rub/eur')
        btn7 = types.InlineKeyboardButton('Другое значение', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Перепроверьте данные. Нам нужно положительное число и более 0:')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        res = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f'Получается: {round(res, 2)}. Введите следующее число?')
        bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введите пару значений через слэшь')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
        try:
            values = message.text.upper().split('/')
            res = currency.convert(amount, values[0], values[1])
            bot.send_message(message.chat.id, f'Получается: {round(res, 2)}. Введите следующее число?')
            bot.register_next_step_handler(message, summa)
        except Exception:
            bot.send_message(message.chat.id, 'Что-то не так. Перепроверьте данные. Введите значение заново:')
            bot.register_next_step_handler(message, my_currency)


bot.polling(none_stop = True)
