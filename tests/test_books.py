"""
Тесты функциональности книжных рекомендаций.
Запуск: pytest tests/test_books.py -v
"""
import pytest


class TestBooksInFormats:
    def test_book_format_in_formats_keyboard(self):
        from bot.keyboards.inline import formats_keyboard
        kb = formats_keyboard([])
        callbacks = {btn.callback_data for row in kb.inline_keyboard for btn in row}
        assert "toggle_fmt_book" in callbacks

    def test_book_format_selectable(self):
        from bot.keyboards.inline import formats_keyboard
        kb = formats_keyboard(["book"])
        texts = {btn.text for row in kb.inline_keyboard for btn in row}
        assert any("✅" in t and "Книг" in t for t in texts)

    def test_format_material_card_book_shows_google_link(self):
        from bot.services.roadmap_service import format_material_card
        material = {
            "title": "Чистый код",
            "type": "book",
            "platform": "Google",
            "url": "https://www.google.com/search?q=Clean+Code+Robert+Martin+pdf",
            "why_this": "Классика",
        }
        card = format_material_card(material, 1)
        assert "Google" in card
        assert "📚" in card

    def test_format_material_card_book_emoji(self):
        from bot.services.roadmap_service import format_material_card
        material = {
            "title": "Python Crash Course",
            "type": "book",
            "platform": "Google",
            "url": "https://www.google.com/search?q=Python+Crash+Course+pdf",
            "why_this": "Для начинающих",
        }
        card = format_material_card(material, 2)
        assert "2." in card
        assert "📚" in card

    def test_format_material_card_book_link_label(self):
        from bot.services.roadmap_service import format_material_card
        material = {
            "title": "Грокаем алгоритмы",
            "type": "book",
            "platform": "Google",
            "url": "https://www.google.com/search?q=Grokking+Algorithms+pdf",
            "why_this": "Алгоритмы для начинающих",
        }
        card = format_material_card(material, 1)
        assert "Найти книгу (Google)" in card

    def test_book_in_format_labels(self):
        from bot.services.profile_service import FORMAT_LABELS
        assert "book" in FORMAT_LABELS
        assert FORMAT_LABELS["book"] == "Книги"


class TestBookVerifier:
    def test_google_search_url_contains_query(self):
        from bot.services.book_verifier import _google_books_search_url
        url = _google_books_search_url("Clean Code Robert Martin")
        assert "google.com" in url
        assert "Clean" in url
        assert "pdf" in url

    def test_google_search_url_no_spaces(self):
        from bot.services.book_verifier import _google_books_search_url
        url = _google_books_search_url("Чистый код Роберт Мартин")
        assert " " not in url

    def test_build_query_uses_search_query(self):
        from bot.services.book_verifier import _build_query
        mat = {"title": "Чистый код", "author": "Мартин", "search_query": "Clean Code Robert Martin"}
        assert _build_query(mat) == "Clean Code Robert Martin"

    def test_build_query_fallback_to_title_author(self):
        from bot.services.book_verifier import _build_query
        mat = {"title": "Чистый код", "author": "Роберт Мартин"}
        result = _build_query(mat)
        assert "Чистый код" in result
        assert "Роберт Мартин" in result

    def test_build_query_fallback_to_title_only(self):
        from bot.services.book_verifier import _build_query
        mat = {"title": "Чистый код"}
        assert _build_query(mat) == "Чистый код"

    def test_validate_book_valid(self):
        from bot.services.book_verifier import validate_book_data
        mat = {"title": "Чистый код", "author": "Роберт Мартин", "search_query": "Clean Code Robert Martin", "type": "book"}
        assert validate_book_data(mat) is not None

    def test_validate_book_no_title_returns_none(self):
        from bot.services.book_verifier import validate_book_data
        assert validate_book_data({"title": "", "type": "book", "search_query": "something"}) is None

    def test_validate_book_short_title_returns_none(self):
        from bot.services.book_verifier import validate_book_data
        assert validate_book_data({"title": "AB", "type": "book", "search_query": "AB"}) is None

    def test_validate_book_no_search_query_returns_none(self):
        from bot.services.book_verifier import validate_book_data
        assert validate_book_data({"title": "Чистый код", "type": "book"}) is None

    def test_process_books_sets_google_url(self):
        import asyncio
        from bot.services.book_verifier import process_books_in_roadmap
        data = {"steps": [{"materials": [
            {"title": "Чистый код", "type": "book", "author": "Мартин", "search_query": "Clean Code Robert Martin", "url": "#"},
        ]}]}
        result = asyncio.run(process_books_in_roadmap(data))
        mat = result["steps"][0]["materials"][0]
        assert "google.com" in mat["url"]
        assert "pdf" in mat["url"]
        assert mat["platform"] == "Google"

    def test_process_books_removes_no_data(self):
        import asyncio
        from bot.services.book_verifier import process_books_in_roadmap
        data = {"steps": [{"materials": [
            {"title": "AB", "type": "book", "url": "#"},
        ]}]}
        result = asyncio.run(process_books_in_roadmap(data))
        assert result["steps"][0]["materials"] == []
