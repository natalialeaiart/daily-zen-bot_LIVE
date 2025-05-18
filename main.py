import os
import telegram
from openai import OpenAI
# Импортируем os для работы с файлами, уже есть

# --- Настройки API и канала ---
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose" # Убедитесь, что это корректное @имя_канала или ID

client = OpenAI(api_key=openai_api_key)
bot = telegram.Bot(token=telegram_token)

# --- Настройки для Песни дня ---
SONGS_FILE = 'youtube_songs.txt' # Имя файла со списком песен
INDEX_FILE = 'current_song_index.txt' # Имя файла для хранения текущего индекса песни

# --- Настройки для Стилей Изображений ---
# Список стилей для генерации изображений.
# В каждом стиле должен быть плейсхолдер {theme}, куда будет подставляться тема цитаты.
IMAGE_PROMPT_STYLES = [
    # Стиль 1: Яркий Живой Минимализм (без упоминания телефона)
    "Symbolic concept of {theme}: a vibrant minimalist aesthetic with lifelike elements. Clean lines, rich, harmonious colors, elegant vertical composition, full bleed, high detail, inspiring, 9:16 aspect ratio. Purely visual, no text elements.",
    
    # Стиль 2: Эстетичный Фотореализм (без упоминания телефона)
    "Symbolic concept of {theme}: photorealistic style infused with an artistic, aesthetic touch. Bright, natural lighting, vivid and appealing colors, perhaps a subtle touch of wonder, tall vertical image, highly detailed, immersive, 9:16 aspect ratio.Purely visual, no text elements.",
    
    # Стиль 3: Современная Красочная Иллюстрация (без упоминания телефона)
    "Symbolic concept of {theme}: modern aesthetic illustration, featuring a bold and beautiful color palette. Clean, contemporary design, an uplifting and lifelike feel, distinct vertical format, edge-to-edge clarity, 9:16 aspect ratio.Purely visual, no text elements.",
    
    # Стиль 4: Органический и Безмятежный Минимализм (без упоминания телефона)
    "Symbolic concept of {theme}: serene and colorful aesthetic, blending elegant minimalism with organic, lifelike forms. Soft, diffused lighting creating a gentle mood, beautiful color gradients, elegant tall vertical design, high detail, 9:16 aspect ratio.Purely visual, no text elements.",
    
    # Стиль 5: Художественная и Реалистичная Иллюстрация (без упоминания телефона)
    "Symbolic concept of {theme}: a beautifully illustrated vertical scene, realistic yet imbued with a touch of artistic flair and wonder. Rich, vibrant, and lifelike colors, clear focus on the theme, minimalist yet meaningful background elements, highly detailed, 9:16 aspect ratio.Purely visual, no text elements."
]

# Файл для индекса текущего стиля
CURRENT_STYLE_INDEX_FILE = 'current_style_index.txt'


# --- Вспомогательные функции для работы с файлами (остаются те же) ---
# Эти функции теперь будут использоваться и для индекса песен, и для индекса стилей.
def read_song_list(filename):
    """Читает список URL из файла, игнорируя пустые строки и комментарии."""
    items = [] # Изменено имя переменной на более общее
    print(f"Попытка чтения списка из файла: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    items.append(line)
        print(f"Успешно прочитано {len(items)} строк из '{filename}'.")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.")
        return []
    except Exception as e:
        print(f"Ошибка при чтении файла '{filename}': {e}")
        return []
    return items

def read_current_index(filename):
    """Читает текущий индекс из файла (для песен или стилей)."""
    print(f"Попытка чтения текущего индекса из файла: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                index = int(content)
                print(f"Успешно прочитан индекс {index} из файла '{filename}'.")
                return index
            else:
                print(f"Файл индекса '{filename}' пуст.")
                return -1 
    except FileNotFoundError:
        print(f"Файл индекса '{filename}' не найден. Начнем с 0.")
        return -1 
    except ValueError:
        print(f"Предупреждение: Файл индекса '{filename}' содержит нечисловые данные. Начнем с 0.")
        return -1
    except Exception as e:
        print(f"Ошибка при чтении файла индекса '{filename}': {e}")
        return -1


def write_current_index(filename, index):
    """Записывает текущий индекс в файл (для песен или стилей)."""
    print(f"Попытка записи индекса {index} в файл: {filename}")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(index))
        print(f"Индекс {index} успешно записан в файл '{filename}'.")
    except Exception as e:
        print(f"Ошибка записи файла индекса '{filename}': {e}")

# --- Основной код бота ---
print("Начало выполнения скрипта.")

# 1. Жёсткий промпт для цитаты
# ... (ваш код для шага 1 остается без изменений) ...
prompt = (
    "Сгенерируй одну мудрую цитату дня от известного человека, писателя, философа, героя книги, фильма и т.д. Важно, чтоб цитата была позитивной, вдохновляющей, мудрой и/или с юмором. "
    "Сначала напиши её на английском языке, затем переведи на русский. "
    "Строго в следующем формате:\n\n"
    "\"Английская цитата\" — Автор\n\"Русская цитата\" — Автор"
)
print("Запрос цитаты у GPT-4o...")
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    # 2. Разбор цитаты
    # ... (ваш код для шага 2 остается без изменений) ...
    text = response.choices[0].message.content.strip()
    lines = [line for line in text.split("\n") if line.strip()]
    english = lines[0].strip('"') if len(lines) >= 1 else ""
    russian = lines[1].strip('"') if len(lines) >= 2 else ""
    print("Цитата сгенерирована и разобрана.")
    
    # 3. Финальное сообщение для цитаты
    # ... (ваш код для шага 3 остается без изменений) ...
    quote_text = f"Quote of the day:\n\n{english}\n\nЦитата дня:\n\n{russian}" if english and russian else english or text
    print(f"Финальный текст цитаты готов:\n---\n{quote_text}\n---")

    # 4. Извлечение темы для изображения
    # ... (ваш код для шага 4 остается без изменений) ...
    print("Извлечение темы цитаты для изображения...")
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
    print(f"Тема цитаты определена: {theme}")

    # --- ВЫБОР СТИЛЯ ИЗОБРАЖЕНИЯ ---
    print("\n--- Выбор стиля для изображения ---")
    current_style_idx = read_current_index(CURRENT_STYLE_INDEX_FILE) 
    
    next_style_idx = current_style_idx + 1 if current_style_idx is not None and current_style_idx != -1 else 0
    if next_style_idx >= len(IMAGE_PROMPT_STYLES):
        next_style_idx = 0 # Начинаем сначала, если достигли конца списка стилей
        print("Достигнут конец списка стилей, сброс индекса стиля на 0.")
    
    selected_style_template = IMAGE_PROMPT_STYLES[next_style_idx]
    # Заменяем {theme} в выбранном стиле на актуальную тему
    image_generation_prompt = selected_style_template.replace("{theme}", theme) 
    
    print(f"Выбран шаблон стиля (индекс {next_style_idx}): {selected_style_template}")
    print(f"Финальный промпт для генерации изображения: {image_generation_prompt}")

    # 5. Генерация изображения
    print("Запрос генерации изображения у DALL-E 3...")
    image = client.images.generate(
        model="dall-e-3",
        prompt=image_generation_prompt, # Используем собранный промпт с выбранным стилем
        n=1,
        size="1024x1792" # Вертикальный размер
    )
    image_url = image.data[0].url
    print(f"Изображение сгенерировано. URL: {image_url}")

    # Сохраняем новый индекс стиля ПОСЛЕ успешной генерации изображения
    write_current_index(CURRENT_STYLE_INDEX_FILE, next_style_idx)
    print(f"Новый индекс стиля {next_style_idx} записан в файл '{CURRENT_STYLE_INDEX_FILE}'.")

    # 6. Отправка первого поста (Фото + Цитата)
    print("Попытка отправки первого поста (Фото + Цитата) в Telegram...")
    bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote_text)
    print("Первый пост (Фото + Цитата) отправлен успешно.")

except Exception as e:
    print(f"Критическая ошибка на шаге генерации/отправки цитаты/изображения: {e}")
    # Если произошла ошибка (например, с генерацией изображения),
    # индекс стиля НЕ будет обновлен в этой сессии, чтобы в следующий раз,
    # возможно, попытаться снова с этим же стилем или после исправления проблемы.


# --- 7. Подготовка и отправка второго поста (Песня дня) ---
# ... (ваш код для шага 7 остается без изменений, как в предыдущих версиях) ...
print("\n--- Начинаем подготовку к отправке 'Песни дня' ---")

youtube_songs = read_song_list(SONGS_FILE) # Функция read_song_list теперь более универсальна

if not youtube_songs:
    print(f"Не могу отправить 'Песню дня': список песен пуст или файл '{SONGS_FILE}' не найден или содержит ошибки.")
else:
    current_song_idx = read_current_index(INDEX_FILE) # Индекс для песен
    
    next_song_idx = current_song_idx + 1 if current_song_idx is not None and current_song_idx != -1 else 0
    if next_song_idx >= len(youtube_songs):
        next_song_idx = 0 
        print("Достигнут конец списка песен, сброс индекса песни на 0.")

    print(f"Рассчитан индекс песни для следующей отправки: {next_song_idx}")
    try:
        song_url = youtube_songs[next_song_idx]
        print(f"URL песни для отправки: {song_url}")
        print("Попытка отправки сообщения 'Песня дня' в Telegram...")
        bot.send_message(
            chat_id=chat_id,
            text=f"Song Of The Day - Песня Дня 🎧🌟\n\n{song_url}"
        )
        print("'Песня дня' сообщение отправлено успешно.")
        write_current_index(INDEX_FILE, next_song_idx) # Сохраняем индекс песни
        print(f"Новый индекс песни {next_song_idx} успешно записан в файл '{INDEX_FILE}'.")
    except IndexError:
         print(f"Ошибка: Индекс песни {next_song_idx} вне диапазона ({len(youtube_songs)} песен). Проверьте файл '{SONGS_FILE}'.")
    except Exception as e:
        print(f"ПРОИЗОШЛА ОШИБКА ПРИ ОТПРАВКЕ ПЕСНИ ДНЯ ИЛИ ЗАПИСИ ИНДЕКСА ПЕСНИ: {e}")
        print(f"Индекс песни ({next_song_idx}) НЕ БЫЛ обновлен в файле '{INDEX_FILE}'.")

print("\nВыполнение скрипта завершено.")
# Конец скрипта
