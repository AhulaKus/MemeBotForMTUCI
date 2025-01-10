## Основное
Проект является Telegram-бототом, который может самостоятельно составлять текст по запросу, выдавая пользователю картинку-мем.

## Установка
1. С сайта ollama необходимо скачать фреймворк:
### **https://ollama.com/download/windows**
   
2. Скачайте модели, которые будут использоватся в боте и запустите их:
   ```bash
   ollama pull phi3
   ```
   ```bash
   ollama pull llava
   ```
   ```bash
   ollama run phi3
   ```
   ```bash
   ollama run llava
   ```
   
3. Перейдите в директрорию с проектом:
   ```bash
   cd path
   ```

4. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv
   ```

5. Активируйте его:
   ```bash
   ./venv/bin/activate.exe
   ```

5. Установите зависимости:
   ```bash
   pip install -r requiremetns.txt
   ```

6. Зайдите в папку с ботом и запустите его:
   ```bash
   cd app
   ```
   ```bash
   python main.py
   ```
