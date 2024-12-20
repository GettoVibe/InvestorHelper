from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv
import requests
import os
import logging
from datetime import datetime, timedelta

# Загрузка переменных окружения
load_dotenv()

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение токена из переменной окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_TOKEN:
    logger.error("Токен Telegram бота не найден. Убедитесь, что он указан в .env файле.")
    exit(1)

# API для получения курсов валют
EXCHANGE_RATE_API_URL = "https://api.exchangerate-api.com/v4/latest/"

# Команда /start
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    logger.info(f"Received start command from {user.first_name}")
    if update.message:
        await update.message.reply_text(
            f"Привет, {user.first_name}! Я бот для конвертации валют. \n"
            "Используй /help, чтобы узнать, что я умею."
        )

# Команда /help
async def help_command(update: Update, context: CallbackContext):
    if update.message:
        await update.message.reply_text(
            "Вот, что я умею:\n"
            "/start - Запустить бота\n"
            "/help - Помощь\n"
            "/rates - Посмотреть актуальные курсы валют\n"
            "/track - Настроить список отслеживаемых валют\n"
            "/convert - Конвертировать сумму из одной валюты в другую\n"
            "/alert - Настроить уведомления о курсе валют\n"
            "/base - Установить базовую валюту"
        )

# Команда /rates - получение курсов валют
async def rates(update: Update, context: CallbackContext):
    base_currency = context.user_data.get('base_currency', 'USD')  # Базовая валюта по умолчанию
    response = requests.get(EXCHANGE_RATE_API_URL + base_currency)
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']
        message = f"Актуальные курсы валют (базовая: {base_currency}):\n"
        for currency, rate in rates.items():
            message += f"{currency}: {rate}\n"
        if update.message:
            await update.message.reply_text(message)
    else:
        if update.message:
            await update.message.reply_text("Не удалось получить курсы валют. Попробуйте позже.")

# Команда /convert - конвертация валют
async def convert(update: Update, context: CallbackContext):
    try:
        if len(context.args) != 3:
            if update.message:
                await update.message.reply_text("Использование: /convert <сумма> <исходная валюта> <целевая валюта>")
            return
        
        amount = float(context.args[0])  # Сумма для конвертации
        from_currency = context.args[1].upper()  # Исходная валюта
        to_currency = context.args[2].upper()  # Целевая валюта
        
        response = requests.get(EXCHANGE_RATE_API_URL + from_currency)
        
        if response.status_code == 200:
            data = response.json()
            rates = data['rates']
            
            if to_currency not in rates:
                if update.message:
                    await update.message.reply_text(f"Ошибка: валюта {to_currency} не найдена.")
                return
            
            conversion_rate = rates[to_currency]
            converted_amount = amount * conversion_rate
            if update.message:
                await update.message.reply_text(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
        else:
            if update.message:
                await update.message.reply_text("Не удалось получить курсы валют. Попробуйте позже.")
    
    except ValueError:
        if update.message:
            await update.message.reply_text("Ошибка: сумма должна быть числом.")

# Сохранение отслеживаемых валют для пользователя
async def track(update: Update, context: CallbackContext):
    user = update.effective_user
    if len(context.args) == 0:
        tracked_currencies = context.user_data.get('tracked_currencies', [])
        base_currency = context.user_data.get('base_currency', 'USD')  # Получаем базовую валюту пользователя
        if tracked_currencies:
            message = f"Отслеживаемые валюты (базовая валюта: {base_currency}):\n"
            for currency in tracked_currencies:
                # Получаем курс для каждой отслеживаемой валюты
                response = requests.get(EXCHANGE_RATE_API_URL + base_currency)  # Используем базовую валюту
                if response.status_code == 200:
                    data = response.json()
                    rates = data['rates']
                    if currency.upper() in rates:
                        rate = rates[currency.upper()]
                        message += f"{currency.upper()}: {rate}\n"
                    else:
                        message += f"{currency.upper()}: Нет данных о курсе\n"
                else:
                    message += f"{currency.upper()}: Не удалось получить курс\n"
        else:
            message = "В данный момент вы не отслеживаете никакие валюты. Введите /track и название валюты, чтобы добавить валюту"
        if update.message:
            await update.message.reply_text(message)
    else:
        # Добавляем новые валюты в список отслеживаемых
        tracked_currencies = context.user_data.get('tracked_currencies', [])
        for currency in context.args:
            if currency.upper() not in tracked_currencies:
                tracked_currencies.append(currency.upper())
        context.user_data['tracked_currencies'] = tracked_currencies
        if update.message:
            await update.message.reply_text(f"Теперь вы отслеживаете валюты: {', '.join(tracked_currencies)}")

# Уведомления о курсе валют
async def alert(update: Update, context: CallbackContext):
    try:
        if len(context.args) != 3:
            if update.message:
                await update.message.reply_text("Использование: /alert <валюта> <оператор> <значение>\nПример: /alert USD > 80")
            return
        
        currency = context.args[0].upper()
        operator = context.args[1]
        threshold = float(context.args[2])

        # Сохраняем уведомление в user_data
        alerts = context.user_data.get('alerts', [])
        alerts.append((currency, operator, threshold))
        context.user_data['alerts'] = alerts

        if update.message:
            await update.message.reply_text(f"Уведомление настроено: {currency} {operator} {threshold}")
    except ValueError:
        if update.message:
            await update.message.reply_text("Ошибка: некорректное значение порога.")

async def check_alerts(context: CallbackContext):
    job = context.job
    user_data = job.data
    chat_id = job.chat_id

    if 'alerts' not in user_data:
        return

    alerts = user_data['alerts']
    response = requests.get(EXCHANGE_RATE_API_URL + "USD")  # Проверяем на основе USD
    if response.status_code == 200:
        data = response.json()
        rates = data['rates']

        for alert in alerts:
            currency, operator, threshold = alert
            if currency in rates:
                rate = rates[currency]

                if (operator == '>' and rate > threshold) or (operator == '<' and rate < threshold):
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"Уведомление: {currency} {operator} {threshold}. Текущий курс: {rate}"
                    )

# Установка базовой валюты
async def base(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        if update.message:
            await update.message.reply_text("Использование: /base <валюта>")
        return

    base_currency = context.args[0].upper()
    context.user_data['base_currency'] = base_currency
    if update.message:
        await update.message.reply_text(f"Базовая валюта установлена: {base_currency}")

# Основная функция
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Логируем старт работы бота
    logger.info("Bot is starting...")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("convert", convert))
    application.add_handler(CommandHandler("track", track))
    application.add_handler(CommandHandler("rates", rates))
    application.add_handler(CommandHandler("alert", alert))
    application.add_handler(CommandHandler("base", base))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
