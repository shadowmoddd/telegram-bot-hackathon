from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.config import FORMAT_ICONS, SOURCE_ICONS, TOPICS, LEVELS
from bot.keyboards.inline import route_item_kb, route_list_kb, topics_kb, start_route_kb
from recommender.engine import (
    get_user, get_route, update_item_status, update_user_profile,
    build_route, save_route,
)

router = Router()


def format_resource_card(res, position: int, total: int, status: str = "pending") -> str:
    icon = FORMAT_ICONS.get(res.format, "📌")
    source = SOURCE_ICONS.get(res.source, "🔗 Ресурс")
    level_map = {"beginner": "🌱 Начальный", "intermediate": "🌿 Средний", "advanced": "🌳 Продвинутый"}
    level = level_map.get(res.level, res.level)

    status_line = ""
    if status == "completed":
        status_line = "\n✅ <i>Изучено</i>"
    elif status == "skipped":
        status_line = "\n⏭ <i>Пропущено</i>"

    duration = f"\n⏱ Примерно {res.duration_h:.0f} ч" if res.duration_h else ""

    desc = ""
    if res.description:
        desc = f"\n\n💬 {res.description[:200]}{'…' if len(res.description) > 200 else ''}"

    return (
        f"📍 <b>Ресурс {position + 1} из {total}</b>{status_line}\n\n"
        f"{icon} <b>{res.title}</b>\n"
        f"🏷 {source} · {level}{duration}\n"
        f"🔗 <a href='{res.url}'>{res.url}</a>"
        f"{desc}"
    )


async def show_route_item(callback_or_message, telegram_id: int, edit: bool = True):
    user = get_user(telegram_id)
    if not user or not user.topic:
        text = "Профиль не заполнен. Напиши /start чтобы начать."
        if edit:
            await callback_or_message.message.edit_text(text)
        else:
            await callback_or_message.answer(text)
        return

    route = get_route(user.id)
    if not route:
        text = "Маршрут пустой. Напиши /start чтобы создать маршрут."
        if edit:
            await callback_or_message.message.edit_text(text)
        else:
            await callback_or_message.answer(text)
        return

    pos = user.current_position or 0
    pos = max(0, min(pos, len(route) - 1))

    item, res = route[pos]
    total = len(route)
    text = format_resource_card(res, pos, total, item.status)

    kb = route_item_kb(pos, total, res.id)
    if edit:
        await callback_or_message.message.edit_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    else:
        await callback_or_message.answer(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


@router.callback_query(F.data == "nav:start")
async def cb_nav_start(callback: CallbackQuery):
    update_user_profile(callback.from_user.id, current_position=0)
    await show_route_item(callback, callback.from_user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data == "nav:next")
async def cb_nav_next(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден")
        return
    pos = (user.current_position or 0) + 1
    route = get_route(user.id)
    pos = min(pos, len(route) - 1)
    update_user_profile(callback.from_user.id, current_position=pos)
    await show_route_item(callback, callback.from_user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data == "nav:prev")
async def cb_nav_prev(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден")
        return
    pos = max((user.current_position or 0) - 1, 0)
    update_user_profile(callback.from_user.id, current_position=pos)
    await show_route_item(callback, callback.from_user.id, edit=True)
    await callback.answer()


@router.callback_query(F.data.startswith("item:done:"))
async def cb_item_done(callback: CallbackQuery):
    resource_id = int(callback.data.split(":")[2])
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    update_item_status(user.id, resource_id, "completed")

    route = get_route(user.id)
    pos = user.current_position or 0
    next_pos = pos + 1

    if next_pos >= len(route):
        done = sum(1 for item, _ in route if item.status == "completed")
        await callback.message.edit_text(
            f"🎉 <b>Маршрут завершён!</b>\n\n"
            f"Ты изучил <b>{done}</b> из <b>{len(route)}</b> ресурсов.\n\n"
            "Хочешь выбрать новую тему или получить больше материалов?",
            parse_mode="HTML",
            reply_markup=route_list_kb(),
        )
    else:
        update_user_profile(callback.from_user.id, current_position=next_pos)
        await show_route_item(callback, callback.from_user.id, edit=True)

    await callback.answer("✅ Отмечено как изученное!")


@router.callback_query(F.data.startswith("item:skip:"))
async def cb_item_skip(callback: CallbackQuery):
    resource_id = int(callback.data.split(":")[2])
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    update_item_status(user.id, resource_id, "skipped")

    route = get_route(user.id)
    pos = (user.current_position or 0) + 1
    pos = min(pos, len(route) - 1)
    update_user_profile(callback.from_user.id, current_position=pos)
    await show_route_item(callback, callback.from_user.id, edit=True)
    await callback.answer("⏭ Пропущено")


@router.callback_query(F.data == "route:list")
async def cb_route_list(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user:
        await callback.answer()
        return

    route = get_route(user.id)
    if not route:
        await callback.message.edit_text("Маршрут пустой.", reply_markup=route_list_kb())
        await callback.answer()
        return

    status_icons = {"pending": "⬜️", "completed": "✅", "skipped": "⏭"}
    lines = []
    for item, res in route:
        icon = status_icons.get(item.status, "⬜️")
        fmt = FORMAT_ICONS.get(res.format, "📌")
        lines.append(f"{icon} {fmt} {res.title}")

    done = sum(1 for item, _ in route if item.status == "completed")
    text = (
        f"📋 <b>Твой маршрут</b> ({done}/{len(route)} изучено):\n\n"
        + "\n".join(lines)
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=start_route_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "route:new")
async def cb_route_new(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    if not user or not user.topic:
        await callback.message.edit_text("Выбери тему:", reply_markup=topics_kb())
        await callback.answer()
        return

    await callback.message.edit_text("⏳ Строю новый маршрут...")
    resources = build_route(user)

    if not resources:
        await callback.message.edit_text(
            "😔 Ресурсы не найдены. Попробуй изменить профиль.",
            reply_markup=route_list_kb(),
        )
        await callback.answer()
        return

    save_route(user.id, resources)
    update_user_profile(callback.from_user.id, current_position=0)

    await callback.message.edit_text(
        f"✅ Новый маршрут из <b>{len(resources)}</b> ресурсов готов!",
        parse_mode="HTML",
        reply_markup=start_route_kb(),
    )
    await callback.answer()


@router.message(Command("route"))
async def cmd_route(message: Message):
    await show_route_item(message, message.from_user.id, edit=False)
