import os
from random import choice
from textwrap import wrap

# файл добавления текста на изображение
from PIL import Image, ImageDraw, ImageFont    # импорт библиотеки для работы с изображениями

from config import IMAGES_PATH, MEMES_PATH


async def add_text_to_image(text, font_path, font_size, text_color, text_position, chat_id):
    """
    Добавляет текст на случайное изображение и сохраняет его.

    Аргументы:
        text (str): Текст для добавления на изображение.
        font_path (str): Путь к файлу шрифта.
        font_size (int): Размер шрифта.
        text_color (tuple): Цвет текста в формате RGB (например, (0, 0, 0) для чёрного).
        text_position (tuple): Начальная позиция текста (x, y).
        chat_id (int): Уникальный идентификатор чата (используется для сохранения файла).
    """

    image_size = (480, 480)  # width, height

    # Перенос текста
    wrapped_text = wrap_text(text)

    # Открываем случайное изображение и изменяем его размер
    image = Image.open(select_random_image()).resize(image_size)
    draw = ImageDraw.Draw(image)

    # Создаём шрифт
    font = ImageFont.truetype(font_path, font_size)

    # Вычисляем размеры текста
    bbox = draw.textbbox(text_position, wrapped_text, font=font)

    # Получаем координаты рамки текста
    bbox_width = bbox[2] - bbox[0]
    bbox_height = bbox[3] - bbox[1]

    # Рассчитываем координаты текста
    x1 = (image_size[0] - bbox_width) / 2
    y1 = image_size[1] - bbox_height - 5  # 5 для интерлиньяжа, иначе текст криво наложится на рамку
    x2 = x1 + bbox_width
    y2 = y1 + bbox_height + 5  # 5 для интерлиньяжа, иначе текст криво наложится на рамку

    # Рисуем белый фон для текста
    draw.rectangle(
        xy=(x1, y1, x2, y2),
        fill="white"
    )

    # Добавляем текст поверх фона
    draw.text((x1, y1), wrapped_text, font=font, fill=text_color)

    image.save(f'{MEMES_PATH}/{chat_id}.jpg')    # сохраняем изображение пользователя с id чата в названии


def select_random_image():
    """Выбирает случайное изображение из предопределённого списка."""
    template_meme_images = os.listdir(IMAGES_PATH)
    return f'{IMAGES_PATH}/{choice(template_meme_images)}'


def wrap_text(text, line_width=32):
    """Переносит текст, чтобы он помещался в заданную ширину."""
    return '\n'.join(wrap(text, line_width))
