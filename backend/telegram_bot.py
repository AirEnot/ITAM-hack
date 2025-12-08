import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from config import get_settings

load_dotenv()
settings = get_settings()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or settings.TELEGRAM_BOT_TOKEN
BACKEND_URL = os.getenv("BACKEND_URL") or settings.BACKEND_URL
FRONTEND_URL = os.getenv("FRONTEND_URL") or settings.FRONTEND_URL


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    
    # Получаем информацию о пользователе
    user = update.effective_user
    telegram_id = str(user.id)
    telegram_username = user.username or f"user_{user.id}"
    
    try:
        # Отправляем запрос на backend чтобы получить код
        response = requests.post(
            f"{BACKEND_URL}/api/auth/telegram/generate-code",
            params={
                "telegram_id": telegram_id,
                "telegram_username": telegram_username
            }
        )
        
        if response.status_code != 200:
            await update.message.reply_text("❌ Ошибка сервера. Попробуйте позже.")
            return
        
        data = response.json()
        code = data.get("code")
        
        # Отправляем сообщение с кодом
        message = (
            f"🔐 Ваш код авторизации:\n\n"
            f"<b>{code}</b>\n\n"
            f"⏰ Код действителен 10 минут\n\n"
            f"Вставьте этот код на сайте:\n"
            f"<a href='{FRONTEND_URL}'>Перейти на сайт</a>"
        )
        
        await update.message.reply_text(
            message,
            parse_mode="HTML"
        )
        
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("❌ Ошибка подключения. Попробуйте позже.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    
    help_text = (
        "🤖 Помощь\n\n"
        "/start - Получить код авторизации\n"
        "/help - Показать эту справку\n\n"
        "Вставьте полученный код на сайте чтобы авторизоваться."
    )
    
    await update.message.reply_text(help_text)


def main():
    """Главная функция для запуска бота"""
    
    # Создаём приложение
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Запускаем бота
    print("🤖 Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
