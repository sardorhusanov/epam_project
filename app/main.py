from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.container import Container
from app.lifespan import build_lifespan
from app.shared.db import model_registry
from app.shared.exceptions.handlers import register_exception_handlers
from app.shared.logging.config import configure_logging
from app.shared.middleware.request_logging import RequestLoggingMiddleware


def create_app(container: Container | None = None) -> FastAPI:
    application_container = container or Container()
    settings = application_container.settings()
    configure_logging(settings.DEBUG)

    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=build_lifespan(application_container),
    )
    application.container = application_container
    application.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(application)
    application.include_router(auth_router)

    @application.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    return application


app = create_app()