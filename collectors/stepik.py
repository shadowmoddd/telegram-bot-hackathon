"""Fetch free Russian courses from Stepik public API."""
import time
import requests

STEPIK_BASE = "https://stepik.org/api"

TOPIC_KEYWORDS: dict[str, list[str]] = {
    "python": ["python", "питон", "django", "flask"],
    "web": ["html", "css", "javascript", "веб", "frontend", "backend", "react", "vue"],
    "data_science": ["data science", "машинное обучение", "нейрон", "ml", "анализ данных", "pandas"],
    "design": ["дизайн", "figma", "ux", "ui", "графический"],
    "marketing": ["маркетинг", "smm", "реклама", "seo", "контент"],
    "english": ["английский", "english", "esl"],
    "business": ["бизнес", "менеджмент", "управление проектами", "предпринимательство"],
    "other": [],
}


def _classify_topic(title: str, summary: str) -> str:
    text = (title + " " + (summary or "")).lower()
    for topic, keywords in TOPIC_KEYWORDS.items():
        if topic == "other":
            continue
        if any(kw in text for kw in keywords):
            return topic
    return "other"


def _estimate_level(title: str, summary: str) -> str:
    text = (title + " " + (summary or "")).lower()
    if any(w in text for w in ["начинающ", "с нуля", "основы", "введение", "базов", "для новичков"]):
        return "beginner"
    if any(w in text for w in ["продвинут", "advanced", "глубок", "для опытных"]):
        return "advanced"
    return "intermediate"


def fetch_courses(max_pages: int = 10) -> list[dict]:
    results = []
    for page in range(1, max_pages + 1):
        resp = requests.get(
            f"{STEPIK_BASE}/courses",
            params={"is_paid": "false", "language": "ru", "page": page},
            timeout=15,
        )
        if resp.status_code != 200:
            break
        data = resp.json()
        courses = data.get("courses", [])
        if not courses:
            break

        for c in courses:
            title = c.get("title", "").strip()
            summary = (c.get("summary") or "").strip()
            url = f"https://stepik.org/course/{c['id']}/promo"
            rating = float(c.get("rating", 0) or 0)
            workload = c.get("workload") or ""

            duration_h = None
            if workload:
                try:
                    nums = [int(s) for s in workload.split() if s.isdigit()]
                    if nums:
                        duration_h = float(nums[0])
                except (ValueError, IndexError):
                    pass

            results.append({
                "title": title,
                "url": url,
                "description": summary[:500] if summary else None,
                "source": "stepik",
                "topic": _classify_topic(title, summary),
                "level": _estimate_level(title, summary),
                "format": "course",
                "duration_h": duration_h,
                "rating": min(rating, 5.0),
                "is_free": True,
                "language": "ru",
            })

        if not data.get("meta", {}).get("has_next"):
            break
        time.sleep(0.3)

    return results
