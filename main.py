import os
import requests
import telegram
from openai import OpenAI

# Настройка переменных окружения
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"

# Инициализация OpenAI клиента
client = OpenAI(api_key=openai_api_key)

# 1. Генерация цитаты через Chat API
chat_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Сгенерируй одну мудрую цитату дня на русском языке. Это должна быть реальная цитата от известного человека, философа, автора книги или персонажа фильма. Укажи автора цитаты или источник. Затем переведи её на английский язык."}
    ]
)
quote = chat_response.choices[0].message.content

# 2. Генерация изображения по этой цитате
image_response = client.images.generate(
    model="dall-e-3",
    prompt=quote,
    n=1,
    size="1024x1024"
)
image_url = image_response.data[0].url

# 3. Отправка в Telegram
bot = telegram.Bot(token=telegram_token)
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote)
