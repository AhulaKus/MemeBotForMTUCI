from contextlib import asynccontextmanager  # Для создания контекстного менеджера

import aiosqlite  # Библиотека для асинхронной работы с SQLite

from config import DB_PATH
from utils.randomizer import random_token  # Импортируем функцию для генерации случайных токенов


@asynccontextmanager
async def get_db_connection():
    """
    Контекстный менеджер для создания подключения к базе данных.
    Автоматически открывает и закрывает соединение.
    """
    db = await aiosqlite.connect(DB_PATH)
    try:
        yield db  # Возвращает подключение для выполнения запросов
    finally:
        await db.close()  # Закрывает соединение при выходе из контекста


async def recreate_table():
    """
    Пересоздает главную таблицу `users` в базе данных.
    Удаляет старую таблицу, создает новую и заполняет 100 случайных записей.
    """
    async with get_db_connection() as db:
        # Удаляем таблицу, если она существует
        await db.execute("DROP TABLE IF EXISTS users")

        # Создаем новую таблицу `users`
        await db.execute(
            """
            CREATE TABLE users (
                token TEXT,            -- Уникальный токен пользователя
                chat_id TEXT,          -- Идентификатор чата Telegram
                is_authorized BOOLEAN, -- Статус авторизации
                model TEXT             -- Выбранная модель
            )
            """
        )

        # Генерируем данные для вставки
        users = [(random_token(), "0", False, "phi3") for _ in range(100)]

        # Вставляем данные в таблицу
        await db.executemany(
            "INSERT INTO users (token, chat_id, is_authorized, model) VALUES (?, ?, ?, ?)",
            users,
        )
        await db.commit()  # Сохраняем изменения


async def get_model(chat_id):
    """
    Получает выбранную модель пользователя из базы данных по идентификатору чата.

    Аргументы:
        chat_id (str): Идентификатор чата Telegram.

    Возвращает:
        Название выбранной модели в виде строки.
    """
    async with get_db_connection() as db:
        cursor = await db.execute("SELECT model FROM users WHERE chat_id=?", (chat_id,))
        result = await cursor.fetchone()
        return result[0]  # Возвращаем название модели


async def update_model(chat_id, model):
    """
    Обновляет выбранную модель пользователя в базе данных.

    Аргументы:
        chat_id (str): Идентификатор чата Telegram.
        model (str): Название новой модели.
    """
    async with get_db_connection() as db:
        await db.execute(
            "UPDATE users SET model = ? WHERE chat_id = ?", (model, chat_id)
        )
        await db.commit()  # Сохраняем изменения


async def is_user_added(chat_id):
    """
    Проверяет, добавлен ли пользователь в базу данных.

    Аргументы:
        chat_id (str): Идентификатор чата Telegram.

    Возвращает:
        True, если пользователь существует, иначе False.
    """
    async with get_db_connection() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE chat_id=?", (chat_id,)
        )
        result = await cursor.fetchone()
        return result[0] > 0  # Проверяем, есть ли записи


async def is_token_authorized(token):
    """
    Проверяет, авторизован ли токен в базе данных.

    Аргументы:
        token (str): Уникальный токен пользователя.

    Возвращает:
        True, если токен авторизован, иначе False.
    """
    async with get_db_connection() as db:
        cursor = await db.execute(
            "SELECT is_authorized FROM users WHERE token=?", (token,)
        )
        result = await cursor.fetchone()
        return result[0]  # Возвращаем статус авторизации


async def auth_user(chat_id, token):
    """
    Авторизует пользователя, обновляя его запись в базе данных.

    Аргументы:
        chat_id (str): Идентификатор чата Telegram.
        token (str): Уникальный токен пользователя.
    """
    async with get_db_connection() as db:
        await db.execute(
            "UPDATE users SET is_authorized = 1, chat_id = ? WHERE token = ?",
            (chat_id, token),
        )
        await db.commit()  # Сохраняем изменения


async def logout_user(token):
    """
    Выполняет логаут пользователя, сбрасывая его авторизацию и модель.

    Аргументы:
        token (str): Уникальный токен пользователя.
    """
    async with get_db_connection() as db:
        await db.execute(
            'UPDATE users SET is_authorized = 0, chat_id = 0, model = "phi3" WHERE token = ?',
            (token,),
        )
        await db.commit()  # Сохраняем изменения


async def get_token(chat_id):
    """
    Получает токен пользователя из базы данных по идентификатору чата.

    Аргументы:
        chat_id (str): Идентификатор чата Telegram.

    Возвращает:
        Токен в виде строки
    """
    async with get_db_connection() as db:
        cursor = await db.execute("SELECT token FROM users WHERE chat_id=?", (chat_id,))
        result = await cursor.fetchone()
        return result[0]  # Возвращаем токен


async def is_token_valid(token):
    """
    Проверяет, существует ли токен в базе данных.

    Аргументы:
        chat_id (str): Идентификатор чата Telegram.

    Возвращает:
        True, если токен существует, иначе False.
    """
    async with get_db_connection() as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE token = ?", (token,)
        )
        result = await cursor.fetchone()
        return result[0] > 0  # Проверяем, есть ли записи
