"""
Telegram бот для RAG-ассистента.
Обрабатывает сообщения пользователей и отправляет их ассистенту.
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from src.rag_assistant import get_assistant, RAGAssistant

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Тексты сообщений
WELCOME_MESSAGE = """Привет! Я ассистент по Python и DevOps.

Я могу ответить на вопросы о:
• Git и контроль версий
• Docker и контейнеризация
• Виртуальные окружения Python
• pytest и тестирование
• FastAPI и веб-разработка
• asyncio и асинхронное программирование
• SQLAlchemy и базы данных
• Pydantic и валидация данных
• Poetry и управление зависимостями
• CI/CD и автоматизация
• И многое другое!

Просто напишите свой вопрос, и я постараюсь помочь.

Команды:
/start — показать это сообщение
/reset — сбросить контекст диалога
/help — справка"""

HELP_MESSAGE = """Справка по боту

Этот бот использует RAG (Retrieval-Augmented Generation) для ответов на вопросы по Python и DevOps.

Как это работает:
1. Вы задаёте вопрос
2. Бот ищет релевантную информацию в базе знаний
3. На основе найденных данных формирует ответ
4. В ответе указываются источники информации

Советы:
• Задавайте конкретные вопросы
• Бот помнит контекст диалога — можно уточнять
• Используйте /reset если хотите начать новую тему

Команды:
/start — приветствие
/reset — сбросить контекст
/help — эта справка"""

RESET_MESSAGE = "Контекст диалога сброшен. Можете начать новую тему."

THINKING_MESSAGE = "Думаю над ответом..."


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text(WELCOME_MESSAGE)
    logger.info(f"User {update.effective_user.id} started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text(HELP_MESSAGE)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /reset."""
    user_id = update.effective_user.id
    assistant = get_assistant()
    assistant.reset_thread(user_id)
    await update.message.reply_text(RESET_MESSAGE)
    logger.info(f"User {user_id} reset their context")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    user_id = update.effective_user.id
    question = update.message.text.strip()
    
    if not question:
        return
    
    logger.info(f"User {user_id}: {question[:100]}...")
    
    await update.message.chat.send_action("typing")
    
    thinking_msg = await update.message.reply_text(THINKING_MESSAGE)
    
    try:
        assistant = get_assistant()
        response = await assistant.ask_async(user_id, question)
        
        reply_text = response.text
        
        # Добавляем источники, если они есть
        if response.sources:
            sources_text = ", ".join(f"`{s}`" for s in response.sources)
            reply_text += f"\n\n📚 *Источники:* {sources_text}"
        
        await thinking_msg.delete()
        await update.message.reply_text(
            reply_text,
            parse_mode="Markdown"
        )
        
        logger.info(f"Response to user {user_id}: {response.text[:100]}...")
        
    except Exception as e:
        logger.error(f"Error handling message from user {user_id}: {e}")
        await thinking_msg.delete()
        await update.message.reply_text(
            f"❌ Произошла ошибка при обработке запроса.\n\n"
            f"Попробуйте позже или переформулируйте вопрос.\n\n"
            f"Техническая информация: `{str(e)[:200]}`",
            parse_mode="Markdown"
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок."""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Запуск бота."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError(
            "Не задана переменная окружения TELEGRAM_BOT_TOKEN. "
            "Скопируйте env.example в .env и добавьте токен бота."
        )
    
    print("=" * 50)
    print("Запуск Telegram бота")
    print("=" * 50)
    
    print("⏳ Инициализация RAG-ассистента...")
    try:
        assistant = get_assistant()
        # Пробуем загрузить индекс
        assistant._load_index_id()
        print("✓ Ассистент готов")
    except Exception as e:
        print(f"⚠ Предупреждение: {e}")
        print("  Бот запустится, но могут быть ошибки при обработке сообщений")
    
    # Создание приложения
    application = Application.builder().token(token).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    application.add_error_handler(error_handler)
    
    print("✓ Бот запущен! Нажмите Ctrl+C для остановки.")
    print("=" * 50)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
