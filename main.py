import os
import telegram
from openai import OpenAI
# Импортируем os для работы с файлами, уже есть

openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"

client = OpenAI(api_key=openai_api_key)
bot = telegram.Bot(token=telegram_token)

# --- Настройки для Песни дня ---
SONGS_FILE = 'youtube_songs.txt' # Имя файла со списком песен
INDEX_FILE = 'current_song_index.txt' # Имя файла для хранения текущего индекса

# --- Вспомогательные функции для работы с файлами песен и индекса ---
def read_song_list(filename):
    """Читает список URL из файла, игнорируя пустые строки и комментарии."""
    songs = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Игнорируем пустые строки и строки, начинающиеся с # (для комментариев)
                if line and not line.startswith('#'):
                    songs.append(line)
    except FileNotFoundError:
        print(f"Ошибка: Файл со списком песен '{filename}' не найден.")
        # Вернем пустой список, чтобы основная логика могла это обработать
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла песен '{filename}': {e}")
        return []
    return songs

def read_current_index(filename):
    """Читает текущий индекс песни из файла."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                # Пытаемся прочитать число. Если не получается, считаем, что индекс некорректен.
                return int(content)
            else:
                # Файл пуст
                return -1
    except FileNotFoundError:
        # Файл не найден - это нормально для первого запуска
        return -1
    except ValueError:
        # Содержимое файла некорректно (не число)
        print(f"Предупреждение: Файл индекса '{filename}' содержит нечисловые данные. Начнем с 0.")
        return -1
    except Exception as e:
        print(f"Ошибка при чтении файла индекса '{filename}': {e}")
        return -1


def write_current_index(filename, index):
    """Записывает текущий индекс песни в файл."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(index))
    except Exception as e:
        print(f"Ошибка записи файла индекса '{filename}': {e}")

# --- Основной код бота ---

# 1. Жёсткий промпт для цитаты
prompt = (
    "Сгенерируй одну мудрую цитату дня от известного человека, писателя, философа, героя книги, фильма и т.д. Важно, чтоб цитата была позитивной, вдохновляющей, мудрой и/или с юмором. "
    "Сначала напиши её на английском языке, затем переведи на русский. "
    "Строго в следующем формате:\n\n"
    "\"Английская цитата\" — Автор\n\"Русская цитата\" — Автор"
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}]
)

# 2. Разбор цитаты
text = response.choices[0].message.content.strip()
lines = [line for line in text.split("\n") if line.strip()]
english = lines[0].strip('"') if len(lines) >= 1 else ""
russian = lines[1].strip('"') if len(lines) >= 2 else ""

# 3. Финальное сообщение для цитаты
quote_text = f"Quote of the day:\n\n{english}\n\nЦитата дня:\n\n{russian}" if english and russian else english or text

# 4. Извлечение темы для изображения
theme_response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": (
                f"Вот цитата:\n\n{english}\n\n"
                "Определи её главную тему одним словом или фразой (на английском)."
            )
        }
    ]
)
theme = theme_response.choices[0].message.content.strip()

# 5. Генерация изображения
image = client.images.generate(
    model="dall-e-3",
    prompt=f"Symbolic concept of {theme}, artistic rendering, elegant, high detail, blend of vintage and cybernetic aesthetics",
    n=1,
    size="1024x1024"
)
image_url = image.data[0].url

# 6. Отправка первого поста (Фото + Цитата)
try:
    bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote_text)
    print("Первый пост (Фото + Цитата) отправлен успешно.")
except Exception as e:
    print(f"Ошибка при отправке первого поста (Фото + Цитата): {e}")


# --- 7. Подготовка и отправка второго поста (Песня дня) ---

print("Подготовка к отправке 'Песни дня'...")

youtube_songs = read_song_list(SONGS_FILE)

if not youtube_songs:
    print(f"Не могу отправить 'Песню дня': список песен пуст или файл '{SONGS_FILE}' не найден или содержит ошибки.")
    # Опционально: отправить сообщение об ошибке в канал
    # try:
    #     bot.send_message(chat_id=chat_id, text="Не удалось загрузить список песен дня.")
    # except Exception as e_msg:
    #     print(f"Ошибка при отправке сообщения об ошибке списка песен: {e_msg}")

else:
    # Список песен загружен, приступаем к выбору следующей песни
    current_index = read_current_index(INDEX_FILE)
    print(f"Текущий сохраненный индекс песни: {current_index}")

    # Определяем индекс следующей песни
    # Если read_current_index вернул -1 (файл не найден или пуст/некорректен), начнем с индекса 0
    next_index = current_index + 1 if current_index is not None and current_index != -1 else 0

    # Реализация цикла: если next_index равен или больше количества песен, сбрасываем на 0
    if next_index >= len(youtube_songs):
        next_index = 0
        print("Достигнут конец списка песен, сброс индекса на 0.")

    # Получаем URL песни по рассчитанному индексу
    try:
        song_url = youtube_songs[next_index]

        # Отправляем сообщение с "Песней дня"
        print(f"Попытка отправки песни с индексом {next_index}: {song_url}")
        bot.send_message(
            chat_id=chat_id,
            text=f"✨ Песня дня ✨\n\n{song_url}"
        )
        print(f"'Песня дня' с индексом {next_index} отправлена успешно.")

        # Важно: Сохраняем НОВЫЙ индекс ПОСЛЕ успешной отправки
        write_current_index(INDEX_FILE, next_index)
        print(f"Новый индекс {next_index} успешно записан в файл '{INDEX_FILE}'.")

    except IndexError:
         print(f"Ошибка: Индекс песни {next_index} вне диапазона ({len(youtube_songs)} песен). Проверьте файл '{SONGS_FILE}'.")
         # Опционально: отправить сообщение об ошибке в канал
         # try:
         #     bot.send_message(chat_id=chat_id, text="Ошибка выбора песни дня. Проверьте список песен.")
         # except Exception as e_msg:
         #      print(f"Ошибка при отправке сообщения об ошибке выбора песни: {e_msg}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения с песней дня: {e}")
        # Если отправка не удалась, мы НЕ обновляем файл индекса,
        # чтобы бот попробовал отправить ту же песню в следующий раз.

# Конец скрипта
