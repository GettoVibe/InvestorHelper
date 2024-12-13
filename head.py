from multiprocessing import Value
import telebot
from currency_converter import CurrencyConverter
from telebot import types


bot = telebot.TeleBot('7937493118:AAHhVBdgP6rpeGhs9D3hlkmqX3eS0uopb5Q')
currency = CurrencyConverter()
amount = 0

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name} {message.from_user.last_name}!\n Я - твой личный переводчик валют.\n Чтобы узнать подробнее о моих навыках, напиши /help.')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Список навыков:\n /start - начать работу с ботом\n /help - получить список доступных навыков\n /convert - конвертировать валюту')


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