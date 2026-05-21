# Progressors Learning Bot

Telegram-бот с Mini App для персональных образовательных маршрутов. True Tech Arena 2026.

**Бот:** https://t.me/progressors_learn_bot  
**Mini App:** https://naughty-profit.surge.sh

---

## Проверка без установки

Бот уже запущен, Mini App задеплоен. Для быстрой проверки:

1. Открыть https://t.me/progressors_learn_bot
2. Нажать `/start`
3. Нажать **🚀 Открыть приложение**

---

## Запуск из исходников (Docker)

### Требования

- **Docker Desktop** — [docker.com/get-started](https://www.docker.com/get-started/) (Windows / macOS / Linux)
- Аккаунт Telegram
- Аккаунт на [console.groq.com](https://console.groq.com) (бесплатно)

---

### Шаг 1 — Клонировать репозиторий

```bash
git clone <ссылка-на-репозиторий>
cd task-repo
```

---

### Шаг 2 — Получить BOT_TOKEN

1. Открыть Telegram, найти [@BotFather](https://t.me/BotFather)
2. Отправить команду `/newbot`
3. Ввести любое имя бота, например: `Progressors Test Bot`
4. Ввести username, например: `progressors_test_123_bot` (должен заканчиваться на `bot`)
5. BotFather пришлёт токен вида:
   ```
   123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
6. Скопировать этот токен

---

### Шаг 3 — Получить GROQ_API_KEY

1. Зайти на [console.groq.com](https://console.groq.com)
2. Зарегистрироваться (бесплатно, можно через Google)
3. Перейти в раздел **API Keys**
4. Нажать **Create API Key**
5. Скопировать ключ вида:
   ```
   gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

### Шаг 4 — Создать файл .env

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows (cmd):**
```cmd
copy .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

Открыть файл `.env` в любом текстовом редакторе и заполнить:

```
BOT_TOKEN=вставить_токен_из_шага_2
GROQ_API_KEY=вставить_ключ_из_шага_3
MINIAPP_URL=https://naughty-profit.surge.sh
```

> `MINIAPP_URL` менять не нужно — Mini App уже задеплоен.

---

### Шаг 5 — Запустить

```bash
docker-compose up --build
```

Первый запуск занимает ~2–3 минуты (скачивание образа Python).

Когда в консоли появится:
```
INFO  Bot started
```
— бот готов к работе.

---

### Шаг 6 — Проверить

1. Открыть Telegram
2. Найти своего бота по username из шага 2
3. Нажать `/start`
4. Нажать кнопку **🚀 Открыть приложение**
5. Приложение должно открыться внутри Telegram

---

### Остановить бота

```bash
docker-compose down
```

---

## Запуск локально (без Docker)

Если Docker недоступен:

**Требования:** Python 3.11+

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Собрать базу материалов
python scripts/convert_bd.py

# 3. Запустить бота
python -m bot.main
```

Файл `.env` должен быть заполнен так же, как в шаге 4.

---

## Переменные окружения

| Переменная | Описание | Где взять |
|---|---|---|
| `BOT_TOKEN` | Токен Telegram-бота | @BotFather → /newbot |
| `GROQ_API_KEY` | API-ключ Groq (бесплатно) | console.groq.com → API Keys |
| `MINIAPP_URL` | URL Mini App | Уже задан — менять не нужно |

---

## Стек

| Компонент | Технология |
|---|---|
| Telegram Bot | Python 3.11, aiogram 3.x |
| AI | Groq API (llama-3.3-70b-versatile) |
| База данных | SQLite + aiosqlite + SQLAlchemy 2 |
| Mini App | React 19 + TypeScript + Vite |
| База материалов | 273 проверенных ресурса |
| Хостинг Mini App | Surge.sh |

---

## Структура проекта

```
bot/          — Telegram-бот (Python)
miniapp/      — Mini App (React/TypeScript)
bd/           — курируемая база материалов (273 ресурса)
scripts/      — утилиты
prompts/      — промты для AI
data/         — генерируется автоматически при сборке
```

---

## Сценарий тестирования

1. `/start` → кнопка **Открыть приложение**
2. Выбрать сферу: IT → Backend (или Design, Видеомонтаж)
3. Пройти диагностический квиз (7 вопросов) — ИИ определяет уровень
4. Изучить персональный маршрут с материалами
5. Открыть шаг → видео запускается в плеере внутри приложения
6. Нажать **📖 Документация** — шпаргалки открываются в Telegram
7. Пройти квиз по шагу → **Откорректировать курс** — ИИ анализирует ошибки
8. **Хочу больше материалов** → AI подбирает из базы по выбранному формату
9. Завершить шаг → перейти к следующему (материалы другие, не повторяются)
10. Сменить сферу → вернуться назад → прогресс сохранён
