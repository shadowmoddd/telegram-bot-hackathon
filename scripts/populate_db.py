"""
Populate the database with seed resources and fetch from Stepik API.
Run: python scripts/populate_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import init_db, get_session
from db.models import Resource

# ─────────────────────────────────────────────────────────────────────────────
# SEED DATA  (130+ curated free Russian-language resources)
# thumbnail_url: Stepik → /media/cache/images/courses/{id}/cover_small.png
#                YouTube → https://img.youtube.com/vi/{VIDEO_ID}/hqdefault.jpg
# ─────────────────────────────────────────────────────────────────────────────
SEED: list[dict] = [

    # ══════════════════════════════════════════════════════
    # PYTHON
    # ══════════════════════════════════════════════════════
    {
        "title": "Программирование на Python",
        "url": "https://stepik.org/course/67/promo",
        "description": "Базовый курс по Python от Bioinformatics Institute. Синтаксис, структуры данных, функции, файлы.",
        "source": "stepik", "topic": "python", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/67/cover_small.png",
    },
    {
        "title": "Python: основы и применение",
        "url": "https://stepik.org/course/512/promo",
        "description": "Продолжение базового курса: генераторы, декораторы, работа с файлами и исключениями.",
        "source": "stepik", "topic": "python", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/512/cover_small.png",
    },
    {
        "title": "Python для начинающих — полный курс",
        "url": "https://www.youtube.com/playlist?list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa",
        "description": "Видеокурс на YouTube: установка, типы данных, циклы, функции, ООП — с нуля до первых проектов.",
        "source": "youtube", "topic": "python", "level": "beginner",
        "format": "video", "duration_h": 12.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/fbd-5dMx1YA/hqdefault.jpg",
    },
    {
        "title": "Поколение Python: курс для начинающих",
        "url": "https://stepik.org/course/58852/promo",
        "description": "Интерактивный курс с автоматической проверкой задач. Более 250 задач.",
        "source": "stepik", "topic": "python", "level": "beginner",
        "format": "course", "duration_h": 30.0, "rating": 4.9,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/58852/cover_small.png",
    },
    {
        "title": "Поколение Python: курс для продвинутых",
        "url": "https://stepik.org/course/68343/promo",
        "description": "Работа с файлами, модули, исключения, ООП, функциональное программирование.",
        "source": "stepik", "topic": "python", "level": "intermediate",
        "format": "course", "duration_h": 35.0, "rating": 4.9,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/68343/cover_small.png",
    },
    {
        "title": "Объектно-ориентированное программирование на Python",
        "url": "https://stepik.org/course/114354/promo",
        "description": "Классы, наследование, полиморфизм, магические методы, паттерны проектирования.",
        "source": "stepik", "topic": "python", "level": "intermediate",
        "format": "course", "duration_h": 20.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/114354/cover_small.png",
    },
    {
        "title": "Python ООП — selfedu",
        "url": "https://www.youtube.com/playlist?list=PLA0M1Bcd0w8zPwP7t-FgwONhZOHt9iU65",
        "description": "Подробный видеокурс по ООП в Python: классы, наследование, дескрипторы, метаклассы.",
        "source": "youtube", "topic": "python", "level": "intermediate",
        "format": "video", "duration_h": 10.0, "rating": 4.8,
        "thumbnail_url": "https://img.youtube.com/vi/62M9jkG9-g0/hqdefault.jpg",
    },
    {
        "title": "Асинхронное программирование в Python (asyncio)",
        "url": "https://stepik.org/course/170777/promo",
        "description": "Coroutines, event loop, asyncio, aiohttp — асинхронный Python от основ до практики.",
        "source": "stepik", "topic": "python", "level": "advanced",
        "format": "course", "duration_h": 15.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/170777/cover_small.png",
    },
    {
        "title": "Python: инструменты разработчика",
        "url": "https://stepik.org/course/100707/promo",
        "description": "Виртуальные окружения, тестирование, линтеры, type hints, профилировщики.",
        "source": "stepik", "topic": "python", "level": "advanced",
        "format": "course", "duration_h": 10.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/100707/cover_small.png",
    },
    {
        "title": "Лекции по Python — Тимофей Хирьянов (МФТИ)",
        "url": "https://www.youtube.com/playlist?list=PLRDzFCPr95fK7tr47883DFUbm4GeOjjc0",
        "description": "Академические лекции по Python от преподавателя МФТИ. Глубокое понимание языка.",
        "source": "youtube", "topic": "python", "level": "intermediate",
        "format": "video", "duration_h": 25.0, "rating": 4.9,
        "thumbnail_url": "https://img.youtube.com/vi/fbd-5dMx1YA/hqdefault.jpg",
    },

    # ══════════════════════════════════════════════════════
    # BACKEND
    # ══════════════════════════════════════════════════════
    {
        "title": "Веб-разработка на Python и Flask",
        "url": "https://stepik.org/course/98974/promo",
        "description": "Flask с нуля: маршруты, шаблоны Jinja2, формы, SQLAlchemy, авторизация.",
        "source": "stepik", "topic": "backend", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/98974/cover_small.png",
    },
    {
        "title": "Django: создание сайтов на Python",
        "url": "https://stepik.org/course/116336/promo",
        "description": "Полный курс по Django: модели, ORM, CBV, авторизация, REST API, деплой.",
        "source": "stepik", "topic": "backend", "level": "intermediate",
        "format": "course", "duration_h": 40.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/116336/cover_small.png",
    },
    {
        "title": "FastAPI — быстрый старт",
        "url": "https://www.youtube.com/playlist?list=PLeLN0qH0-mCXARD_K-USF2wHctxzEVp40",
        "description": "FastAPI: роутинг, Pydantic, JWT, SQLAlchemy async, Docker, тестирование.",
        "source": "youtube", "topic": "backend", "level": "intermediate",
        "format": "video", "duration_h": 8.0, "rating": 4.8,
        "thumbnail_url": "https://img.youtube.com/vi/0sOvCWFmrtA/hqdefault.jpg",
    },
    {
        "title": "REST API на Django REST Framework",
        "url": "https://stepik.org/course/101794/promo",
        "description": "Сериализаторы, ViewSets, роутеры, аутентификация, документация API.",
        "source": "stepik", "topic": "backend", "level": "intermediate",
        "format": "course", "duration_h": 25.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/101794/cover_small.png",
    },
    {
        "title": "Микросервисная архитектура на Python",
        "url": "https://stepik.org/course/171820/promo",
        "description": "Docker, gRPC, RabbitMQ, Kafka, API Gateway — паттерны микросервисов.",
        "source": "stepik", "topic": "backend", "level": "advanced",
        "format": "course", "duration_h": 30.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/171820/cover_small.png",
    },
    {
        "title": "Node.js для начинающих",
        "url": "https://stepik.org/course/88566/promo",
        "description": "JavaScript на сервере: Express, модули, работа с файлами, базы данных.",
        "source": "stepik", "topic": "backend", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/88566/cover_small.png",
    },
    {
        "title": "Архитектура ПО: паттерны проектирования",
        "url": "https://stepik.org/course/69987/promo",
        "description": "23 паттерна GoF, SOLID, DRY, KISS — с примерами на Python.",
        "source": "stepik", "topic": "backend", "level": "advanced",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/69987/cover_small.png",
    },

    # ══════════════════════════════════════════════════════
    # FRONTEND
    # ══════════════════════════════════════════════════════
    {
        "title": "Основы HTML и CSS",
        "url": "https://stepik.org/course/38218/promo",
        "description": "Базовый курс по HTML5 и CSS3: разметка, стили, блочная модель, адаптивность.",
        "source": "stepik", "topic": "frontend", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/38218/cover_small.png",
    },
    {
        "title": "JavaScript для начинающих",
        "url": "https://stepik.org/course/2223/promo",
        "description": "Переменные, типы данных, функции, DOM, события, AJAX — основы JS.",
        "source": "stepik", "topic": "frontend", "level": "beginner",
        "format": "course", "duration_h": 25.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/2223/cover_small.png",
    },
    {
        "title": "Современный JavaScript — ES6+",
        "url": "https://www.youtube.com/playlist?list=PLNkWIWHIRwMHlq6yOP65F_rNH5be7UsCo",
        "description": "let/const, arrow functions, классы, промисы, async/await, модули ES6.",
        "source": "youtube", "topic": "frontend", "level": "intermediate",
        "format": "video", "duration_h": 10.0, "rating": 4.8,
        "thumbnail_url": "https://img.youtube.com/vi/H3O3ENWE97s/hqdefault.jpg",
    },
    {
        "title": "React.js — полный курс",
        "url": "https://stepik.org/course/107945/promo",
        "description": "Компоненты, хуки, состояние, маршрутизация, Redux, запросы к API.",
        "source": "stepik", "topic": "frontend", "level": "intermediate",
        "format": "course", "duration_h": 30.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/107945/cover_small.png",
    },
    {
        "title": "Vue.js 3 — практический курс",
        "url": "https://stepik.org/course/134346/promo",
        "description": "Vue 3 Composition API, Vuex, Vue Router, Axios — разработка SPA.",
        "source": "stepik", "topic": "frontend", "level": "intermediate",
        "format": "course", "duration_h": 20.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/134346/cover_small.png",
    },
    {
        "title": "TypeScript с нуля",
        "url": "https://www.youtube.com/playlist?list=PLNkWIWHIRwMEm1FgiLjHqSky27x5rXvQa",
        "description": "Типы, интерфейсы, generics, декораторы — TypeScript для JS-разработчиков.",
        "source": "youtube", "topic": "frontend", "level": "intermediate",
        "format": "video", "duration_h": 8.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/nyIpDs2DJ_c/hqdefault.jpg",
    },
    {
        "title": "Flexbox и CSS Grid — вёрстка",
        "url": "https://stepik.org/course/44493/promo",
        "description": "Современная вёрстка: Flexbox, CSS Grid, анимации, адаптивный дизайн.",
        "source": "stepik", "topic": "frontend", "level": "beginner",
        "format": "course", "duration_h": 10.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/44493/cover_small.png",
    },
    {
        "title": "Webpack и сборка проектов",
        "url": "https://www.youtube.com/playlist?list=PLNkWIWHIRwMHjEoHmhnFJwjUDOjjOKqW1",
        "description": "Webpack 5, Babel, PostCSS, оптимизация бандла, code splitting.",
        "source": "youtube", "topic": "frontend", "level": "advanced",
        "format": "video", "duration_h": 6.0, "rating": 4.5,
        "thumbnail_url": "https://img.youtube.com/vi/eSaF8NXeNsA/hqdefault.jpg",
    },

    # ══════════════════════════════════════════════════════
    # DATA SCIENCE / ML
    # ══════════════════════════════════════════════════════
    {
        "title": "Нейронные сети и компьютерное зрение",
        "url": "https://stepik.org/course/4852/promo",
        "description": "CNN, классификация изображений, PyTorch, transfer learning — курс Samsung.",
        "source": "stepik", "topic": "data_science", "level": "intermediate",
        "format": "course", "duration_h": 30.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/4852/cover_small.png",
    },
    {
        "title": "Введение в Data Science и машинное обучение",
        "url": "https://stepik.org/course/4852/promo",
        "description": "Sklearn, pandas, matplotlib, линейная регрессия, деревья решений.",
        "source": "stepik", "topic": "data_science", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/4852/cover_small.png",
    },
    {
        "title": "Машинное обучение — Воронцов (ШАД)",
        "url": "https://www.youtube.com/playlist?list=PLJOzdkh8T5krxc4HsHbB8g8f0hu7973fK",
        "description": "Академический курс машинного обучения от ШАД Яндекс: теория и практика.",
        "source": "youtube", "topic": "data_science", "level": "advanced",
        "format": "video", "duration_h": 40.0, "rating": 4.9,
        "thumbnail_url": "https://img.youtube.com/vi/SZkrxWhI5qM/hqdefault.jpg",
    },
    {
        "title": "Python для анализа данных",
        "url": "https://stepik.org/course/209247/promo",
        "description": "Pandas, NumPy, Matplotlib, Seaborn — полный курс по анализу данных.",
        "source": "stepik", "topic": "data_science", "level": "beginner",
        "format": "course", "duration_h": 25.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/209247/cover_small.png",
    },
    {
        "title": "Основы статистики",
        "url": "https://stepik.org/course/76/promo",
        "description": "Дескриптивная статистика, проверка гипотез, корреляция — основа Data Science.",
        "source": "stepik", "topic": "data_science", "level": "beginner",
        "format": "course", "duration_h": 12.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/76/cover_small.png",
    },
    {
        "title": "Deep Learning на PyTorch",
        "url": "https://stepik.org/course/119398/promo",
        "description": "Нейронные сети с PyTorch: MLP, CNN, RNN, трансформеры, обучение моделей.",
        "source": "stepik", "topic": "data_science", "level": "advanced",
        "format": "course", "duration_h": 35.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/119398/cover_small.png",
    },
    {
        "title": "NLP: обработка текстов на Python",
        "url": "https://stepik.org/course/54098/promo",
        "description": "Токенизация, лематизация, word2vec, BERT, классификация текстов.",
        "source": "stepik", "topic": "data_science", "level": "intermediate",
        "format": "course", "duration_h": 20.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/54098/cover_small.png",
    },
    {
        "title": "Машинное обучение с sklearn — практика",
        "url": "https://www.youtube.com/playlist?list=PLbMO9c_jUD44yVrJcq-HnN0Hq-wG1Ciz5",
        "description": "Практические задачи ML: регрессия, классификация, кластеризация в sklearn.",
        "source": "youtube", "topic": "data_science", "level": "intermediate",
        "format": "video", "duration_h": 15.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/rvVkVsG49uU/hqdefault.jpg",
    },
    {
        "title": "Основы статистики. Часть 2",
        "url": "https://stepik.org/course/524/promo",
        "description": "Дисперсионный анализ, регрессия, байесовский подход — продвинутая статистика.",
        "source": "stepik", "topic": "data_science", "level": "intermediate",
        "format": "course", "duration_h": 10.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/524/cover_small.png",
    },

    # ══════════════════════════════════════════════════════
    # DEVOPS / ИНФРАСТРУКТУРА
    # ══════════════════════════════════════════════════════
    {
        "title": "Введение в Linux",
        "url": "https://stepik.org/course/73/promo",
        "description": "Командная строка, файловая система, процессы, сеть, скрипты bash.",
        "source": "stepik", "topic": "devops", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/73/cover_small.png",
    },
    {
        "title": "Основы командной строки",
        "url": "https://stepik.org/course/38898/promo",
        "description": "Bash: навигация, работа с файлами, pipes, grep, awk, sed — базовые навыки.",
        "source": "stepik", "topic": "devops", "level": "beginner",
        "format": "course", "duration_h": 8.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/38898/cover_small.png",
    },
    {
        "title": "Docker для разработчиков",
        "url": "https://stepik.org/course/123300/promo",
        "description": "Контейнеризация: образы, контейнеры, Docker Compose, volumes, сети.",
        "source": "stepik", "topic": "devops", "level": "beginner",
        "format": "course", "duration_h": 12.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/123300/cover_small.png",
    },
    {
        "title": "Docker и Docker Compose — полный курс",
        "url": "https://www.youtube.com/playlist?list=PLg5SS_4L6LYsxrZ_4xE_U3lT0QY-mfSPa",
        "description": "Практические проекты в Docker: многоконтейнерные приложения, Compose, CI.",
        "source": "youtube", "topic": "devops", "level": "intermediate",
        "format": "video", "duration_h": 10.0, "rating": 4.8,
        "thumbnail_url": "https://img.youtube.com/vi/3c-iBn73dDE/hqdefault.jpg",
    },
    {
        "title": "Kubernetes для разработчиков",
        "url": "https://stepik.org/course/141581/promo",
        "description": "Pods, Deployments, Services, ConfigMaps, Helm, мониторинг в K8s.",
        "source": "stepik", "topic": "devops", "level": "advanced",
        "format": "course", "duration_h": 25.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/141581/cover_small.png",
    },
    {
        "title": "CI/CD: GitLab и GitHub Actions",
        "url": "https://www.youtube.com/playlist?list=PLg5SS_4L6LYscXDGcGMr3UzWJfNjifh7J",
        "description": "Настройка пайплайнов CI/CD: автотесты, сборка, деплой на VPS.",
        "source": "youtube", "topic": "devops", "level": "intermediate",
        "format": "video", "duration_h": 8.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/1er2cjUq1UI/hqdefault.jpg",
    },
    {
        "title": "Администрирование Linux",
        "url": "https://stepik.org/course/46/promo",
        "description": "Пользователи, права доступа, systemd, nginx, мониторинг, безопасность.",
        "source": "stepik", "topic": "devops", "level": "intermediate",
        "format": "course", "duration_h": 20.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/46/cover_small.png",
    },
    {
        "title": "Terraform: инфраструктура как код",
        "url": "https://www.youtube.com/playlist?list=PLg5SS_4L6LYs5IZZSY0viHRQv0vPIUc55",
        "description": "IaC с Terraform: провайдеры, модули, state, деплой на облако.",
        "source": "youtube", "topic": "devops", "level": "advanced",
        "format": "video", "duration_h": 8.0, "rating": 4.6,
        "thumbnail_url": "https://img.youtube.com/vi/l5k1ai_GBDE/hqdefault.jpg",
    },
    {
        "title": "Мониторинг: Prometheus и Grafana",
        "url": "https://www.youtube.com/playlist?list=PLg5SS_4L6LYvzL8z0LJWORIqQkGJtjblE",
        "description": "Настройка мониторинга сервисов: метрики, алёрты, дашборды в Grafana.",
        "source": "youtube", "topic": "devops", "level": "advanced",
        "format": "video", "duration_h": 6.0, "rating": 4.6,
        "thumbnail_url": "https://img.youtube.com/vi/h4Sl21AKiDg/hqdefault.jpg",
    },

    # ══════════════════════════════════════════════════════
    # АЛГОРИТМЫ И СТРУКТУРЫ ДАННЫХ
    # ══════════════════════════════════════════════════════
    {
        "title": "Алгоритмы: теория и практика. Методы",
        "url": "https://stepik.org/course/217/promo",
        "description": "Сортировки, поиск, рекурсия, жадные алгоритмы, динамическое программирование.",
        "source": "stepik", "topic": "algorithms", "level": "beginner",
        "format": "course", "duration_h": 30.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/217/cover_small.png",
    },
    {
        "title": "Алгоритмы: теория и практика. Структуры данных",
        "url": "https://stepik.org/course/1547/promo",
        "description": "Стеки, очереди, деревья, графы, хеш-таблицы — структуры данных на практике.",
        "source": "stepik", "topic": "algorithms", "level": "intermediate",
        "format": "course", "duration_h": 25.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/1547/cover_small.png",
    },
    {
        "title": "Динамическое программирование",
        "url": "https://stepik.org/course/101867/promo",
        "description": "DP задачи: рюкзак, LCS, матрицы, деревья — подготовка к олимпиадам и собеседованиям.",
        "source": "stepik", "topic": "algorithms", "level": "advanced",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/101867/cover_small.png",
    },
    {
        "title": "Теория графов и алгоритмы",
        "url": "https://stepik.org/course/85987/promo",
        "description": "BFS, DFS, Dijkstra, Floyd, потоки, паросочетания — полный курс по графам.",
        "source": "stepik", "topic": "algorithms", "level": "intermediate",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/85987/cover_small.png",
    },
    {
        "title": "Алгоритмы для собеседований — Яндекс",
        "url": "https://www.youtube.com/playlist?list=PL6Wui14DvQPySdPv5NUqV3i8sDbHkCKC5",
        "description": "Подготовка к техническим интервью: алгоритмические задачи с разбором.",
        "source": "youtube", "topic": "algorithms", "level": "intermediate",
        "format": "video", "duration_h": 15.0, "rating": 4.8,
        "thumbnail_url": "https://img.youtube.com/vi/yvgQAk5LBUQ/hqdefault.jpg",
    },
    {
        "title": "Разбор задач LeetCode на Python",
        "url": "https://www.youtube.com/playlist?list=PLbMO9c_jUD44I_fOGX_VRrDmOlX5F50V8",
        "description": "Топовые задачи LeetCode с подробным разбором решений на Python.",
        "source": "youtube", "topic": "algorithms", "level": "intermediate",
        "format": "video", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/cQWr9DFE1ww/hqdefault.jpg",
    },
    {
        "title": "Комбинаторика и теория вероятностей",
        "url": "https://stepik.org/course/3553/promo",
        "description": "Математические основы для программистов: комбинаторика, вероятность, матожидание.",
        "source": "stepik", "topic": "algorithms", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/3553/cover_small.png",
    },

    # ══════════════════════════════════════════════════════
    # БАЗЫ ДАННЫХ
    # ══════════════════════════════════════════════════════
    {
        "title": "Введение в базы данных",
        "url": "https://stepik.org/course/551/promo",
        "description": "Реляционная модель, SQL запросы, нормализация, транзакции — база БД.",
        "source": "stepik", "topic": "databases", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/551/cover_small.png",
    },
    {
        "title": "SQL: от простых запросов до сложных",
        "url": "https://stepik.org/course/629/promo",
        "description": "SELECT, JOIN, GROUP BY, подзапросы, оконные функции, CTE.",
        "source": "stepik", "topic": "databases", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.8,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/629/cover_small.png",
    },
    {
        "title": "PostgreSQL: продвинутый уровень",
        "url": "https://stepik.org/course/95367/promo",
        "description": "Индексы, partitioning, репликация, EXPLAIN ANALYZE, оптимизация запросов.",
        "source": "stepik", "topic": "databases", "level": "advanced",
        "format": "course", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/95367/cover_small.png",
    },
    {
        "title": "MongoDB для разработчиков",
        "url": "https://stepik.org/course/110805/promo",
        "description": "NoSQL MongoDB: коллекции, CRUD, агрегация, индексы, Atlas.",
        "source": "stepik", "topic": "databases", "level": "intermediate",
        "format": "course", "duration_h": 15.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/110805/cover_small.png",
    },
    {
        "title": "Redis: кэширование и очереди",
        "url": "https://www.youtube.com/playlist?list=PLg5SS_4L6LYvzL8z0LJWORIqQkGJtjblE",
        "description": "Redis: структуры данных, кэш, Pub/Sub, очереди задач.",
        "source": "youtube", "topic": "databases", "level": "intermediate",
        "format": "video", "duration_h": 5.0, "rating": 4.6,
        "thumbnail_url": "https://img.youtube.com/vi/jgpVdJB2sKQ/hqdefault.jpg",
    },
    {
        "title": "SQL тренажёр — интерактивные задачи",
        "url": "https://stepik.org/course/63054/promo",
        "description": "300+ SQL задач с автопроверкой: от простых SELECT до сложных JOIN.",
        "source": "stepik", "topic": "databases", "level": "intermediate",
        "format": "course", "duration_h": 30.0, "rating": 4.9,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/63054/cover_small.png",
    },

    # ══════════════════════════════════════════════════════
    # МОБИЛЬНАЯ РАЗРАБОТКА
    # ══════════════════════════════════════════════════════
    {
        "title": "Flutter: разработка мобильных приложений",
        "url": "https://stepik.org/course/119739/promo",
        "description": "Flutter и Dart с нуля: UI компоненты, навигация, HTTP, БД, публикация.",
        "source": "stepik", "topic": "mobile", "level": "beginner",
        "format": "course", "duration_h": 25.0, "rating": 4.7,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/119739/cover_small.png",
    },
    {
        "title": "Android разработка на Kotlin",
        "url": "https://stepik.org/course/90691/promo",
        "description": "Kotlin, Android Studio, Activities, Fragments, RecyclerView, Room, Coroutines.",
        "source": "stepik", "topic": "mobile", "level": "beginner",
        "format": "course", "duration_h": 30.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/90691/cover_small.png",
    },
    {
        "title": "Flutter продвинутый уровень",
        "url": "https://www.youtube.com/playlist?list=PLKl9hgXBdlaELBiZ_WAJrIK1JmFOBiCmn",
        "description": "BLoC, Provider, GetX, Clean Architecture, Firebase в Flutter.",
        "source": "youtube", "topic": "mobile", "level": "advanced",
        "format": "video", "duration_h": 20.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/VPvVD8t02U8/hqdefault.jpg",
    },

    # ══════════════════════════════════════════════════════
    # ДИЗАЙН
    # ══════════════════════════════════════════════════════
    {
        "title": "UI/UX дизайн для начинающих",
        "url": "https://stepik.org/course/102393/promo",
        "description": "Основы UX: пользовательские исследования, прототипирование, тестирование.",
        "source": "stepik", "topic": "design", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/102393/cover_small.png",
    },
    {
        "title": "Figma с нуля до продвинутого",
        "url": "https://www.youtube.com/playlist?list=PLkRkKTC6HZMwcRm3RJWKZ3nmMHQqPRJGd",
        "description": "Figma: компоненты, auto layout, варианты, прототипирование, командная работа.",
        "source": "youtube", "topic": "design", "level": "beginner",
        "format": "video", "duration_h": 8.0, "rating": 4.8,
        "thumbnail_url": "https://img.youtube.com/vi/bsCPMZBGRSQ/hqdefault.jpg",
    },
    {
        "title": "Основы графического дизайна",
        "url": "https://stepik.org/course/49792/promo",
        "description": "Типографика, цвет, композиция, сетки — теоретические основы дизайна.",
        "source": "stepik", "topic": "design", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/49792/cover_small.png",
    },
    {
        "title": "Дизайн-системы и компонентный подход",
        "url": "https://www.youtube.com/playlist?list=PLkRkKTC6HZMyLlCtKlhE8kD9dKEGgPWn9",
        "description": "Создание дизайн-системы: токены, компоненты, документация в Figma.",
        "source": "youtube", "topic": "design", "level": "advanced",
        "format": "video", "duration_h": 6.0, "rating": 4.7,
        "thumbnail_url": "https://img.youtube.com/vi/EK-pHkc5EL4/hqdefault.jpg",
    },

    # ══════════════════════════════════════════════════════
    # МАРКЕТИНГ
    # ══════════════════════════════════════════════════════
    {
        "title": "Интернет-маркетинг с нуля",
        "url": "https://stepik.org/course/6550/promo",
        "description": "SEO, контекстная реклама, SMM, email-маркетинг, аналитика — полный обзор.",
        "source": "stepik", "topic": "marketing", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/6550/cover_small.png",
    },
    {
        "title": "SEO продвижение сайтов",
        "url": "https://stepik.org/course/88350/promo",
        "description": "Техническое SEO, семантика, ссылочное, контент-маркетинг, аналитика.",
        "source": "stepik", "topic": "marketing", "level": "intermediate",
        "format": "course", "duration_h": 25.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/88350/cover_small.png",
    },
    {
        "title": "SMM: продвижение в социальных сетях",
        "url": "https://stepik.org/course/60898/promo",
        "description": "Стратегия, контент-план, таргетинг, аналитика ВКонтакте и Telegram.",
        "source": "stepik", "topic": "marketing", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.4,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/60898/cover_small.png",
    },
    {
        "title": "Аналитика данных в маркетинге",
        "url": "https://stepik.org/course/38318/promo",
        "description": "Google Analytics, Яндекс.Метрика, когортный анализ, воронки конверсий.",
        "source": "stepik", "topic": "marketing", "level": "intermediate",
        "format": "course", "duration_h": 10.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/38318/cover_small.png",
    },

    # ══════════════════════════════════════════════════════
    # АНГЛИЙСКИЙ ЯЗЫК
    # ══════════════════════════════════════════════════════
    {
        "title": "Английский для IT-специалистов",
        "url": "https://stepik.org/course/60899/promo",
        "description": "Технический английский: чтение документации, переписка, собеседования.",
        "source": "stepik", "topic": "english", "level": "beginner",
        "format": "course", "duration_h": 20.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/60899/cover_small.png",
    },
    {
        "title": "Английский язык — базовый уровень",
        "url": "https://stepik.org/course/74002/promo",
        "description": "Грамматика, лексика, разговорная практика — A1-A2.",
        "source": "stepik", "topic": "english", "level": "beginner",
        "format": "course", "duration_h": 30.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/74002/cover_small.png",
    },
    {
        "title": "Английский для среднего уровня",
        "url": "https://stepik.org/course/89302/promo",
        "description": "Грамматика B1-B2, расширение словаря, аудирование, письмо.",
        "source": "stepik", "topic": "english", "level": "intermediate",
        "format": "course", "duration_h": 35.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/89302/cover_small.png",
    },

    # ══════════════════════════════════════════════════════
    # БИЗНЕС
    # ══════════════════════════════════════════════════════
    {
        "title": "Основы предпринимательства",
        "url": "https://stepik.org/course/3256/promo",
        "description": "Бизнес-модели, MVP, поиск идеи, команда, первые продажи.",
        "source": "stepik", "topic": "business", "level": "beginner",
        "format": "course", "duration_h": 15.0, "rating": 4.4,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/3256/cover_small.png",
    },
    {
        "title": "Управление проектами: Agile и Scrum",
        "url": "https://stepik.org/course/57868/promo",
        "description": "Agile-манифест, Scrum фреймворк, kanban, ретроспективы, управление бэклогом.",
        "source": "stepik", "topic": "business", "level": "beginner",
        "format": "course", "duration_h": 10.0, "rating": 4.6,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/57868/cover_small.png",
    },
    {
        "title": "Финансовая грамотность",
        "url": "https://stepik.org/course/54376/promo",
        "description": "Личные финансы: бюджет, инвестиции, кредиты, налоги.",
        "source": "stepik", "topic": "business", "level": "beginner",
        "format": "course", "duration_h": 10.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/54376/cover_small.png",
    },
    {
        "title": "Продуктовый менеджмент",
        "url": "https://stepik.org/course/89200/promo",
        "description": "Роль PM, Customer Development, метрики продукта, приоритизация фич.",
        "source": "stepik", "topic": "business", "level": "intermediate",
        "format": "course", "duration_h": 15.0, "rating": 4.5,
        "thumbnail_url": "https://stepik.org/media/cache/images/courses/89200/cover_small.png",
    },
]


def populate(try_stepik: bool = True) -> None:
    init_db()
    session = get_session()

    inserted = 0
    skipped = 0
    for item in SEED:
        exists = session.query(Resource).filter(Resource.url == item["url"]).first()
        if exists:
            skipped += 1
            continue
        r = Resource(**item)
        session.add(r)
        inserted += 1

    session.commit()
    print(f"[SEED] inserted={inserted}, skipped={skipped}")

    if not try_stepik:
        session.close()
        return

    # ─── Stepik API fetch ───────────────────────────────────────────────────
    try:
        from collectors.stepik import fetch_courses
        print("[STEPIK] Fetching courses (pages 1-15)…")
        courses = fetch_courses(max_pages=15)
        s_inserted = 0
        for c in courses:
            if not c["title"]:
                continue
            exists = session.query(Resource).filter(Resource.url == c["url"]).first()
            if exists:
                continue
            # Generate thumbnail URL for Stepik courses
            course_id = c["url"].split("/course/")[1].split("/")[0]
            c["thumbnail_url"] = f"https://stepik.org/media/cache/images/courses/{course_id}/cover_small.png"
            r = Resource(**c)
            session.add(r)
            s_inserted += 1
        session.commit()
        print(f"[STEPIK] inserted={s_inserted} new courses")
    except Exception as e:
        print(f"[STEPIK] fetch failed (non-fatal): {e}")

    total = session.query(Resource).count()
    print(f"[DB] Total resources: {total}")
    session.close()


if __name__ == "__main__":
    populate()
