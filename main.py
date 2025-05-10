import os
import telegram
from openai import OpenAI

# Инициализация
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = "@dailyzendose"

# 1. Генерация цитаты
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Сгенерируй одну мудрую цитату дня на английском языке. Это должна быть реальная цитата от известного человека, философа, автора книги или персонажа фильма. Укажи автора цитаты или источник. Затем переведи её на русский язык."}
    ]
)
quote = response.choices[0].message.content

# 2. Генерация изображения
image = client.images.generate(
    model="dall-e-3",
    prompt=quote,
    n=1,
    size="1024x1024"
)
image_url = image.data[0].url

# 3. Отправка в Telegram
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote)
