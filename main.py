import os
import requests
import telegram
from openai import OpenAI

# Переменные окружения
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"

# OpenAI клиент
client = OpenAI(api_key=openai_api_key)

# Запрос к GPT
chat_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                "Сгенерируй одну мудрую цитату дня на английском языке. "
                "Это должна быть реальная цитата от известного человека, философа, автора книги или персонажа фильма. "
                "Укажи автора цитаты или источник. Затем переведи её на русский язык."
            )
        }
    ]
)

# Разбор ответа
text = chat_response.choices[0].message.content.strip()
lines = [line.strip() for line in text.split('\n') if line.strip()]
english = lines[0] if len(lines) > 0 else ""
russian = lines[1] if len(lines) > 1 else ""
quote = f"{english}\n\n{russian}"

# Генерация картинки
image_response = client.images.generate(
    model="dall-e-3",
    prompt=english or russian,
    n=1,
    size="1024x1024"
)
image_url = image_response.data[0].url

# Telegram отправка
bot = telegram.Bot(token=telegram_token)
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote)
