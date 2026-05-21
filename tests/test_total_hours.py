"""
Тесты для функциональности total_hours (бюджет часов на маршрут).
Запуск: pytest tests/test_total_hours.py -v
"""
import pytest

from bot.services.profile_service import (
    TOTAL_HOURS_LABELS,
    TOTAL_HOURS_VALUES,
    format_profile_summary,
)
from bot.services.content_verifier import is_russian_text


# ──────────────────────────────────────────────
# Тесты TOTAL_HOURS_LABELS
# ──────────────────────────────────────────────

class TestTotalHoursLabels:
    def test_all_keys_present(self):
        expected = {"10", "20", "40", "80", "80plus"}
        assert set(TOTAL_HOURS_LABELS.keys()) == expected

    def test_all_values_non_empty(self):
        for key, label in TOTAL_HOURS_LABELS.items():
            assert label, f"Empty label for key '{key}'"

    def test_values_match_keys_in_values_dict(self):
        assert set(TOTAL_HOURS_LABELS.keys()) == set(TOTAL_HOURS_VALUES.keys())

    @pytest.mark.parametrize("key,expected_substring", [
        ("10", "10"),
        ("20", "20"),
        ("40", "40"),
        ("80", "80"),
        ("80plus", "80"),
    ])
    def test_label_contains_hours(self, key, expected_substring):
        assert expected_substring in TOTAL_HOURS_LABELS[key]


# ──────────────────────────────────────────────
# Тесты format_profile_summary с total_hours
# ──────────────────────────────────────────────

class TestProfileSummaryWithTotalHours:
    def _base_data(self, total_hours="40"):
        return {
            "goal": "стать разработчиком",
            "sphere": "it",
            "level": "beginner",
            "time_per_week": "3to5",
            "total_hours": total_hours,
            "formats": ["video"],
            "learn_style": "practice",
        }

    def test_total_hours_shown_in_summary(self):
        data = self._base_data("40")
        summary = format_profile_summary(data)
        assert "Всего часов" in summary
        assert "20–40" in summary

    def test_total_hours_80plus(self):
        data = self._base_data("80plus")
        summary = format_profile_summary(data)
        assert "80+" in summary

    def test_missing_total_hours_shows_not_specified(self):
        data = self._base_data(total_hours=None)
        data["total_hours"] = None
        summary = format_profile_summary(data)
        assert "не указано" in summary

    def test_summary_has_required_fields(self):
        data = self._base_data()
        summary = format_profile_summary(data)
        for field in ["Цель", "Уровень", "Всего часов"]:
            assert field in summary, f"'{field}' not found in summary"


# ──────────────────────────────────────────────
# Тесты is_russian_text
# ──────────────────────────────────────────────

class TestIsRussianText:
    @pytest.mark.parametrize("text,expected", [
        ("Введение в Python", True),
        ("Python Tutorial for Beginners", False),
        ("Основы машинного обучения", True),
        ("HTML CSS basics", False),
        ("SQL для анализа данных", True),
        ("React JS course", False),
        ("", True),   # пустой — не фильтруем
        ("SQL", True),  # слишком короткий — не фильтруем
    ])
    def test_detection(self, text, expected):
        assert is_russian_text(text) == expected, f"Failed for: {text!r}"

    def test_mixed_text_with_enough_cyrillic_passes(self):
        assert is_russian_text("Python курс для начинающих разработчиков") is True

    def test_mostly_latin_fails(self):
        assert is_russian_text("Advanced Python Development Course") is False


# ──────────────────────────────────────────────
# Тесты keyboard total_hours_keyboard
# ──────────────────────────────────────────────

class TestTotalHoursKeyboard:
    def test_keyboard_has_5_buttons(self):
        from bot.keyboards.inline import total_hours_keyboard
        kb = total_hours_keyboard()
        buttons = [btn for row in kb.inline_keyboard for btn in row]
        assert len(buttons) == 5

    def test_all_callbacks_start_with_hours(self):
        from bot.keyboards.inline import total_hours_keyboard
        kb = total_hours_keyboard()
        for row in kb.inline_keyboard:
            for btn in row:
                assert btn.callback_data.startswith("hours_"), \
                    f"Bad callback: {btn.callback_data}"

    def test_callback_keys_match_labels(self):
        from bot.keyboards.inline import total_hours_keyboard
        kb = total_hours_keyboard()
        callbacks = {btn.callback_data.replace("hours_", "")
                     for row in kb.inline_keyboard for btn in row}
        assert callbacks == set(TOTAL_HOURS_LABELS.keys())


# ──────────────────────────────────────────────
# Тесты FSM states
# ──────────────────────────────────────────────

class TestFSMStates:
    def test_total_hours_state_exists(self):
        from bot.fsm.states import ProfileForm
        assert hasattr(ProfileForm, "total_hours")

    def test_state_order_correct(self):
        from bot.fsm.states import ProfileForm
        states = list(ProfileForm.__states__)
        time_idx = next(i for i, s in enumerate(states) if "time_per_week" in str(s))
        hours_idx = next(i for i, s in enumerate(states) if "total_hours" in str(s))
        formats_idx = next(i for i, s in enumerate(states) if "formats" in str(s))
        assert time_idx < hours_idx < formats_idx, \
            "total_hours must be between time_per_week and formats"
