#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

API_KEY = 'TOKENBOT'
INFLATION_URL = 'https://www.cbr.ru/hd_base/infl/'

def fetch_inflation_data():
    response = requests.get(INFLATION_URL)
    data = response.json()
    return data['data']

def plot_inflation(data):
    dates = [item['date'] for item in data]
    inflations = [item['value'] for item in data]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, inflations, marker='o')# ������ �� ������� � ���� �����
    plt.title('�������� � ���������� ���������')
    plt.xlabel('����')
    plt.ylabel('������� ��������')
    plt.xticks(rotation=45)
    plt.grid()# ����� �������
    plt.tight_layout()# ����������� ������������ �������

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    return buffer

def inflation(update: Update, context: CallbackContext):
    data = fetch_inflation_data()
    img_buffer = plot_inflation(data)

    update.message.reply_photo(photo=img_buffer)

def main():
    updater = Updater(API_KEY, use_context=True)
    dp = updater.dispatcher# ��������� ��� ��������� ���������� ����� ������� � ��������� �����
    dp.add_handler(CommandHandler("inflation", inflation))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

