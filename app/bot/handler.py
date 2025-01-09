from functools import wraps  # Импортируем функцию для создания декораторов

# Импортируем необходимые модули из aiogram для обработки Telegram-сообщений
from aiogram import F, Router, types
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# Импортируем модули для работы с базой данных, создания изображений и генерации текста
from config import FONTS_PATH, MEMES_PATH
from db import data_func
from utils import image_create
from app.ml import text_gen

# Создаем роутер для регистрации хэндлеров
router = Router()

# Декоратор для проверки авторизации пользователя
def require_auth(func):
    """
    Декоратор, проверяющий, авторизован ли пользователь.
    Если пользователь не авторизован, перенаправляет его в функцию `start`.
    """
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        chat_id = message.chat.id
        if not await data_func.is_user_added(chat_id):  # Проверяем авторизованность
            await start(message)  # Если нет, вызываем функцию приветствия
        else:
            return await func(message, *args, **kwargs)  # Если да, выполняем исходную функцию
    return wrapper

# Обработчик команды /start
@router.message(F.text == '/start')
async def start(message: Message):
    """
    Обрабатывает команду /start.
    Если пользователь не авторизован, предлагает ввести токен для авторизации.
    """
    chat_id = message.chat.id
    if not await data_func.is_user_added(chat_id):  # Проверяем, авторизован ли пользователь
        await message.answer(
            "Привет! С помощью этого бота ты можешь сгенерировать мем!\n"
            "Но сначала введи свой уникальный токен!"
        )
    else:
        await message.answer('Вы уже авторизованы!')  # Если авторизован, уведомляем об этом

# Обработчик команды /stop
@router.message(F.text == '/stop')
@require_auth  # Проверяем, авторизован ли пользователь
async def stop(message: Message):
    """
    Обрабатывает команду /stop.
    Выполняет логаут пользователя, удаляя его токен из базы данных.
    """
    chat_id = message.chat.id
    token = await data_func.get_token(chat_id)  # Получаем токен пользователя
    await data_func.logout_user(token)  # Удаляем токен из базы
    await message.answer('Выполнен логаут!')  # Уведомляем пользователя

# Обработчик аутентификации (сообщения, начинающиеся с '#')
@router.message(F.text[0] == '#')
async def auth(message: Message):
    """
    Обрабатывает сообщения с токенами (начинаются с '#').
    Выполняет проверку токена и добавляет пользователя в базу данных, если он не авторизован.
    """
    chat_id = message.chat.id
    token = message.text

    if not await data_func.is_token_valid(token):  # Проверяем валидность токена
        await message.answer('Неверный токен!')
    elif await data_func.is_user_added(chat_id):  # Проверяем, не авторизован ли пользователь
        await message.answer('Вы уже авторизованы!')
    elif await data_func.is_token_authorized(token):  # Проверяем, не занят ли токен
        await message.answer('Этот токен уже занят!')
    else:
        await data_func.auth_user(chat_id, token)  # Авторизуем пользователя
        await message.answer('Вы успешно авторизовались!')

# Обработчик команды /model
@router.message(F.text == '/model')
@require_auth  # Проверяем, авторизован ли пользователь
async def model_sel(message: Message):
    """
    Обрабатывает команду /model.
    Отправляет пользователю клавиатуру с выбором модели.
    """
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Llava", callback_data="llava"),
                InlineKeyboardButton(text="Phi-3", callback_data="phi"),
            ]
        ]
    )
    await message.answer(
        "Выберите модель, которую хотите использовать:",
        reply_markup=inline_keyboard
    )

# Обработчик нажатия кнопок выбора модели
@router.callback_query(lambda c: c.data in ["llava", "phi"])
async def button_callback_handler(callback_query: types.CallbackQuery):
    """
    Обрабатывает выбор модели.
    Обновляет модель пользователя в базе данных в зависимости от нажатой кнопки.
    """
    model = callback_query.data  # Получаем выбранную модель из данных коллбэка
    await data_func.update_model(callback_query.message.chat.id, model)  # Сохраняем модель в базе
    await callback_query.answer(f"Вы выбрали модель {model.capitalize()}")  # Уведомляем пользователя

# Обработчик всех остальных сообщений
@router.message()
@require_auth  # Проверяем, авторизован ли пользователь
async def any_message(message: Message):
    """
    Обрабатывает любые сообщения.
    Генерирует текст и изображение на основе сообщения пользователя и выбранной модели.
    """
    chat_id = message.chat.id
    model = await data_func.get_model(chat_id)  # Получаем выбранную модель пользователя

    msg = await text_gen.generate_text(model, message.text)  # Генерируем текст на основе сообщения

    # Создаем изображение с текстом
    await image_create.add_text_to_image(
        msg,
        f"{FONTS_PATH}/Andy_Bold_0.otf",
        32,
        (0, 0, 0),  # Цвет текста
        (0, 300, 0),
        chat_id
    )

    # Отправляем сгенерированное изображение пользователю
    photo = FSInputFile(f'{MEMES_PATH}/{chat_id}.jpg')
    await message.answer_photo(photo=photo)
