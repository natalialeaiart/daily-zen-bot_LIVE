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
    "Symbolic concept of {theme}: a vibrant minimalist aesthetic with lifelike elements. Clean lines, rich, harmonious colors, elegant vertical composition, full bleed, high detail, inspiring, 9:16 aspect ratio. Purely visual, no text elements.",
    "Symbolic concept of {theme}: photorealistic style infused with an artistic, aesthetic touch. Bright, natural lighting, vivid and appealing colors, perhaps a subtle touch of wonder, tall vertical image, highly detailed, immersive, 9:16 aspect ratio.Purely visual, no text elements.",
    "Symbolic concept of {theme}: modern aesthetic illustration, featuring a bold and beautiful color palette. Clean, contemporary design, an uplifting and lifelike feel, distinct vertical format, edge-to-edge clarity, 9:16 aspect ratio.Purely visual, no text elements.",
    "Symbolic concept of {theme}: serene and colorful aesthetic, blending elegant minimalism with organic, lifelike forms. Soft, diffused lighting creating a gentle mood, beautiful color gradients, elegant tall vertical design, high detail, 9:16 aspect ratio.Purely visual, no text elements.",
    "Symbolic concept of {theme}: a beautifully illustrated vertical scene, realistic yet imbued with a touch of artistic flair and wonder. Rich, vibrant, and lifelike colors, clear focus on the theme, minimalist yet meaningful background elements, highly detailed, 9:16 aspect ratio.Purely visual, no text elements."
]
CURRENT_STYLE_INDEX_FILE = 'current_style_index.txt'

# --- Категории и стили для Задания Дня ---
THOUGHT_CATEGORIES = [
    "философия", "юмор жизни", "самопознание", "минимализм", "психология",
    "осознанность", "бизнес", "творчество", "критическое мышление",
    "мотивация", "эмоциональный интеллект", "лидерство"
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
    }
}
# --- Функции для работы с файлами ---
def read_song_list(filename):
    items = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    items.append(line)
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Список песен будет пуст.")
        return []
    except Exception as e:
        print(f"Ошибка чтения файла {filename}: {e}")
        return []
    return items

def read_current_index(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return int(content) if content else -1
    except FileNotFoundError:
        print(f"Файл индекса {filename} не найден. Начнем с начала.")
        return -1 # Начать с первого элемента, если файл не найден
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

# --- Определение темы и генерация изображения через Replicate ---
theme_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Вот текст:\n\n{text_thought}\n\nОпредели его главную тему одним-двумя словами (на английском) для генерации изображения."}]
)
theme_for_image = theme_response.choices[0].message.content.strip()
print(f"Тема для изображения: {theme_for_image}")

current_style_idx = read_current_index(CURRENT_STYLE_INDEX_FILE)
next_style_idx = (current_style_idx + 1) if current_style_idx != -1 else 0
if next_style_idx >= len(IMAGE_PROMPT_STYLES):
    next_style_idx = 0

selected_style_template = IMAGE_PROMPT_STYLES[next_style_idx]
image_prompt = selected_style_template.replace("{theme}", theme_for_image)
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
    bot.send_message(chat_id=chat_id, text=quote_text) # Отправить только текст, если с картинкой проблема
    print(f"Мысль дня по теме '{selected_category}' отправлена без изображения.")


# --- Песня дня ---
youtube_songs = read_song_list(SONGS_FILE)
if youtube_songs:
    current_song_idx = read_current_index(INDEX_FILE)
    next_song_idx = (current_song_idx + 1) if current_song_idx != -1 else 0
    if next_song_idx >= len(youtube_songs):
        next_song_idx = 0

    if 0 <= next_song_idx < len(youtube_songs):
        song_url = youtube_songs[next_song_idx]
        bot.send_message(chat_id=chat_id, text=f"Song Of The Day - Песня Дня 🎧🌟\n\n{song_url}")
        write_current_index(INDEX_FILE, next_song_idx)
        print("Песня дня отправлена.")
    else:
        print(f"Ошибка: next_song_idx ({next_song_idx}) вышел за пределы списка песен (длина: {len(youtube_songs)}). Песня не отправлена.")
else:
    print("Список песен пуст или не найден. Песня дня не отправлена.")

# --- Генерация задания дня по теме ---
print(f"Генерация задания дня по теме: {selected_category}")

style_info = CATEGORY_STYLES.get(selected_category, {
    "personas": "опытный наставник",
    "tone_description": "вдохновляющий, ясный и полезный. Задание должно быть легким для выполнения и интересным.",
    "emojis": {"task": "💡", "benefit": "🌱", "action": "🚀"} # Дефолтные значения
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
    "- Не используй нумерованные или маркированные списки внутри описания задания, пользы или призыва к действию (кроме тех, что уже есть в структуре).\n"
    "- Пиши вдохновляюще, но без лишней 'воды'. Каждое слово должно быть на своем месте.\n"
    "- Убедись, что текст легко читается и понятен широкой аудитории.\n"
    "- Не пиши никаких вступлений или заключений за пределами указанной структуры. Только три блока, как описано выше.\n"
    "- Уложи всё задание, пользу и призыв в короткий, ёмкий текст. Общий объем ответа должен быть небольшим.\n\n"
    f"Создай уникальное задание для темы «{selected_category}», строго следуя голосу {personas}, их тону ({tone_description}), и указанной структуре с эмодзи ({task_emoji}, {benefit_emoji}, {action_emoji}) и Markdown для заголовков."
)

task_response = client.chat.completions.create(
    model="gpt-4o-mini", # или gpt-4o для потенциально более качественных стилизаций
    messages=[{"role": "user", "content": task_prompt}]
)
generated_task_text = task_response.choices[0].message.content.strip()

# Формируем заголовок для поста с заданием
task_post_header = f"✨ *Задание дня: {selected_category.capitalize()}*"
# Итоговый текст поста (заголовок + сгенерированное задание)
# OpenAI уже должен вернуть текст с нужными заголовками и эмодзи по промпту.
# Поэтому просто отправляем то, что сгенерировано, добавив главный заголовок.

final_task_post = f"{task_post_header}\n\n{generated_task_text}"

try:
    bot.send_message(chat_id=chat_id, text=final_task_post, parse_mode='MarkdownV2')
    print("Задание дня отправлено.")
except telegram.error.BadRequest as e:
    print(f"Ошибка отправки задания дня с MarkdownV2: {e}")
    # Попытка отправить без форматирования или с HTML, если MarkdownV2 не удался
    # Убираем Markdown из текста перед повторной отправкой
    plain_text_task = final_task_post.replace("*", "") # Простое удаление звездочек
    bot.send_message(chat_id=chat_id, text=plain_text_task)
    print("Задание дня отправлено в простом текстовом формате после ошибки Markdown.")
except Exception as e:
    print(f"Непредвиденная ошибка при отправке задания дня: {e}")


print("Скрипт завершён.")
