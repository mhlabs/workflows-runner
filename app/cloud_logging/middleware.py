import contextvars
import sys

from fastapi.logger import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

cloud_trace_context = contextvars.ContextVar('cloud_trace_context', default='')
http_request_context = contextvars.ContextVar('http_request_context', default=dict({}))


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if 'x-cloud-trace-context' in request.headers:
            cloud_trace_context.set(request.headers.get('x-cloud-trace-context'))

        http_request = {
            'requestMethod': request.method,
            'requestUrl': request.url.path,
            'requestSize': sys.getsizeof(request),
            'remoteIp': request.client.host,
            'protocol': request.url.scheme,
        }

        if 'referrer' in request.headers:
            http_request['referrer'] = request.headers.get('referrer')

        if 'user-agent' in request.headers:
            http_request['userAgent'] = request.headers.get('user-agent')

        http_request_context.set(http_request)

        try:
            return await call_next(request)
        except Exception as ex:
            logger.debug(f'Request failed: {ex}')
            return JSONResponse(
                status_code=500,
                content={
                    'success': False,
                    'message': ex
                }
            )
