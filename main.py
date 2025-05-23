import os
import telegram
import random
import replicate
from openai import OpenAI

# --- Настройки API и канала ---
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose" # Замените на ваш chat_id, если нужно

client = OpenAI(api_key=openai_api_key)
bot = telegram.Bot(token=telegram_token)
replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

# --- Настройки для Песни дня ---
SONGS_FILE = 'youtube_songs.txt'
INDEX_FILE = 'current_song_index.txt'

# --- Настройки для Стилей Изображений ---
IMAGE_PROMPT_STYLES = [
    "Visual representation of {theme} featuring {visual_element}: a vibrant minimalist aesthetic with lifelike elements. Clean lines, rich, harmonious colors, elegant vertical composition, full bleed, high detail, inspiring, 9:16 aspect ratio. Purely visual, no text elements.",
    "Visual representation of {theme} featuring {visual_element}: photorealistic style infused with an artistic, aesthetic touch. Bright, natural lighting, vivid and appealing colors, perhaps a subtle touch of wonder, tall vertical image, highly detailed, immersive, 9:16 aspect ratio. Purely visual, no text elements.",
    "Visual representation of {theme} featuring {visual_element}: modern aesthetic illustration, featuring a bold and beautiful color palette. Clean, contemporary design, an uplifting and lifelike feel, distinct vertical format, edge-to-edge clarity, 9:16 aspect ratio. Purely visual, no text elements.",
    "Visual representation of {theme} featuring {visual_element}: serene and colorful aesthetic, blending elegant minimalism with organic, lifelike forms. Soft, diffused lighting creating a gentle mood, beautiful color gradients, elegant tall vertical design, high detail, 9:16 aspect ratio. Purely visual, no text elements.",
    "Visual representation of {theme} featuring {visual_element}: a beautifully illustrated vertical scene, realistic yet imbued with a touch of artistic flair and wonder. Rich, vibrant, and lifelike colors, clear focus on the theme, minimalist yet meaningful background elements, highly detailed, 9:16 aspect ratio. Purely visual, no text elements."
]
CURRENT_STYLE_INDEX_FILE = 'current_style_index.txt'

# --- Категории и стили для Задания Дня ---
THOUGHT_CATEGORIES = [
    "философия", "юмор жизни", "самопознание", "минимализм", "психология",
    "осознанность", "бизнес", "творчество", "критическое мышление",
    "мотивация", "эмоциональный интеллект", "лидерство", "Спорт"
]
LAST_TOPIC_FILE = "last_topic.txt"

CATEGORY_STYLES = {
    "философия": {
        "personas": "Сенека, Алан Уоттс и Марк Аврелий",
        "tone_description": "размышляющий, вечный, наблюдающий. Задания должны касаться «смысла» и перспективы времени. Используй глубокие, но понятные метафоры, говори спокойно и мудро.",
        "emojis": {"task": "📜", "benefit": "⏳", "action": "🌌"}
    },
    "юмор жизни": {
        "personas": "Курт Воннегут, Джен Синсеро и Райан Холидей (с легкостью)",
        "tone_description": "ироничный, лёгкий, меткий. Задания должны вызывать «улыбку сквозь мудрость». Добавь щепотку здорового сарказма или неожиданный, забавный поворот.",
        "emojis": {"task": "🎭", "benefit": "😉", "action": "😂"}
    },
    "самопознание": {
        "personas": "Брене Браун и Лиз Гилберт",
        "tone_description": "мягкий, интимный, честный. Задания должны быть в духе «поговори с собой по-настоящему». Поощряй уязвимость, самосострадание и принятие.",
        "emojis": {"task": "💬", "benefit": "💖", "action": "💌"}
    },
    "минимализм": {
        "personas": "The Minimalists (Джошуа Филдс Милберн и Райан Никодемус) и Мари Кондо",
        "tone_description": "ясный, лаконичный, освобождающий. Задания должны быть про «меньше — значит глубже». Фокусируйся на избавлении от лишнего и поиске радости в простоте.",
        "emojis": {"task": "🧹", "benefit": "🧘", "action": "✨"}
    },
    "психология": {
        "personas": "Карл Роджерс, Джордан Питерсон (в мягком, поддерживающем стиле) и Эрик Берн",
        "tone_description": "понимающий, объясняющий, с доброй глубиной. Задания — как ключики к пониманию себя и других. Используй аналогии из повседневной жизни, говори доступно.",
        "emojis": {"task": "🗝️", "benefit": "🧠", "action": "🤝"}
    },
    "осознанность": {
        "personas": "Тит Нат Хан, Ошо и Экхарт Толле",
        "tone_description": "медитативный, поэтичный, замедляющий. Задания — как глоток тишины. Используй образы природы, простые практики, говори спокойно и умиротворяюще.",
        "emojis": {"task": "🕊️", "benefit": "🌿", "action": "🌬️"}
    },
    "бизнес": {
        "personas": "Стивен Кови, Сет Годин и Тим Феррис",
        "tone_description": "чёткий, прагматичный, с искрой. Задания — микро-прокачки навыков и мышления. Предлагай конкретные, измеримые действия, вдохновляй на эффективность.",
        "emojis": {"task": "🎯", "benefit": "📈", "action": "💡"}
    },
    "творчество": {
        "personas": "Элизабет Гилберт, Остин Клеон и Нил Гейман",
        "tone_description": "вдохновляющий, поэтичный, дерзкий. Задания — как зажигалка воображения. Поощряй эксперименты, игру и выход за рамки привычного.",
        "emojis": {"task": "🎨", "benefit": "🌟", "action": "🚀"}
    },
    "критическое мышление": {
        "personas": "Даниэль Канеман, Юваль Ной Харари и Джордж Карлин (иногда с его прямотой)",
        "tone_description": "провокационный, логичный, с вызовом. Задания — как встряска для ума. Задавай неудобные вопросы, предлагай анализировать информацию и сомневаться.",
        "emojis": {"task": "🧐", "benefit": "⚖️", "action": "🤔"}
    },
    "мотивация": {
        "personas": "Тони Роббинс, Робин Шарма и Мэл Роббинс",
        "tone_description": "энергичный, страстный, фокусирующий. Задания — как заряд в спину. Используй повелительное наклонение, слова-активаторы и призывы к немедленному действию.",
        "emojis": {"task": "🔥", "benefit": "🏆", "action": "⚡"}
    },
    "эмоциональный интеллект": {
        "personas": "Сьюзан Дэвид и Маршалл Розенберг",
        "tone_description": "сочувствующий, глубоко человечный. Задания — мягкая прокачка внутренней чуткости к себе и другим. Фокусируйся на чувствах, потребностях и эмпатии.",
        "emojis": {"task": "👂", "benefit": "❤️‍🩹", "action": "🫂"}
    },
    "лидерство": {
        "personas": "Саймон Синек, Джон Максвелл и Брене Браун",
        "tone_description": "вдохновляющий, уверенный, с высокой планкой. Задания — выбор быть сильным и добрым одновременно. Говори о влиянии, ответственности и служении.",
        "emojis": {"task": "👑", "benefit": "🌍", "action": "🤝"}
    },
    "Спорт": {
        "personas": "Джеймс Клир (автор «Atomic Habits»), Дэвид Гоггинс (если нужен жёсткий мотиватор) и Келли Старрет (осознанный подход к телу)",
        "tone_description": "бодрый, телесный, прокачивающий. Задания должны быть как микрошаги к силе, выносливости и любви к движению. Подчеркни важность регулярности, маленьких побед и слушания своего тела.",
        "emojis": {"task": "🏋️‍♂️", "benefit": "💪", "action": "🏆"}
    }
}

# --- Шаблоны для подводок к Песне Дня ---
SONG_INTRO_TEMPLATES = [
    "Саундтрек к этому дню 🎶\nИногда песня становится больше, чем просто фоном. Вдруг это именно она?",
    "Твоя песня дня ✨\nСегодня она звучит просто так. Завтра — может стать воспоминанием.",
    "Музыкальная пауза 🎧\nУ каждого момента может быть свой звук. Может, именно этот зацепит?",
    "Мелодия момента 🎵\nСохрани это настроение. Иногда песня — это личная история в 3 минутах.",
    "Песня, которую ты можешь запомнить 🌟\nЕсли откликнется — пусть останется с тобой.",
    "Просто включи ▶️\nИногда нужная песня попадает вовремя. Возможно, как сейчас.",
    "Одна песня — один день 📀\nЗапиши её в память. Или просто слушай."
]

# --- Функции для работы с файлами ---
def read_song_list(filename):
    """
    Читает список песен из файла.
    Ожидаемый формат строки: Название Песни - Исполнитель|URL_ссылка
    """
    song_data_list = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('|', 1)  # Разделяем по первому символу '|'
                    if len(parts) == 2:
                        title = parts[0].strip()
                        url = parts[1].strip()
                        if title and url: # Убедимся, что обе части не пустые
                            song_data_list.append({"title": title, "url": url})
                        else:
                            print(f"Предупреждение: Пропущена некорректная строка (пустое название или URL): {line}")
                    else:
                        print(f"Предупреждение: Пропущена некорректная строка (отсутствует разделитель '|'): {line}")
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Список песен будет пуст.")
        return []
    except Exception as e:
        print(f"Ошибка чтения файла {filename}: {e}")
        return []
    return song_data_list

def read_current_index(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return int(content) if content else -1
    except FileNotFoundError:
        print(f"Файл индекса {filename} не найден. Начнем с начала.")
        return -1
    except ValueError:
        print(f"Ошибка значения в файле индекса {filename}. Начнем с начала.")
        return -1
    except Exception as e:
        print(f"Ошибка чтения файла индекса {filename}: {e}")
        return -1

def write_current_index(filename, index):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(index))
    except Exception as e:
        print(f"Ошибка записи индекса в файл {filename}: {e}")

# --- Генерация мудрой мысли дня ---
print("Начало выполнения скрипта.")

last_topic = None
if os.path.exists(LAST_TOPIC_FILE):
    with open(LAST_TOPIC_FILE, 'r', encoding='utf-8') as f:
        last_topic = f.read().strip()

available_topics = [t for t in THOUGHT_CATEGORIES if t != last_topic]
if not available_topics:
    available_topics = THOUGHT_CATEGORIES
selected_category = random.choice(available_topics)

with open(LAST_TOPIC_FILE, 'w', encoding='utf-8') as f:
    f.write(selected_category)

print(f"Выбрана категория для мысли и задания: {selected_category}")

prompt_thought = (
    f"Сгенерируй одну мудрую, вдохновляющую или философскую мысль на русском языке, "
    f"основанную на идеях из книги, курса, фильма, статьи или интервью по теме «{selected_category}». "
    "Это не должна быть цитата, а краткая мысль в духе источника. "
    "В конце обязательно укажи источник (в скобках). "
    "Формат ответа — только текст одной строки. Без вступлений и пояснений."
)

response_thought = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt_thought}]
)
text_thought = response_thought.choices[0].message.content.strip()
quote_text = f"Мысль дня ({selected_category}):\n\n{text_thought}"

# --- Определение темы и визуального элемента для генерации изображения ---
visual_prompt = (
    f"Вот текст:\n\n{text_thought}\n\n"
    f"1. Определи его главную тему одним-двумя словами (на английском) для генерации изображения.\n"
    f"2. Определи один конкретный визуальный образ или предмет, который хорошо передаёт смысл этого текста "
    f"и который легко нарисовать: например, предмет, жест, природное явление, понятный всем символ.\n\n"
    f"Формат ответа:\n"
    f"Тема: [тема на английском]\n"
    f"Визуальный элемент: [описание конкретного визуального элемента на английском]"
)

theme_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": visual_prompt}]
)
theme_response_text = theme_response.choices[0].message.content.strip()
print(f"Ответ по теме и визуальному элементу: {theme_response_text}")

# Извлечение темы и визуального элемента из ответа
theme_for_image = "abstract concept"  # значение по умолчанию
visual_element = "symbolic representation"  # значение по умолчанию

for line in theme_response_text.split('\n'):
    if line.lower().startswith("тема:") or line.lower().startswith("theme:"):
        theme_for_image = line.split(':', 1)[1].strip()
    elif line.lower().startswith("визуальный элемент:") or line.lower().startswith("visual element:"):
        visual_element = line.split(':', 1)[1].strip()

print(f"Тема для изображения: {theme_for_image}")
print(f"Визуальный элемент: {visual_element}")

current_style_idx = read_current_index(CURRENT_STYLE_INDEX_FILE)
next_style_idx = (current_style_idx + 1) if current_style_idx != -1 else 0
if next_style_idx >= len(IMAGE_PROMPT_STYLES):
    next_style_idx = 0

selected_style_template = IMAGE_PROMPT_STYLES[next_style_idx]
image_prompt = selected_style_template.replace("{theme}", theme_for_image).replace("{visual_element}", visual_element)
print(f"Промпт для изображения: {image_prompt}")

try:
    output = replicate_client.run(
        "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",
        input={
            "prompt": image_prompt,
            "width": 1024,
            "height": 1792,
            "num_inference_steps": 30,
            "guidance_scale": 7.5
        }
    )
    image_url = output[0]
    write_current_index(CURRENT_STYLE_INDEX_FILE, next_style_idx)
    bot.send_photo(chat_id=chat_id, photo=image_url, caption=quote_text)
    print(f"Мысль дня и изображение по теме '{selected_category}' отправлены.")
except Exception as e:
    print(f"Ошибка при генерации или отправке изображения: {e}")
    bot.send_message(chat_id=chat_id, text=quote_text)
    print(f"Мысль дня по теме '{selected_category}' отправлена без изображения.")


# --- Песня дня ---
def read_song_links(filename):
    """Читает список ссылок из файла. Ожидает одну ссылку на строку."""
    links = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):
                    links.append(url)
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Список песен будет пуст.")
        return []
    except Exception as e:
        print(f"Ошибка чтения файла {filename}: {e}")
        return []
    return links

song_links = read_song_links(SONGS_FILE)
if song_links:
    current_song_idx = read_current_index(INDEX_FILE)
    next_song_idx = (current_song_idx + 1) if current_song_idx != -1 else 0
    if next_song_idx >= len(song_links):
        next_song_idx = 0

    if 0 <= next_song_idx < len(song_links):
        song_url = song_links[next_song_idx]
        selected_intro = random.choice(SONG_INTRO_TEMPLATES)
        song_post_text = f"{selected_intro}\n\n{song_url}"

        try:
            bot.send_message(chat_id=chat_id, text=song_post_text, disable_web_page_preview=False)
            write_current_index(INDEX_FILE, next_song_idx)
            print(f"Песня дня отправлена: {song_url}")
        except Exception as e:
            print(f"Ошибка при отправке песни дня: {e}")
    else:
        print(f"Ошибка: next_song_idx ({next_song_idx}) вышел за пределы списка ссылок (длина: {len(song_links)}). Песня не отправлена.")
else:
    print("Список песен пуст или некорректен. Песня дня не отправлена.")

# --- Генерация задания дня по теме ---
print(f"Генерация задания дня по теме: {selected_category}")

style_info = CATEGORY_STYLES.get(selected_category, {
    "personas": "опытный наставник",
    "tone_description": "вдохновляющий, ясный и полезный. Задание должно быть легким для выполнения и интересным.",
    "emojis": {"task": "💡", "benefit": "🌱", "action": "🚀"} 
})

personas = style_info["personas"]
tone_description = style_info["tone_description"]
task_emoji = style_info["emojis"]["task"]
benefit_emoji = style_info["emojis"]["benefit"]
action_emoji = style_info["emojis"]["action"]

task_prompt = (
    f"Ты — виртуальный наставник, который сегодня говорит голосом и мудростью {personas} по теме «{selected_category}». "
    f"Твоя задача — придумать одно небольшое, но очень полезное задание на день для этой темы.\n"
    f"Стиль изложения: {tone_description}.\n\n"
    "Задание должно быть:\n"
    "1. Легко выполнимым сегодня.\n"
    "2. Интересным и нескучным.\n"
    "3. По-настоящему полезным для человека.\n\n"
    "Структура твоего ответа ДОЛЖНА БЫТЬ СТРОГО следующей (используй именно эти эмодзи и Markdown для выделения заголовков жирным):\n"
    f"{task_emoji} *Задание дня:*\n[Здесь текст самого задания. Будь конкретным и ясным. Не более 2-3 предложений.]\n\n"
    f"{benefit_emoji} *В чём польза?*\n[Здесь короткое, но ёмкое объяснение, почему это задание стоит выполнить. Подчеркни ценность. Не более 1-2 предложений.]\n\n"
    f"{action_emoji} *Как действовать?*\n[Здесь призыв к действию. Предложи, как можно поделиться результатами или мыслями в комментариях (например, наблюдениями, фото, инсайтами, словами, впечатлениями). Сделай это приглашающим и мотивирующим. Не более 1-2 предложений.]\n\n"
    "ВАЖНО:\n"
    "- Не используй нумерованные или маркированные списки.\n"
    "- Не добавляй никаких других заголовков или разделов.\n"
    "- Не используй хештеги.\n"
    "- Не добавляй никаких вступлений или заключений.\n"
    "- Не обращайся к читателю по имени.\n"
    "- Не используй слова «сегодня» и «сегодняшний».\n"
    "- Не упоминай, что это задание от бота или ИИ.\n"
    "- Не используй слово «задание» в самом тексте задания."
)

response_task = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": task_prompt}]
)
text_task = response_task.choices[0].message.content.strip()

try:
    bot.send_message(chat_id=chat_id, text=text_task, parse_mode="Markdown")
    print(f"Задание дня по теме '{selected_category}' отправлено.")
except Exception as e:
    print(f"Ошибка при отправке задания дня: {e}")
    try:
        bot.send_message(chat_id=chat_id, text=text_task)
        print(f"Задание дня по теме '{selected_category}' отправлено без форматирования.")
    except Exception as e2:
        print(f"Критическая ошибка при отправке задания дня: {e2}")

print("Скрипт выполнен успешно.")
