import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Получаем токен
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"  # Публичный канал

# Парсим одну цитату с сайта
try:
    url = "https://www.championat.com/lifestyle/article-5100445-50-motiviruyuschih-i-vdohnovlyayuschih-citat-na-kazhdyj-den.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Ищем первый абзац с цитатой
    quotes = soup.find_all("li")
    quote_text = quotes[0].get_text(strip=True) if quotes else "Не удалось найти цитату."
    print("✅ Цитата получена:", quote_text)
except Exception as e:
    print("❌ Ошибка парсинга сайта:", e)
    quote_text = "Не удалось получить цитату."

# Отправка в Telegram
try:
    bot = Bot(token=telegram_token)
    bot.send_message(chat_id=chat_id, text=f"Цитата дня:\n\n{quote_text}")
    print("✅ Сообщение отправлено в Telegram.")
except Exception as e:
    print("❌ Ошибка отправки в Telegram:", e)
