from db.database import get_session
from db.models import Resource, User, UserRoute
from bot.config import ROUTE_SIZE


LEVEL_EXPAND = {
    "beginner": ["beginner"],
    "intermediate": ["beginner", "intermediate"],
    "advanced": ["intermediate", "advanced"],
}


def build_route(user: User) -> list[Resource]:
    session = get_session()
    try:
        limit = ROUTE_SIZE.get(user.time_available or "medium", 7)
        levels = LEVEL_EXPAND.get(user.level or "beginner", ["beginner"])

        query = session.query(Resource).filter(
            Resource.topic == user.topic,
            Resource.level.in_(levels),
            Resource.is_free == True,
            Resource.language == "ru",
        )

        if user.format_pref and user.format_pref != "any":
            query_fmt = query.filter(Resource.format == user.format_pref)
            resources = query_fmt.order_by(Resource.rating.desc()).limit(limit).all()
            if len(resources) < 3:
                resources = query.order_by(Resource.rating.desc()).limit(limit).all()
        else:
            resources = query.order_by(Resource.rating.desc()).limit(limit).all()

        if len(resources) < 3:
            resources = (
                session.query(Resource)
                .filter(Resource.topic == user.topic, Resource.is_free == True)
                .order_by(Resource.rating.desc())
                .limit(limit)
                .all()
            )

        # Sort by level progression: beginner → intermediate → advanced
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        resources = sorted(resources, key=lambda r: level_order.get(r.level, 1))
        return resources
    finally:
        session.close()


def save_route(user_db_id: int, resources: list[Resource]) -> None:
    session = get_session()
    try:
        session.query(UserRoute).filter(UserRoute.user_id == user_db_id).delete()
        for pos, res in enumerate(resources):
            item = UserRoute(user_id=user_db_id, resource_id=res.id, position=pos)
            session.add(item)
        session.commit()
    finally:
        session.close()


def get_route(user_db_id: int) -> list[tuple[UserRoute, Resource]]:
    session = get_session()
    try:
        items = (
            session.query(UserRoute, Resource)
            .join(Resource, UserRoute.resource_id == Resource.id)
            .filter(UserRoute.user_id == user_db_id)
            .order_by(UserRoute.position)
            .all()
        )
        return [(item, res) for item, res in items]
    finally:
        session.close()


def update_item_status(user_db_id: int, resource_id: int, status: str) -> None:
    session = get_session()
    try:
        item = (
            session.query(UserRoute)
            .filter(UserRoute.user_id == user_db_id, UserRoute.resource_id == resource_id)
            .first()
        )
        if item:
            item.status = status
            session.commit()
    finally:
        session.close()


def get_or_create_user(telegram_id: int, username: str | None = None) -> User:
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    finally:
        session.close()


def update_user_profile(telegram_id: int, **kwargs) -> None:
    session = get_session()
    try:
        user = session.query(User).filter(User.telegram_id == telegram_id).first()
        if user:
            for key, value in kwargs.items():
                setattr(user, key, value)
            session.commit()
    finally:
        session.close()


def get_user(telegram_id: int) -> User | None:
    session = get_session()
    try:
        return session.query(User).filter(User.telegram_id == telegram_id).first()
    finally:
        session.close()
