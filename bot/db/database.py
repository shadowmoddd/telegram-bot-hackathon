from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import settings
from bot.db.models import Base

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

_MIGRATIONS = [
    "ALTER TABLE users ADD COLUMN last_active_at DATETIME",
    "ALTER TABLE user_profiles ADD COLUMN total_hours VARCHAR(50)",
    "ALTER TABLE user_profiles ADD COLUMN specialization VARCHAR(100)",
    "ALTER TABLE user_profiles ADD COLUMN goal_type VARCHAR(50)",
    "ALTER TABLE user_profiles ADD COLUMN learn_style VARCHAR(50)",
]


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for sql in _MIGRATIONS:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass
