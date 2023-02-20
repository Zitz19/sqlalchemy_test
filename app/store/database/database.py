from typing import Optional, TYPE_CHECKING
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.store.database import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        database_url = 'postgresql+asyncpg://kts_user:kts_pass@localhost/kts'
        self._engine = create_async_engine(database_url, echo=True, future=True)
        self.session = sessionmaker(self._engine, expire_on_commit=False, future=True, class_=AsyncSession)

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self.session:
            async with self.app.database.session() as session:
                session: AsyncSession
                async with session.begin():
                    await session.execute('TRUNCATE admins CASCADE')
                    await session.execute('TRUNCATE themes CASCADE')
                await session.commit()
        if self._engine:
            await self._engine.dispose()
