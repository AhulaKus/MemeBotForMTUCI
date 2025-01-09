from langchain_ollama import ChatOllama  # Для взаимодействия с моделями Ollama
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler  # Обработчики для вывода результатов
from deep_translator import GoogleTranslator  # Для перевода текста

from ml.prompt import SYSTEM_PROMPT  # Системный промпт для модели


async def generate_text(model, message):
    """
    Генерирует текстовую шутку на основе входного сообщения.

    Аргументы:
        model (str): Название модели Ollama.
        message (str): Входное сообщение от пользователя.

    Возвращает:
        Сгенерированная шутка, переведённая на русский язык.
    """
    # Инициализация менеджера обратного вызова для обработки вывода
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    # Настройка модели Ollama
    llm = ChatOllama(
        model=model,         # Название используемой модели
        temperature=0.75,    # Коэффициент случайности (чем выше, тем более креативные ответы)
        max_tokens=2000,     # Максимальное количество токенов в ответе
        top_p=1,             # Параметр выборки токенов
        callback_manager=callback_manager,  # Менеджер обратного вызова
        verbose=True,        # Логирование операций
    )

    # Обработка входного сообщения:
    # Приведение к нижнему регистру, замена слова "мем" на "шутку"
    message = message.lower().replace('мем', 'шутку')

    # Перевод сообщения на английский язык для лучшего понимания моделью
    message = GoogleTranslator(source='auto', target='en').translate(message)

    # Формирование истории (контекста) для модели
    history = [
        {
            "role": "system",  # Системное сообщение для установки контекста
            "content": SYSTEM_PROMPT  # Установленный системный запрос из конфигурации
        },
        {
            "role": "user",  # Сообщение пользователя
            "content": f"{message}"  # Текст сообщения
        }
    ]

    # Генерация ответа с использованием модели Ollama
    msg = llm.invoke(history)

    # Перевод сгенерированного текста обратно на русский язык
    return GoogleTranslator(source='auto', target='ru').translate(msg.content)
