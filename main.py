import os
import telegram
import random
import replicate
from openai import OpenAI

# --- Настройки API и канала ---
openai_api_key = os.getenv("OPENAI_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = "@dailyzendose"

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

# --- Функции для работы с файлами ---
def read_song_list(filename):
    items = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    items.append(line)
    except Exception:
        return []
    return items

def read_current_index(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return int(content) if content else -1
    except Exception:
        return -1

def write_current_index(filename, index):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(str(index))
    except Exception as e:
        print(f"Ошибка записи: {e}")

# --- Генерация мудрой мысли дня ---
print("Начало выполнения скрипта.")

THOUGHT_CATEGORIES = [
    "философия", "юмор жизни", "самопознание", "минимализм", "психология",
    "осознанность", "бизнес", "творчество", "критическое мышление",
    "мотивация", "эмоциональный интеллект", "лидерство"
]
LAST_TOPIC_FILE = "last_topic.txt"

last_topic = None
if os.path.exists(LAST_TOPIC_FILE):
    with open(LAST_TOPIC_FILE, 'r', encoding='utf-8') as f:
        last_topic = f.read().strip()

available_topics = [t for t in THOUGHT_CATEGORIES if t != last_topic]
selected_category = random.choice(available_topics)

with open(LAST_TOPIC_FILE, 'w', encoding='utf-8') as f:
    f.write(selected_category)

prompt = (
    f"Сгенерируй одну мудрую, вдохновляющую или философскую мысль на русском языке, "
    f"основанную на идеях из книги, курса, фильма, статьи или интервью по теме «{selected_category}». "
    "Это не должна быть цитата, а краткая мысль в духе источника. "
    "В конце обязательно укажи источник (в скобках). "
    "Формат ответа — только текст одной строки. Без вступлений и пояснений."
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)
text = response.choices[0].message.content.strip()
quote_text = f"Мысль дня ({selected_category}):\n\n{text}"

# --- Определение темы и генерация изображения через Replicate ---
theme_response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Вот цитата:\n\n{text}\n\nОпредели её главную тему одним словом или фразой (на английском)."}]
)
theme = theme_response.choices[0].message.content.strip()

current_style_idx = read_current_index(CURRENT_STYLE_INDEX_FILE)
next_style_idx = (current_style_idx + 1) if current_style_idx != -1 else 0
if next_style_idx >= len(IMAGE_PROMPT_STYLES):
    next_style_idx = 0

selected_style_template = IMAGE_PROMPT_STYLES[next_style_idx]
image_prompt = selected_style_template.replace("{theme}", theme)

output = replicate_client.run(
    "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc",  # новая актуальная версия без указания конкретного хэша
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

# --- Песня дня ---
youtube_songs = read_song_list(SONGS_FILE)
if youtube_songs:
    current_song_idx = read_current_index(INDEX_FILE)
    next_song_idx = (current_song_idx + 1) if current_song_idx != -1 else 0
    if next_song_idx >= len(youtube_songs):
        next_song_idx = 0

    song_url = youtube_songs[next_song_idx]
    bot.send_message(chat_id=chat_id, text=f"Song Of The Day - Песня Дня 🎧🌟\n\n{song_url}")
    write_current_index(INDEX_FILE, next_song_idx)

print("Скрипт завершён.")
