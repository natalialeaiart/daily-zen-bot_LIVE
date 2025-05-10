import os
import telegram
from openai import OpenAI

openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"

client = OpenAI(api_key=openai_api_key)
bot = telegram.Bot(token=telegram_token)

# 1. Жёсткий промпт: всегда верни 2 строки — англ + перевод
prompt = (
    "Сгенерируй одну мудрую цитату дня от известного человека. "
    "Сначала напиши её на английском языке, затем переведи на русский. "
    "Строго в следующем формате:\n\n"
    "\"Английская цитата\" — Автор\n\"Русская цитата\" — Автор"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)

# 2. Разбор: ожидаем 2 строки
text = response.choices[0].message.content.strip()
lines = [line for line in text.split("\n") if line.strip()]
english = lines[0].strip('"') if len(lines) >= 1 else ""
russian = lines[1].strip('"') if len(lines) >= 2 else ""

# 3. Финальное сообщение
quote_text = f"Quote of the day:\n\n{english}\n\nЦитата дня:\n\n{russian}" if english and russian else english or text

# 4. Извлечение темы
theme_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                f"Вот цитата:\n\n{english}\n\n"
                "Определи её главную тему одним словом (на английском)."
            )
        }
    ]
)
theme = theme_response.choices[0].message.content.strip()

# 5. Генерация изображения
image = client.images.generate(
    model="dall-e-3",
    prompt=f"Symbolic concept of {theme}, elegant, minimalist, inspiring style",
    n=1,
    size="1024x1024"
)
image_url = image.data[0].url

# 6. Отправка в Telegram
bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote_text)
