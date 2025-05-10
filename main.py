import openai
import requests
import telegram
import os

# Настройка переменных
openai.api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"  # Имя канала

# 1. Сгенерировать цитату
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "Сгенерируй одну мудрую цитату дня на русском языке. Это должна быть реальная цитата от известного человека, философа, автора книги или персонажа фильма. Укажи автора цитаты или источник. Затем переведи её на английский язык."}
    ]
)
quote = response['choices'][0]['message']['content']

# 2. Сгенерировать картинку с цитатой
image_response = openai.Image.create(
    prompt=quote,
    model="dall-e-3",
    n=1,
    size="1024x1024"
)
image_url = image_response['data'][0]['url']

# 3. Отправить в Telegram
bot = telegram.Bot(token=telegram_token)
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote)
