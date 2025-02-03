from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.database_url,
)

AsyncSessionLocal = async_sessionmaker(expire_on_commit=False, bind=engine)
