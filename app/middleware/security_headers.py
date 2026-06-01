from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Маршрути Swagger UI / ReDoc — застосовуємо пом'якшений CSP
DOCS_PATHS = {"/docs", "/redoc", "/openapi.json"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для додавання захисних HTTP-заголовків.
    Для /docs та /redoc застосовується пом'якшений CSP,
    щоб Swagger UI міг завантажити ресурси з CDN.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        is_docs = request.url.path in DOCS_PATHS

        if is_docs:
            # Пом'якшений CSP для Swagger UI / ReDoc
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' "
                "https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net https://unpkg.com; "
                "worker-src blob:; "
                "frame-ancestors 'none'"
            )
        else:
            # Суворий CSP для всіх інших маршрутів
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "frame-ancestors 'none'"
            )

        # Захист від Clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Заборона MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Контроль передачі реферера
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Захист від XSS у застарілих браузерах
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response
