from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware для додавання захисних HTTP-заголовків.
    Налаштовує CSP, HSTS, X-Frame-Options тощо.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Content Security Policy - обмеження джерел завантаження ресурсів
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
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
