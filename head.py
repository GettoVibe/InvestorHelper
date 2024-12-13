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
    
# Команда /rates - получение курсов валют
def rates(update: Update, context: CallbackContext):
    base_currency = "USD"  # Базовая валюта по умолчанию
    response = requests.get(EXCHANGE_RATE_API_URL + base_currency)
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        message = "Актуальные курсы валют (базовая: USD):\n"
        for currency, rate in rates.items():
            message += f"{currency}: {rate}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Не удалось получить курсы валют. Попробуйте позже.")

# Обработчик неизвестных сообщений
def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Извините, я не понимаю эту команду. Используйте /help.")

   # Основная функция для запуска бота
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("rates", rates))

    # Обработчик неизвестных сообщений
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
