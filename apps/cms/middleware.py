from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin
from .models import PageSlugHistory


class SlugHistoryRedirectMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code != 404 or request.method != "GET":
            return response
        path = request.path.rstrip("/")
        parts = path.split("/")
        if len(parts) >= 4 and parts[1] == "public" and parts[2] == "pages":
            municipality = getattr(request, "tenant", None)
            slug = parts[3]
            qs = PageSlugHistory.objects.filter(old_slug=slug)
            if municipality:
                qs = qs.filter(page__municipality=municipality)
            hist = qs.order_by("-changed_at").first()
            if hist:
                new_path = path.replace(slug, hist.new_slug)
                return HttpResponsePermanentRedirect(new_path + "/")
        return response
