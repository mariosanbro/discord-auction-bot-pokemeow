from typing import Type, Any
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta
from src.database.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./src/database/database.db"

class DatabaseManager:
    def __init__(self, database_url: str) -> None:
        self.database_url: str = database_url
        self.engine: AsyncEngine = create_async_engine(database_url, echo=True, future=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
    async def fetch_all(self, model: Type[DeclarativeMeta]) -> list[DeclarativeMeta]:
        async with self.async_session() as session:
            query = select(model)
            result = await session.execute(query)
            return result.scalars().all()
    
    async def fetch_one(self, table: Type[DeclarativeMeta], **kwargs) -> DeclarativeMeta | None:
        async with self.async_session() as session:
            query = select(table).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalars().first()
        
    async def insert(self, instance: Type[DeclarativeMeta]) -> bool:
        async with self.async_session() as session:
            session.add(instance)
            try:
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                print(e)
                return False
        
    async def update(self, model: Type[DeclarativeMeta], where: dict[str, Any], **kwargs) -> bool:
        async with self.async_session() as session:
            query = select(model).filter_by(**where)
            result = await session.execute(query)
            instance: DeclarativeMeta | None = result.scalars().first()
            if not instance:
                return False
            for key, value in kwargs.items():
                setattr(instance, key, value)
            try:
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                print(e)
                return False
                
        
    async def delete(self, table: Type[DeclarativeMeta], **kwargs) -> bool:
        async with self.async_session() as session:
            query = select(table).filter_by(**kwargs)
            result = await session.execute(query)
            instance: DeclarativeMeta | None = result.scalars().first()
            if not instance:
                return False
            await session.delete(instance)
            try:
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                print(e)
                return False
            
    # Only used for tests
    async def drop_tables(self) -> bool:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            return True
