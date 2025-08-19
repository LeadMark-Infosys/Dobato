from django.http import HttpResponsePermanentRedirect
from .models import PageSlugHistory


class SlugHistoryRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/")
        parts = path.split("/")
        if len(parts) >= 4 and parts[1] == "public" and parts[2] == "pages":
            slug = parts[3]
            hist = (
                PageSlugHistory.objects.filter(old_slug=slug)
                .order_by("-changed_at")
                .first()
            )
            if hist:
                new_path = path.replace(slug, hist.new_slug)
                return HttpResponsePermanentRedirect(new_path)
        return self.get_response(request)
