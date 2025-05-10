import os
import telegram
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = "@dailyzendose"

# Запрос к OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                "Сгенерируй одну мудрую цитату дня на русском языке. "
                "Это должна быть реальная цитата от известного человека, философа, автора книги или персонажа фильма. "
                "Укажи автора цитаты или источник. Затем переведи её на английский язык."
            )
        }
    ]
)
content = response.choices[0].message.content

# Разделение на языки: предполагаем, что ответ содержит оба текста
# Ищем последнюю английскую кавычку и делим текст
parts = content.strip().split('\n')

# Простейшая логика — фильтрация без заголовков
english = next((line for line in parts if line.startswith('"') and "—" in line and all(ord(c) < 128 for c in line)), "")
russian = next((line for line in parts if line.startswith('"') and "—" in line and not all(ord(c) < 128 for c in line)), "")

# Финальный текст
caption = f"{english}\n\n{russian}"

# Генерация картинки
image = client.images.generate(
    model="dall-e-3",
    prompt=english or russian,
    n=1,
    size="1024x1024"
)
image_url = image.data[0].url

# Отправка в Telegram
bot.send_photo(chat_id=chat_id, photo=image_url, caption=caption)
