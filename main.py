import os
import telegram
from openai import OpenAI

# Настройки
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"

# Подключение
client = OpenAI(api_key=openai_api_key)
bot = telegram.Bot(token=telegram_token)

# Запрос цитаты
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                "Сгенерируй одну мудрую цитату дня на английском языке. "
                "Это должна быть реальная цитата от известного человека, философа, автора книги или персонажа фильма. "
                "Укажи автора. Затем переведи эту цитату на русский язык."
            )
        }
    ]
)

# Обработка
text = response.choices[0].message.content.strip()
lines = [line.strip() for line in text.split("\n") if line.strip()]
english = lines[0] if len(lines) > 0 else ""
russian = lines[1] if len(lines) > 1 else ""

# Финальный caption
quote_caption = f"Quote of the day:\n\n{english}\n\nЦитата дня:\n\n{russian}"

# Извлечение темы (по английской цитате)
theme_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                f"Выдели главную тему этой цитаты одним словом или короткой фразой:\n\n{english}\n\n"
                "Ответь только на английском, без пояснений."
            )
        }
    ]
)
theme = theme_response.choices[0].message.content.strip()

# Генерация картинки
image = client.images.generate(
    model="dall-e-3",
    prompt=f"Conceptual illustration of {theme}, minimalist style, calming colors",
    n=1,
    size="1024x1024"
)
image_url = image.data[0].url

# Отправка
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote_caption)
