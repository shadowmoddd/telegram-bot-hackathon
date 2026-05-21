"""
Тесты углублённого профиля и верификации книг.
Запуск: pytest tests/test_deep_profile.py -v
"""
import pytest

from bot.services.profile_service import (
    LEARN_STYLE_LABELS, LEARN_STYLE_VALUES,
    format_profile_summary,
)
from bot.services.book_verifier import (
    validate_book_data, process_books_in_roadmap, _google_books_search_url, _build_query,
)


class TestLearnStyleLabels:
    def test_all_keys_present(self):
        expected = {"theory_practice", "practice", "examples", "structured"}
        assert set(LEARN_STYLE_LABELS.keys()) == expected

    def test_values_non_empty(self):
        for key, val in LEARN_STYLE_VALUES.items():
            assert val, f"Empty value for key '{key}'"


class TestDeepProfileSummary:
    def _full_data(self):
        return {
            "goal": "стать Python разработчиком",
            "sphere": "it",
            "level": "intermediate",
            "time_per_week": "3to5",
            "total_hours": "40",
            "formats": ["video", "course"],
            "learn_style": "practice",
        }

    def test_learn_style_shown(self):
        summary = format_profile_summary(self._full_data())
        assert "Стиль обучения" in summary
        assert "практик" in summary.lower()

    def test_all_fields_present(self):
        summary = format_profile_summary(self._full_data())
        for field in ["Цель", "Уровень", "Стиль обучения", "Форматы"]:
            assert field in summary, f"'{field}' missing from summary"

    def test_missing_learn_style_shows_dash(self):
        data = self._full_data()
        data["learn_style"] = None
        summary = format_profile_summary(data)
        assert "—" in summary


class TestFSMStatesDeepProfile:
    def test_learn_style_state_exists(self):
        from bot.fsm.states import ProfileForm
        assert hasattr(ProfileForm, "learn_style")

    def test_states_order(self):
        from bot.fsm.states import ProfileForm
        states = list(ProfileForm.__states__)
        names = [str(s) for s in states]
        goal_idx = next(i for i, s in enumerate(names) if "goal" in s)
        quiz_idx = next(i for i, s in enumerate(names) if "quiz" in s)
        time_idx = next(i for i, s in enumerate(names) if "time_per_week" in s)
        ls_idx = next(i for i, s in enumerate(names) if "learn_style" in s)
        assert goal_idx < quiz_idx < time_idx < ls_idx


class TestBookVerifier:
    def test_google_books_search_url(self):
        url = _google_books_search_url("Clean Code Robert Martin")
        assert "google.com" in url
        assert "Clean" in url
        assert "pdf" in url

    def test_build_query_prefers_search_query(self):
        mat = {"title": "Чистый код", "author": "Мартин", "search_query": "Clean Code"}
        assert _build_query(mat) == "Clean Code"

    def test_validate_book_with_search_query(self):
        mat = {
            "title": "Чистый код", "author": "Роберт Мартин",
            "search_query": "Clean Code Robert Martin",
            "type": "book"
        }
        result = validate_book_data(mat)
        assert result is not None

    def test_validate_book_no_title_returns_none(self):
        mat = {"title": "", "type": "book", "search_query": "something"}
        assert validate_book_data(mat) is None

    def test_validate_book_short_title_returns_none(self):
        mat = {"title": "AB", "type": "book", "search_query": "AB"}
        assert validate_book_data(mat) is None

    def test_validate_book_no_search_query_returns_none(self):
        mat = {"title": "Чистый код", "type": "book"}
        assert validate_book_data(mat) is None


class TestKeyboards:
    def test_learn_style_keyboard_has_4_buttons(self):
        from bot.keyboards.inline import learn_style_keyboard
        kb = learn_style_keyboard()
        buttons = [b for row in kb.inline_keyboard for b in row]
        assert len(buttons) == 4

    @pytest.mark.parametrize("kbd,prefix", [
        ("learn_style_keyboard", "lstyle_"),
    ])
    def test_callbacks_have_correct_prefix(self, kbd, prefix):
        import bot.keyboards.inline as kbs
        kb = getattr(kbs, kbd)()
        for row in kb.inline_keyboard:
            for btn in row:
                assert btn.callback_data.startswith(prefix), \
                    f"Bad callback in {kbd}: {btn.callback_data}"
