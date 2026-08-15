from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

class Base(DeclarativeBase):
    pass

_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None

def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        try:
            _engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                future=True,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
            )
        except Exception:
            try:
                import aiosqlite
                _engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)
            except ImportError:
                # Stub engine for offline static analysis/unit testing of non-DB modules
                _engine = None
    return _engine

def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        eng = get_engine()
        if eng is not None:
            _session_factory = async_sessionmaker(
                bind=eng,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
    return _session_factory

# Proxy objects for backward compatibility
class EngineProxy:
    def __getattr__(self, name):
        eng = get_engine()
        if eng is None:
            raise RuntimeError(
                "Database driver (asyncpg) is not installed in the local environment. "
                "Please run inside Docker or install requirements via 'pip install -r requirements.txt'."
            )
        return getattr(eng, name)

class SessionFactoryProxy:
    def __call__(self, *args, **kwargs):
        factory = get_session_factory()
        if factory is None:
            raise RuntimeError(
                "Database driver (asyncpg) is not installed in the local environment. "
                "Please run inside Docker or install requirements via 'pip install -r requirements.txt'."
            )
        return factory(*args, **kwargs)

engine = EngineProxy()
AsyncSessionLocal = SessionFactoryProxy()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    if factory is None:
        raise RuntimeError("Database session factory is uninitialized.")
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
