#!/usr/bin/python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import requests
import datetime
from io import BytesIO # Форматирование в изображение
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def get_currency_data(currency, date=None):
    # Получаем данные о валюте
    url = f'https://api.exchangerate-api.com/v4/latest/{currency}' 
    # Обрабатываем исключения
    try:
        response = requests.get(url)
        data = response.json()
        if 'rates' in data:
            return data['rates']
        else:
            print("Тарифы, не найденные в ответе")
            return None
    #Конструкция используется  для обработки ошибок, связанных с HTTP-запросами.
    except requests.exceptions.HTTPError as err:
        print(f'Произошла ошибка HTTP:{err}')
        return None
    # Xранит исключение в переменной
    except Exception as err:
        print(f"Произошла ошибка:{err}")
        return None
# Построение графика и его габариты
def plot_currency_graph(rates, currency):
    plt.figure(figsize=(10, 5))
    plt.bar(rates.keys(), rates.values())
    plt.title(f'Курс валюты {currency}')
    plt.xlabel('Валюты')
    plt.ylabel('Курс')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)# Устанавливает текущую позицию буфера в начало
    return buf

def start(update: Update,context: CallbackContext):
    update.message.reply.txt('Отправь команду /gragh <валюта> <дата>')
#Вызов команды gragh
def gragh(update: Update,context: CallbackContext):
    if len(context.args)!=2:
        update.message.reply.txt('Использование: /gragh <валюта> <дата (YYYY-MM-DD)>')
        return 
    currency=context.args[0].upper()
    date=context.args[1]

    try:
        rates=get_currency_data(currency,date)
        graf=plot_currency_graph(rates,currency)
        update.message.reply.photo(photo=graf)
    except Exception as e:
        update.message.reply_text('Ошибка:' + str(e))

def main():
    updater = Updater("7937493118:AAHhVBdgP6rpeGhs9D3hlkmqX3eS0uopb5Q", use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("gragh", gragh))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
