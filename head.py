from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import requests

# Токен Telegram бота
TELEGRAM_TOKEN = "7937493118:AAHhVBdgP6rpeGhs9D3hlkmqX3eS0uopb5Q"

# API для получения курсов валют
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/"

# Команда /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я бот для конвертации валют. \n"
        "Используй /help, чтобы узнать, что я умею."
    )

# Команда /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Вот что я умею:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/rates - Посмотреть актуальные курсы валют\n"
        "/track - Настроить список отслеживаемых валют\n"
        "/convert - Конвертировать сумму из одной валюты в другую"
    )

# Команда /rates - получение курсов валют
async def rates(update: Update, context: CallbackContext):
    base_currency = "USD"  # Базовая валюта по умолчанию
    response = requests.get(EXCHANGE_RATE_API_URL + base_currency)
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        message = "Актуальные курсы валют (базовая: USD):\n"
        for currency, rate in rates.items():
            message += f"{currency}: {rate}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Не удалось получить курсы валют. Попробуйте позже.")

# Команда /convert - конвертация валют
async def convert(update: Update, context: CallbackContext):
    try:
        if len(context.args) != 3:
            await update.message.reply_text("Использование: /convert <сумма> <исходная валюта> <целевые валюта>")
            return
        
        amount = float(context.args[0])  # Сумма для конвертации
        from_currency = context.args[1].upper()  # Исходная валюта
        to_currency = context.args[2].upper()  # Целевая валюта
        
        response = requests.get(EXCHANGE_RATE_API_URL + from_currency)
        
        if response.status_code == 200:
            data = response.json()
            rates = data['rates']
            
            if to_currency not in rates:
                await update.message.reply_text(f"Ошибка: валюта {to_currency} не найдена.")
                return
            
            conversion_rate = rates[to_currency]
            converted_amount = amount * conversion_rate
            await update.message.reply_text(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
        else:
            await update.message.reply_text("Не удалось получить курсы валют. Попробуйте позже.")
    
    except ValueError:
        await update.message.reply_text("Ошибка: сумма должна быть числом.")

# Сохранение отслеживаемых валют для пользователя
async def track(update: Update, context: CallbackContext):
    user = update.effective_user
    if len(context.args) == 0:
        tracked_currencies = context.user_data.get('tracked_currencies', [])
        if tracked_currencies:
            message = "Отслеживаемые валюты:\n" + "\n".join(tracked_currencies)
        else:
            message = "Вы не отслеживаете никакие валюты."
        await update.message.reply_text(message)
    else:
        tracked_currencies = context.user_data.get('tracked_currencies', [])
        for currency in context.args:
            if currency.upper() not in tracked_currencies:
                tracked_currencies.append(currency.upper())
        context.user_data['tracked_currencies'] = tracked_currencies
        await update.message.reply_text(f"Теперь вы отслеживаете валюты: {', '.join(tracked_currencies)}")

# Обработчик неизвестных сообщений
async def unknown(update: Update, context: CallbackContext):
    await update.message.reply_text("Извините, я не понимаю эту команду. Используйте /help.")

# Основная функция для запуска бота
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rates", rates))
    application.add_handler(CommandHandler("convert", convert))
    application.add_handler(CommandHandler("track", track))

    # Обработчик неизвестных сообщений
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
