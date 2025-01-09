import asyncio  # Асинхронная библиотека для работы с событиями и задачами
import logging  # Библиотека для логирования событий
import os  # Для работы с операционной системой (чтение переменных окружения)
import sys  # Для работы с системными параметрами и потоками

from aiogram import Bot, Dispatcher  # Основные классы для работы с Telegram Bot API
from aiogram.client.default import DefaultBotProperties  # Настройки бота по умолчанию
from dotenv import find_dotenv, load_dotenv  # Для загрузки переменных из .env файла

from bot.handler import router  # Импорт маршрутизатора для обработки входящих сообщений

# Загрузка переменных из файла .env
load_dotenv(find_dotenv())

# Настройка логирования: уровень INFO, вывод в стандартный поток вывода (stdout)
logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main() -> None:
    """Основная асинхронная функция для запуска Telegram-бота."""

    # Получение токена бота из переменной окружения
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token is None:  # Если токен отсутствует, выбрасываем исключение
        raise ValueError("BOT_TOKEN is not set")

    # Создаем экземпляр бота с заданным токеном и настройками
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(
            parse_mode="HTML"
        ),  # Используем HTML-разметку в сообщениях
    )

    # Удаляем вебхуки, если они есть, и сбрасываем неподтвержденные обновления
    await bot.delete_webhook(drop_pending_updates=True)

    # Создаем диспетчер для управления логикой обработки сообщений
    dp = Dispatcher()

    # Подключаем маршрутизатор, определяющий, как обрабатывать входящие сообщения
    dp.include_routers(router)

    # Запускаем процесс получения и обработки обновлений
    await dp.start_polling(bot)


# Если файл запускается как основной (а не импортируется), выполняем основную функцию
if __name__ == "__main__":
    asyncio.run(main())
