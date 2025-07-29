import logging
import json

api_logger = logging.getLogger('api_log')
class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        body = None 
        try:
            body = request.body.decode('utf-8')
            body_json = json.loads(body)
            body_str = json.dumps(body_json, separators=(',', ':'))
        except Exception:
            body_str = body if body else '[no body]'
        response = self.get_response(request)
        if request.path.startswith('/api/'):
            api_logger.info(
                f"{request.method} {request.path} - Status: {response.status_code} - Body: {body_str}"
            )
        return response
