import os
from openai import OpenAI
from telegram import Bot
from telegram.constants import ParseMode

openai_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

client = OpenAI(api_key=openai_key)

# Генерация цитаты
try:
    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Ты генератор вдохновляющих, мудрых или юмористических цитат известных личностей. "
                    "Цитата должна быть от реально существующего человека (писатель, философ, актёр, спортсмен, политик). "
                    "Укажи имя автора. Переведи на английский. Не используй слова 'Russian' или 'English'."
                )
            },
            {
                "role": "user",
                "content": "Сгенерируй вдохновляющую цитату с автором на русском и английском языках."
            }
        ]
    )
    quote_text = chat_response.choices[0].message.content.strip()
    print("✅ Цитата сгенерирована.")
except Exception as e:
    print("❌ Ошибка генерации цитаты:", e)
    quote_text = "Не удалось сгенерировать цитату."

# Генерация изображения
try:
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=f"Нарисуй красивую вдохновляющую сцену, подходящую по смыслу к цитате: {quote_text}",
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = image_response.data[0].url
    print("✅ Картинка сгенерирована.")
except Exception as e:
    print("❌ Ошибка генерации изображения:", e)
    image_url = None

# Отправка в Telegram
bot = Bot(token=telegram_token)
chat_id = "@dailyzendose"  # Публичный канал

try:
    if image_url:
        bot.send_photo(chat_id=chat_id, photo=image_url)
    else:
        bot.send_message(chat_id=chat_id, text="(Изображение не сгенерировано)")

    bot.send_message(
        chat_id=chat_id,
        text=f"<b>Цитата дня:</b>\n\n{quote_text}",
        parse_mode=ParseMode.HTML
    )
    print("✅ Сообщения отправлены.")
except Exception as e:
    print("❌ Ошибка отправки в Telegram:", e)
