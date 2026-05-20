# ПутеводительЗнаний — Telegram-бот учебных маршрутов

Бот подбирает **персональный учебный маршрут** из бесплатных русскоязычных курсов, видео и статей.  
Источники: Stepik, YouTube, Habr.

## Быстрый старт (Docker)

```bash
# 1. Клонировать репозиторий
git clone <repo_url>
cd task-repo

# 2. Создать файл .env
cp .env.example .env
# Открыть .env и вставить BOT_TOKEN

# 3. Запустить
docker compose up --build -d
```

Бот сразу готов к работе. Ссылка: `https://t.me/<имя_бота>`

---

## Запуск без Docker

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Вставить BOT_TOKEN в .env

python scripts/populate_db.py   # Заполнить БД
python -m bot.main              # Запустить бота
```

---

## Переменные окружения

| Переменная       | Описание                         | Обязательна |
|------------------|----------------------------------|-------------|
| `BOT_TOKEN`      | Токен от @BotFather              | ✅ да       |
| `YOUTUBE_API_KEY`| YouTube Data API v3 ключ         | ❌ нет      |

---

## Команды бота

| Команда     | Действие                         |
|-------------|----------------------------------|
| `/start`    | Начало / возврат к профилю       |
| `/route`    | Текущий маршрут                  |
| `/profile`  | Просмотр профиля                 |
| `/restart`  | Начать заново                    |
| `/help`     | Справка                          |

---

## Пользовательский сценарий

1. `/start` → выбор темы (Python / Backend / Frontend / Data Science / DevOps / …)
2. Уровень (Начинающий / Средний / Продвинутый)
3. Формат (Курс / Видео / Статья / Любой)
4. Доступное время в неделю
5. Бот строит маршрут из 5–10 ресурсов
6. Пользователь листает ресурсы, отмечает изученные / пропускает
7. Можно запросить новый маршрут или изменить профиль

---

## Структура проекта

```
├── bot/
│   ├── main.py            # Точка входа
│   ├── config.py          # Настройки, константы
│   ├── states.py          # FSM-состояния
│   ├── handlers/          # Обработчики команд и колбэков
│   └── keyboards/         # Inline-клавиатуры
├── db/
│   ├── models.py          # SQLAlchemy модели
│   └── database.py        # Сессия БД
├── recommender/
│   └── engine.py          # Логика рекомендаций
├── collectors/
│   └── stepik.py          # Сбор данных из Stepik API
├── scripts/
│   └── populate_db.py     # Заполнение БД (130+ ресурсов)
├── data/
│   └── resources.db       # SQLite база данных
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Технологии

- **Python 3.11**
- **aiogram 3.x** — Telegram Bot Framework
- **SQLite + SQLAlchemy** — хранение ресурсов и профилей
- **Stepik Open API** — автоматический сбор курсов
- **Docker / docker-compose** — контейнеризация

---

## Источники данных

| Источник | Тип         | Статус |
|----------|-------------|--------|
| Stepik   | Курсы       | ✅ API |
| YouTube  | Видео       | ✅ кураторская БД |
| Habr     | Статьи      | ✅ кураторская БД |
