import os
import json
import random
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import telegram
from openai import OpenAI

# Конфигурация файлов
TASK_HISTORY_FILE = "task_history.json"
TASK_TEMPLATES_FILE = "task_templates.json"
LAST_TOPIC_FILE = "last_topic.txt"

# Расширенная система категорий с подкатегориями
ENHANCED_CATEGORIES = {
    "минимализм": {
        "subcategories": [
            "избавление_от_вещей",
            "цифровой_детокс", 
            "упрощение_расписания",
            "осознанное_потребление",
            "ментальная_разгрузка",
            "организация_пространства"
        ],
        "personas": "The Minimalists (Джошуа Филдс Милберн и Райан Никодемус) и Мари Кондо",
        "tone": "ясный, лаконичный, освобождающий. Задания должны быть про «меньше — значит глубже». Сосредоточься на качестве, а не количестве.",
        "emojis": {"task": "✨", "benefit": "🌱", "action": "🚀"}
    },
    "психология": {
        "subcategories": [
            "эмоциональная_регуляция",
            "когнитивные_искажения",
            "межличностные_отношения", 
            "самопознание",
            "стресс_менеджмент",
            "привычки_и_поведение"
        ],
        "personas": "Карл Роджерс, Дэниел Канеман и Сьюзан Дэвид",
        "tone": "понимающий, научно обоснованный, поддерживающий. Задания — как ключи к пониманию себя и других. Используй мягкую глубину и эмпатию.",
        "emojis": {"task": "🧠", "benefit": "💡", "action": "🔍"}
    },
    "осознанность": {
        "subcategories": [
            "медитация_и_дыхание",
            "присутствие_в_моменте",
            "наблюдение_за_мыслями",
            "телесная_осознанность",
            "благодарность",
            "принятие_и_отпускание"
        ],
        "personas": "Тит Нат Хан, Джон Кабат-Зинн и Экхарт Толле",
        "tone": "медитативный, поэтичный, замедляющий. Задания — как глоток тишины. Используй образы природы и метафоры внутреннего пространства.",
        "emojis": {"task": "🧘", "benefit": "🌸", "action": "🌊"}
    },
    "творчество": {
        "subcategories": [
            "художественное_выражение",
            "письмо_и_поэзия",
            "музыка_и_звуки",
            "креативное_мышление",
            "импровизация",
            "ремесло_и_создание"
        ],
        "personas": "Элизабет Гилберт, Остин Клеон и Нил Гейман",
        "tone": "вдохновляющий, поэтичный, дерзкий. Задания — как зажигалка для воображения. Поощряй эксперименты и «красивые ошибки».",
        "emojis": {"task": "🎨", "benefit": "✨", "action": "🌈"}
    },
    "философия": {
        "subcategories": [
            "смысл_и_цель",
            "этика_и_мораль",
            "время_и_вечность",
            "свобода_и_ответственность",
            "истина_и_познание",
            "красота_и_эстетика"
        ],
        "personas": "Сенека, Алан Уоттс и Марк Аврелий",
        "tone": "размышляющий, вечный, наблюдающий. Задания должны касаться «смысла» и перспективы времени. Используй глубокие, но понятные метафоры.",
        "emojis": {"task": "📜", "benefit": "⏳", "action": "🌌"}
    },
    "самопознание": {
        "subcategories": [
            "ценности_и_убеждения",
            "сильные_стороны",
            "теневые_аспекты",
            "жизненная_история",
            "мечты_и_цели",
            "внутренний_диалог"
        ],
        "personas": "Карл Юнг, Брене Браун и Лиз Гилберт",
        "tone": "мягкий, интимный, честный. Задания должны быть в духе «поговори с собой по-настоящему». Поощряй уязвимость и самопринятие.",
        "emojis": {"task": "🪞", "benefit": "💎", "action": "🗝️"}
    },
    "бизнес": {
        "subcategories": [
            "продуктивность",
            "лидерство",
            "коммуникация",
            "принятие_решений",
            "инновации",
            "работа_в_команде"
        ],
        "personas": "Стивен Кови, Сет Годин и Тим Феррис",
        "tone": "четкий, прагматичный, с искрой. Задания — микро-прокачки навыков и мышления. Предлагай конкретные эксперименты с измеримыми результатами.",
        "emojis": {"task": "🎯", "benefit": "📈", "action": "⚡"}
    },
    "мотивация": {
        "subcategories": [
            "постановка_целей",
            "преодоление_препятствий",
            "энергия_и_драйв",
            "дисциплина",
            "вдохновение",
            "празднование_успехов"
        ],
        "personas": "Тони Роббинс, Мел Роббинс и Джеймс Клир",
        "tone": "энергичный, страстный, фокусирующий. Задания — как заряд в спину. Используй повелительные формы и призывы к действию.",
        "emojis": {"task": "🔥", "benefit": "💪", "action": "🚀"}
    },
    "эмоциональный_интеллект": {
        "subcategories": [
            "распознавание_эмоций",
            "эмпатия",
            "управление_реакциями",
            "социальные_навыки",
            "эмоциональная_гибкость",
            "конфликт_резолюция"
        ],
        "personas": "Дэниел Гоулман, Марк Брэкетт и Сьюзан Дэвид",
        "tone": "сочувствующий, глубоко человечный. Задания — мягкая прокачка внутренней чуткости к себе и другим. Задавай неудобные, но важные вопросы.",
        "emojis": {"task": "💝", "benefit": "🤝", "action": "💫"}
    },
    "лидерство": {
        "subcategories": [
            "влияние_и_вдохновение",
            "принятие_решений",
            "развитие_других",
            "видение_и_стратегия",
            "личный_пример",
            "адаптивность"
        ],
        "personas": "Саймон Синек, Джон Максвелл и Брене Браун",
        "tone": "вдохновляющий, уверенный, с высокой планкой. Задания — выбор быть сильным и добрым одновременно. Фокусируйся на служении другим.",
        "emojis": {"task": "👑", "benefit": "🌟", "action": "🎖️"}
    },
    "спорт": {
        "subcategories": [
            "физическая_активность",
            "ментальная_подготовка",
            "здоровые_привычки",
            "выносливость",
            "координация",
            "восстановление"
        ],
        "personas": "Джеймс Клир (автор «Atomic Habits»), Дэвид Гоггинс и Келли Старретт",
        "tone": "бодрый, телесный, прокачивающий. Задания должны быть как микроволны к силе, выносливости или гибкости. Поощряй движение и эксперименты.",
        "emojis": {"task": "💪", "benefit": "⚡", "action": "🏃"}
    },
    "юмор_жизни": {
        "subcategories": [
            "ирония_и_самоирония",
            "легкость_восприятия",
            "игривость",
            "абсурд_и_парадоксы",
            "смех_над_проблемами",
            "радость_в_мелочах"
        ],
        "personas": "Курт Воннегут, Джен Синсеро и Райан Холидей (с легкостью)",
        "tone": "ироничный, лёгкий, меткий. Задания должны вызывать «улыбку сквозь мудрость». Добавь щепотку здорового сарказма или неожиданный поворот.",
        "emojis": {"task": "😄", "benefit": "😉", "action": "🎭"}
    },
    "критическое_мышление": {
        "subcategories": [
            "анализ_информации",
            "логические_ошибки",
            "источники_и_факты",
            "альтернативные_точки_зрения",
            "системное_мышление",
            "принятие_решений"
        ],
        "personas": "Дэниел Канеман, Нассим Талеб и Джордан Питерсон (в мягком, поддерживающем стиле)",
        "tone": "провокационный, логичный, с вызовом. Задания — как встряска для ума. Задавай неудобные вопросы и предлагай альтернативы.",
        "emojis": {"task": "🤔", "benefit": "🧩", "action": "🔍"}
    }
}

# Типы заданий
TASK_TYPES = {
    "практическое": {
        "description": "Конкретные действия и упражнения",
        "examples": ["сделать", "попробовать", "создать", "организовать", "выполнить"],
        "duration": "15-30 минут",
        "focus": "действие и результат"
    },
    "рефлексивное": {
        "description": "Размышления и самоанализ", 
        "examples": ["подумать", "проанализировать", "вспомнить", "осознать", "поразмышлять"],
        "duration": "10-15 минут",
        "focus": "понимание и инсайты"
    },
    "творческое": {
        "description": "Креативные и художественные активности",
        "examples": ["нарисовать", "написать", "сочинить", "придумать", "создать"],
        "duration": "20-45 минут",
        "focus": "самовыражение и креативность"
    },
    "социальное": {
        "description": "Взаимодействие с другими людьми",
        "examples": ["поговорить", "поблагодарить", "помочь", "поделиться", "выразить"],
        "duration": "10-30 минут",
        "focus": "связь и отношения"
    },
    "наблюдательное": {
        "description": "Исследование и изучение окружающего мира",
        "examples": ["понаблюдать", "изучить", "исследовать", "заметить", "обратить внимание"],
        "duration": "15-25 минут",
        "focus": "осознанность и внимание"
    }
}

class TaskHistoryManager:
    """Управление историей заданий"""
    
    def __init__(self, history_file=TASK_HISTORY_FILE):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self):
        """Загрузка истории заданий"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "tasks": [],
            "last_categories": [],
            "category_usage_count": defaultdict(int),
            "subcategory_usage_count": defaultdict(int),
            "task_type_usage_count": defaultdict(int)
        }
    
    def save_history(self):
        """Сохранение истории заданий"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_task(self, category, subcategory, task_type, task_text):
        """Добавление нового задания в историю"""
        task_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "category": category,
            "subcategory": subcategory,
            "task_type": task_type,
            "task_text": task_text,
            "keywords": self.extract_keywords(task_text)
        }
        
        self.history["tasks"].append(task_entry)
        
        # Обновляем счетчики
        self.history["category_usage_count"][category] += 1
        self.history["subcategory_usage_count"][f"{category}:{subcategory}"] += 1
        self.history["task_type_usage_count"][task_type] += 1
        
        # Обновляем последние категории (храним последние 7)
        self.history["last_categories"].append(category)
        if len(self.history["last_categories"]) > 7:
            self.history["last_categories"] = self.history["last_categories"][-7:]
        
        self.save_history()
    
    def extract_keywords(self, text):
        """Извлечение ключевых слов из текста"""
        # Простое извлечение ключевых слов (можно улучшить с помощью NLP)
        words = re.findall(r'\b[а-яё]{4,}\b', text.lower())
        # Исключаем стоп-слова
        stop_words = {'этот', 'этого', 'этой', 'этому', 'этим', 'этом', 'этих', 'этими', 
                     'который', 'которая', 'которое', 'которые', 'которых', 'которым', 'которыми',
                     'можно', 'нужно', 'должен', 'должна', 'должно', 'должны', 'будет', 'будут',
                     'сегодня', 'завтра', 'вчера', 'сейчас', 'потом', 'тогда', 'здесь', 'там'}
        keywords = [word for word in words if word not in stop_words]
        return list(set(keywords))[:10]  # Максимум 10 ключевых слов
    
    def get_recent_categories(self, days=7):
        """Получение категорий, использованных в последние N дней"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tasks = [
            task for task in self.history["tasks"]
            if datetime.strptime(task["date"], "%Y-%m-%d") > cutoff_date
        ]
        return [task["category"] for task in recent_tasks]
    
    def get_recent_subcategories(self, category, days=14):
        """Получение подкатегорий для категории, использованных в последние N дней"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tasks = [
            task for task in self.history["tasks"]
            if (datetime.strptime(task["date"], "%Y-%m-%d") > cutoff_date and 
                task["category"] == category)
        ]
        return [task["subcategory"] for task in recent_tasks]
    
    def get_recent_task_types(self, days=5):
        """Получение типов заданий, использованных в последние N дней"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tasks = [
            task for task in self.history["tasks"]
            if datetime.strptime(task["date"], "%Y-%m-%d") > cutoff_date
        ]
        return [task["task_type"] for task in recent_tasks]
    
    def get_recent_keywords(self, days=7):
        """Получение ключевых слов из недавних заданий"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_tasks = [
            task for task in self.history["tasks"]
            if datetime.strptime(task["date"], "%Y-%m-%d") > cutoff_date
        ]
        all_keywords = []
        for task in recent_tasks:
            all_keywords.extend(task.get("keywords", []))
        return list(set(all_keywords))

class IntelligentTaskSelector:
    """Интеллектуальный выбор параметров задания"""
    
    def __init__(self, history_manager):
        self.history = history_manager
    
    def select_task_parameters(self):
        """Выбор категории, подкатегории и типа задания"""
        
        # 1. Выбор категории
        category = self._select_category()
        
        # 2. Выбор подкатегории
        subcategory = self._select_subcategory(category)
        
        # 3. Выбор типа задания
        task_type = self._select_task_type()
        
        return category, subcategory, task_type
    
    def _select_category(self):
        """Выбор категории с учетом истории"""
        # Исключаем категории, использованные в последние 7 дней
        recent_categories = self.history.get_recent_categories(days=7)
        available_categories = [
            cat for cat in ENHANCED_CATEGORIES.keys() 
            if cat not in recent_categories
        ]
        
        # Если все категории недавно использовались, берем все
        if not available_categories:
            available_categories = list(ENHANCED_CATEGORIES.keys())
        
        # Взвешенный выбор с учетом частоты использования
        category_weights = {}
        total_usage = sum(self.history.history["category_usage_count"].values()) or 1
        
        for category in available_categories:
            usage_count = self.history.history["category_usage_count"].get(category, 0)
            # Чем меньше использовалась категория, тем больше вес
            weight = max(1, total_usage - usage_count * 2)
            category_weights[category] = weight
        
        # Выбираем категорию с учетом весов
        categories = list(category_weights.keys())
        weights = list(category_weights.values())
        
        return random.choices(categories, weights=weights)[0]
    
    def _select_subcategory(self, category):
        """Выбор подкатегории с учетом истории"""
        subcategories = ENHANCED_CATEGORIES[category]["subcategories"]
        
        # Исключаем подкатегории, использованные в последние 14 дней для этой категории
        recent_subcategories = self.history.get_recent_subcategories(category, days=14)
        available_subcategories = [
            subcat for subcat in subcategories 
            if subcat not in recent_subcategories
        ]
        
        # Если все подкатегории недавно использовались, берем все
        if not available_subcategories:
            available_subcategories = subcategories
        
        return random.choice(available_subcategories)
    
    def _select_task_type(self):
        """Выбор типа задания с ротацией"""
        # Исключаем типы, использованные в последние 5 дней
        recent_types = self.history.get_recent_task_types(days=5)
        available_types = [
            task_type for task_type in TASK_TYPES.keys() 
            if task_type not in recent_types
        ]
        
        # Если все типы недавно использовались, берем все
        if not available_types:
            available_types = list(TASK_TYPES.keys())
        
        return random.choice(available_types)

class EnhancedPromptGenerator:
    """Генератор улучшенных промптов"""
    
    def __init__(self, history_manager):
        self.history = history_manager
    
    def create_prompt(self, category, subcategory, task_type):
        """Создание промпта с учетом истории и ограничений"""
        
        category_info = ENHANCED_CATEGORIES[category]
        task_type_info = TASK_TYPES[task_type]
        
        # Получаем недавние ключевые слова для исключения
        recent_keywords = self.history.get_recent_keywords(days=14)
        
        # Получаем примеры разнообразных подходов
        diverse_examples = self._get_diverse_examples(subcategory, task_type)
        
        prompt = f"""Ты — эксперт по теме "{category}" в стиле {category_info['personas']}.

ЗАДАЧА: Создай {task_type} задание по подтеме "{subcategory}".

ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
1. Задание должно быть уникальным и креативным
2. СТРОГО ИЗБЕГАЙ эти недавно использованные подходы и слова: {', '.join(recent_keywords[:15])}
3. Тип активности: {task_type_info['description']}
4. Время выполнения: {task_type_info['duration']}
5. Фокус: {task_type_info['focus']}

ПРИМЕРЫ РАЗНООБРАЗНЫХ ПОДХОДОВ для "{subcategory}":
{diverse_examples}

СТИЛЬ ИЗЛОЖЕНИЯ: {category_info['tone']}

СТРУКТУРА ОТВЕТА (используй именно эти эмодзи):
{category_info['emojis']['task']} *Задание дня:*
[Конкретное, уникальное задание. Максимум 2-3 предложения.]

{category_info['emojis']['benefit']} *В чём польза?*
[Краткое объяснение ценности. 1-2 предложения.]

{category_info['emojis']['action']} *Как действовать?*
[Призыв поделиться результатами в комментариях. 1-2 предложения.]

ВАЖНЫЕ ОГРАНИЧЕНИЯ:
- НЕ используй слова из списка исключений выше
- НЕ повторяй структуры типа "выбери один предмет/вещь"
- НЕ используй банальные формулировки
- БУДЬ креативным и неожиданным
- Весь текст ТОЛЬКО на русском языке
- НЕ используй слово "задание" в тексте самого задания"""

        return prompt
    
    def _get_diverse_examples(self, subcategory, task_type):
        """Получение примеров разнообразных подходов"""
        
        examples_map = {
            # Минимализм
            "избавление_от_вещей": [
                "Сфотографируй 5 предметов и расскажи их историю",
                "Создай капсульную коллекцию из 10 любимых вещей",
                "Устрой аукцион ненужных вещей среди друзей",
                "Примерь роль куратора музея для своего гардероба"
            ],
            "цифровой_детокс": [
                "Замени одно цифровое действие аналоговым",
                "Создай ритуал утреннего пробуждения без телефона",
                "Устрой час тишины без уведомлений",
                "Напиши письмо от руки вместо сообщения"
            ],
            
            # Психология
            "эмоциональная_регуляция": [
                "Создай карту своих эмоциональных триггеров",
                "Попрактикуй технику 'эмоциональный серфинг'",
                "Ведь диалог между разными частями себя",
                "Создай плейлист для разных эмоциональных состояний"
            ],
            
            # Осознанность
            "медитация_и_дыхание": [
                "Попрактикуй дыхание в ритме ходьбы",
                "Создай медитацию на основе звуков вокруг",
                "Попробуй дыхательную практику 4-7-8",
                "Медитируй с фокусом на одном органе чувств"
            ],
            
            # Творчество
            "художественное_выражение": [
                "Нарисуй свое настроение абстрактными формами",
                "Создай коллаж из случайных материалов",
                "Сделай скульптуру из подручных предметов",
                "Нарисуй портрет, не глядя на бумагу"
            ]
        }
        
        # Получаем примеры для конкретной подкатегории
        examples = examples_map.get(subcategory, [
            "Попробуй нестандартный подход к привычному действию",
            "Создай что-то новое из обычных материалов",
            "Исследуй тему через личный опыт",
            "Поэкспериментируй с необычной перспективой"
        ])
        
        # Фильтруем примеры по типу задания
        if task_type == "рефлексивное":
            examples = [ex for ex in examples if any(word in ex.lower() for word in ["подумай", "проанализируй", "размысли", "исследуй"])]
        elif task_type == "творческое":
            examples = [ex for ex in examples if any(word in ex.lower() for word in ["создай", "нарисуй", "сочини", "придумай"])]
        
        return "\n".join(f"- {example}" for example in examples[:3])

def check_task_uniqueness(new_task_text, history_manager, similarity_threshold=0.6):
    """Проверка уникальности нового задания"""
    
    new_keywords = history_manager.extract_keywords(new_task_text)
    recent_keywords = history_manager.get_recent_keywords(days=14)
    
    # Подсчет пересечения ключевых слов
    intersection = set(new_keywords) & set(recent_keywords)
    if len(new_keywords) > 0:
        similarity_score = len(intersection) / len(new_keywords)
    else:
        similarity_score = 0
    
    # Проверка на повторяющиеся структуры
    structure_patterns = [
        r'выбери.*один.*предмет',
        r'выберите.*один.*предмет', 
        r'найди.*вещь',
        r'избавься.*от.*предмет'
    ]
    
    has_repetitive_structure = any(
        re.search(pattern, new_task_text.lower()) 
        for pattern in structure_patterns
    )
    
    is_unique = (similarity_score < similarity_threshold and 
                not has_repetitive_structure)
    
    return is_unique, similarity_score, intersection

def generate_enhanced_daily_task(client, chat_id, bot):
    """Основная функция генерации улучшенного задания дня"""
    
    print("🚀 Запуск улучшенной системы генерации заданий...")
    
    # Инициализация компонентов
    history_manager = TaskHistoryManager()
    task_selector = IntelligentTaskSelector(history_manager)
    prompt_generator = EnhancedPromptGenerator(history_manager)
    
    # Выбор параметров задания
    category, subcategory, task_type = task_selector.select_task_parameters()
    
    print(f"📋 Выбранные параметры:")
    print(f"   Категория: {category}")
    print(f"   Подкатегория: {subcategory}")
    print(f"   Тип задания: {task_type}")
    
    # Генерация промпта
    prompt = prompt_generator.create_prompt(category, subcategory, task_type)
    
    # Генерация задания с проверкой уникальности
    max_attempts = 5
    for attempt in range(max_attempts):
        print(f"🎯 Попытка генерации {attempt + 1}/{max_attempts}")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8  # Повышаем креативность
            )
            
            task_text = response.choices[0].message.content.strip()
            
            # Проверка уникальности
            is_unique, similarity_score, common_keywords = check_task_uniqueness(
                task_text, history_manager
            )
            
            if is_unique:
                print(f"✅ Уникальное задание сгенерировано!")
                
                # Сохранение в историю
                history_manager.add_task(category, subcategory, task_type, task_text)
                
                # Отправка пользователю
                try:
                    bot.send_message(chat_id=chat_id, text=task_text, parse_mode="Markdown")
                    print(f"📤 Задание отправлено в чат {chat_id}")
                    return True
                except Exception as e:
                    print(f"❌ Ошибка отправки: {e}")
                    # Попробуем без форматирования
                    bot.send_message(chat_id=chat_id, text=task_text)
                    return True
            
            else:
                print(f"⚠️ Задание слишком похоже на недавние (сходство: {similarity_score:.2f})")
                print(f"   Общие ключевые слова: {common_keywords}")
                
                # Обновляем промпт для следующей попытки
                prompt += f"\n\nВНИМАНИЕ: Предыдущая попытка была слишком похожа на недавние задания. Избегай слов: {', '.join(common_keywords)}. Будь более креативным и оригинальным!"
        
        except Exception as e:
            print(f"❌ Ошибка генерации: {e}")
    
    print(f"❌ Не удалось сгенерировать уникальное задание за {max_attempts} попыток")
    return False

# Пример интеграции в основной код
if __name__ == "__main__":
    # Тестирование системы
    from openai import OpenAI
    
    # Инициализация (в реальном коде используйте ваши токены)
    client = OpenAI(api_key="your-openai-key")
    
    # Тест генерации
    print("🧪 Тестирование новой системы генерации заданий...")
    
    history_manager = TaskHistoryManager()
    task_selector = IntelligentTaskSelector(history_manager)
    
    # Генерируем несколько заданий для демонстрации
    for i in range(3):
        print(f"\n--- Тест {i+1} ---")
        category, subcategory, task_type = task_selector.select_task_parameters()
        print(f"Категория: {category}")
        print(f"Подкатегория: {subcategory}")
        print(f"Тип: {task_type}")

