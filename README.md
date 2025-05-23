# ✨ Daily Zen Bot

[![Telegram Channel](https://img.shields.io/badge/Telegram-Join%20Channel-blue?logo=telegram)](https://t.me/dailyzendose)

Ежедневная порция вдохновения прямо в Telegram! Этот бот каждый день в **08:00 по Риге (GMT+3)** публикует:

*   Мудрую мысль по теме дня
*   AI-сгенерированное изображение (идеально для обоев на телефон и фона для сторис)
*   Полезное задание дня для личностного роста
*   "Песню дня" из тщательно подобранного плейлиста

## 🧠 Что публикует бот и какая от этого польза

Каждый день вы получаете:

*   **Мысль дня:** Короткое, вдохновляющее изречение в стиле философии, психологии, бизнеса, минимализма и т.д. Вдохновлено книгами, курсами и фильмами. Источник всегда указан. *Может стать отличной идеей для вашего собственного контента на день или темой для размышлений.*

    > Пример: Простота — это не отсутствие, а ясность. (Курс по минимализму от The School of Life)

*   **AI-изображение:** Визуально привлекательная вертикальная картинка (1024x1792), сгенерированная на основе темы дня с конкретными визуальными элементами. *Изображения идеально подходят для обоев на телефон или фона для сторис в социальных сетях. Их смело можно скачивать и использовать для личных целей.*

*   **Задание дня:** Практичное и легко выполнимое задание, которое поможет вам развиваться в соответствии с темой дня. *Выполняя эти задания, вы постепенно формируете полезные привычки и навыки.*

*   **Песня дня:** Тщательно отобранный трек из коллекции лучших песен на русском и английском языках — от давно забытых хитов до новых и популярных композиций. *Отличный способ расширить свой музыкальный кругозор и открыть для себя что-то новое.*

## 🎯 Ежедневные темы

Бот чередует следующие темы, чтобы каждый день приносил что-то новое:

*   Философия
*   Юмор жизни
*   Самопознание
*   Минимализм
*   Психология
*   Осознанность
*   Бизнес
*   Творчество
*   Критическое мышление
*   Мотивация
*   Эмоциональный интеллект
*   Лидерство
*   Спорт

> Важно: Темы не повторяются два дня подряд!

## 💡 Как использовать контент бота

*   **Изображения:** Скачивайте и используйте как обои для телефона, фон для сторис в Instagram/Telegram, или для личных проектов.
*   **Мысли дня:** Используйте как вдохновение для собственных постов, размышлений или дневниковых записей.
*   **Задания:** Выполняйте их для личностного роста и делитесь результатами в комментариях.
*   **Песни:** Добавляйте понравившиеся треки в свои плейлисты и открывайте для себя новую музыку.

## ⚙️ Как это работает?

*   **Автоматизация:** GitHub Actions запускает бота каждый день в **05:00 UTC (08:00 GMT+3)**.
*   **Генерация мысли:** OpenAI GPT-4o mini (через `openai.ChatCompletion`)
*   **Генерация изображения:** Stable Diffusion XL через Replicate API с конкретными визуальными элементами
*   **Публикация:** Telegram Bot API (используется `python-telegram-bot`)

## 🚀 Установка и настройка

Хотите запустить своего собственного Daily Zen Bot? Вот как:

1.  **Клонируйте репозиторий:**

    ```bash
    git clone https://github.com/your-username/daily-zen-bot.git
    cd daily-zen-bot
    ```

2.  **Настройте секреты GitHub Actions:**

    Перейдите в `Settings > Secrets > Actions` вашего репозитория и добавьте следующие секреты:

    *   `OPENAI_API_KEY`:  Ваш ключ API OpenAI.
    *   `TELEGRAM_BOT_TOKEN`: Токен вашего Telegram-бота.
    *   `REPLICATE_API_TOKEN`: Ваш ключ API Replicate.

3.  **Установите зависимости:**

    Убедитесь, что у вас установлены необходимые библиотеки Python:

    ```bash
    pip install -r requirements.txt
    ```

    Файл `requirements.txt` должен содержать:

    ```
    openai
    python-telegram-bot
    replicate
    requests
    ```

4.  **Готово!**

    Файл `.github/workflows/daily.yml` уже настроен для ежедневного запуска бота. GitHub Actions автоматически запустит бота в указанное время.

## ✅ Пример вывода бота

**Мысль дня (минимализм):**

> Простота — это не отсутствие, а ясность.
>
> (Курс по минимализму от The School of Life)

*(Вместе с AI-изображением, заданием дня и "Песней дня")*

## 👩‍💻 Об Авторе

Этот бот создан с любовью и интеллектом: [@natalialeaiart](https://t.me/natalialeaiart)

Присоединяйтесь к Telegram-каналу для ежедневной дозы вдохновения: [@dailyzendose](https://t.me/dailyzendose)
