from sqlalchemy.ext.asyncio import AsyncSession


class BaseSQLAlchemyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
