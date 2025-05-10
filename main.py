import os
import telegram
from openai import OpenAI

# Инициализация
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = "@dailyzendose"

# 1. Генерация цитаты (английский + перевод)
response = client.chat.completions.create(
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
quote = response.choices[0].message.content.strip()

# 2. Извлечь тему для изображения через GPT
theme_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                f"Вот цитата:\n\n{quote}\n\n"
                "Определи ключевую тему или смысл этой цитаты одним-двумя словами (например: courage, creativity, balance, time, love). "
                "Верни только английское слово или короткую фразу без пояснений."
            )
        }
    ]
)
theme = theme_response.choices[0].message.content.strip()

# 3. Генерация изображения по теме
image = client.images.generate(
    model="dall-e-3",
    prompt=f"Conceptual illustration of {theme}, minimal style, peaceful and inspiring",
    n=1,
    size="1024x1024"
)
image_url = image.data[0].url

# 4. Отправка в Telegram
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote)
