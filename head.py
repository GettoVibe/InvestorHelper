from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from dotenv import load_dotenv
import requests
import os

load_dotenv()

# Токен Telegram бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
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
        "Вот, что я умею:\n"
        "/start - Запустить бота\n"
        "/help - Помощь\n"
        "/rates - Посмотреть актуальные курсы валют\n"
        "/track - Настроить список отслеживаемых валют\n"
        "/convert - Конвертировать сумму из одной валюты в другую\n"
        "/alert - Настроить уведомления о курсе валют\n"
        "/base - Установить базовую валюту\n"
    )

# Команда /rates
async def rates(update: Update, context: CallbackContext):
    base_currency = context.user_data.get('base_currency', 'USD')
    response = requests.get(EXCHANGE_RATE_API_URL + base_currency)
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        message = f"Курсы валют (базовая: {base_currency}):\n"
        for currency, rate in rates.items():
            message += f"{currency}: {rate}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Ошибка при получении курсов валют. Попробуйте позже.")

# Команда /convert
async def convert(update: Update, context: CallbackContext):
    if len(context.args) != 3:
        await update.message.reply_text("Использование: /convert <сумма> <исходная валюта> <целевая валюта>")
        return

    try:
        amount = float(context.args[0])
        from_currency = context.args[1].upper()
        to_currency = context.args[2].upper()

        response = requests.get(EXCHANGE_RATE_API_URL + from_currency)
        if response.status_code == 200:
            data = response.json()
            rates = data['rates']

            if to_currency in rates:
                converted_amount = amount * rates[to_currency]
                await update.message.reply_text(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
            else:
                await update.message.reply_text(f"Валюта {to_currency} не найдена.")
        else:
            await update.message.reply_text("Ошибка получения данных. Попробуйте позже.")
    except ValueError:
        await update.message.reply_text("Ошибка: сумма должна быть числом.")

# Команда /track
async def track(update: Update, context: CallbackContext):
    tracked_currencies = context.user_data.get('tracked_currencies', [])
    if context.args:
        for currency in context.args:
            if currency.upper() not in tracked_currencies:
                tracked_currencies.append(currency.upper())
        context.user_data['tracked_currencies'] = tracked_currencies
        await update.message.reply_text(f"Вы добавили для отслеживания: {', '.join(tracked_currencies)}")
    else:
        if tracked_currencies:
            message = "Отслеживаемые валюты:\n"
            for currency in tracked_currencies:
                response = requests.get(EXCHANGE_RATE_API_URL + "USD")
                if response.status_code == 200:
                    rates = response.json().get('rates', {})
                    rate = rates.get(currency, "нет данных")
                    message += f"{currency}: {rate}\n"
                else:
                    message += f"{currency}: ошибка при получении данных\n"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Вы пока не отслеживаете ни одной валюты.")

# Команда /alert
async def alert(update: Update, context: CallbackContext):
    if len(context.args) != 3:
        await update.message.reply_text("Использование: /alert <валюта> <оператор> <значение>")
        return

    try:
        currency = context.args[0].upper()
        operator = context.args[1]
        threshold = float(context.args[2])
        alerts = context.user_data.get('alerts', [])
        alerts.append((currency, operator, threshold))
        context.user_data['alerts'] = alerts
        await update.message.reply_text(f"Уведомление добавлено: {currency} {operator} {threshold}")
    except ValueError:
        await update.message.reply_text("Ошибка: некорректное значение.")

# Команда /base
async def base(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Использование: /base <валюта>")
        return

    base_currency = context.args[0].upper()
    context.user_data['base_currency'] = base_currency
    await update.message.reply_text(f"Базовая валюта установлена: {base_currency}")

# Основная функция
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rates", rates))
    application.add_handler(CommandHandler("convert", convert))
    application.add_handler(CommandHandler("track", track))
    application.add_handler(CommandHandler("alert", alert))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("base", base))

    application.run_polling()

if __name__ == "__main__":
    main()
