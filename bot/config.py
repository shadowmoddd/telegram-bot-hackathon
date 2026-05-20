import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

TOPICS: dict[str, str] = {
    "python": "🐍 Python",
    "backend": "⚙️ Бэкенд-разработка",
    "frontend": "🎨 Фронтенд-разработка",
    "data_science": "📊 Data Science / ML",
    "devops": "🐳 DevOps / Инфраструктура",
    "algorithms": "🧮 Алгоритмы и структуры данных",
    "databases": "🗄️ Базы данных",
    "mobile": "📱 Мобильная разработка",
    "design": "✏️ Дизайн",
    "marketing": "📢 Маркетинг",
    "english": "🇬🇧 Английский язык",
    "business": "💼 Бизнес",
    "other": "🔍 Другое",
}

LEVELS: dict[str, str] = {
    "beginner": "🌱 Начинающий",
    "intermediate": "🌿 Средний",
    "advanced": "🌳 Продвинутый",
}

FORMATS: dict[str, str] = {
    "any": "📚 Любой",
    "course": "🎓 Курс",
    "video": "🎬 Видео",
    "article": "📝 Статья",
}

TIME_OPTIONS: dict[str, str] = {
    "low": "⏱ 1–3 ч/нед",
    "medium": "⏱ 3–7 ч/нед",
    "high": "⏱ 7+ ч/нед",
}

ROUTE_SIZE: dict[str, int] = {
    "low": 5,
    "medium": 7,
    "high": 10,
}

FORMAT_ICONS: dict[str, str] = {
    "course": "🎓",
    "video": "🎬",
    "article": "📝",
}

SOURCE_ICONS: dict[str, str] = {
    "stepik": "📘 Stepik",
    "youtube": "▶️ YouTube",
    "habr": "📰 Habr",
    "manual": "🔗 Ресурс",
}
