from dependency_injector import containers, providers

from app.auth.service import AuthService
from app.shared.cache.redis import RedisCacheService
from app.shared.config.settings import Settings
from app.shared.db.session import create_engine, create_session_factory
from app.shared.security.jwt import TokenManager
from app.shared.security.password import PasswordManager
from app.users.repository import UserRepository


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app.auth"])

    settings = providers.Singleton(Settings)

    engine = providers.Singleton(
        create_engine,
        database_url=settings.provided.DATABASE_URL,
        echo=settings.provided.DEBUG,
    )
    session_factory = providers.Singleton(create_session_factory, engine=engine)

    cache_service = providers.Singleton(
        RedisCacheService, redis_url=settings.provided.REDIS_URL
    )
    password_manager = providers.Singleton(PasswordManager)
    token_manager = providers.Singleton(TokenManager, settings=settings)

    user_repository = providers.Factory(UserRepository, session_factory=session_factory)
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository,
        cache=cache_service,
        password_manager=password_manager,
        token_manager=token_manager,
    )
