from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shared.settings import CommonSettings


class DBProvider(Provider):
    @provide(scope=Scope.APP)
    async def engine(self, settings: CommonSettings) -> AsyncEngine:
        return create_async_engine(
            settings.db.URL, pool_pre_ping=True, pool_recycle=3600
        )

    @provide(scope=Scope.APP)
    async def sessionmaker(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def session(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session
