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

            if len(parts) >= 5 and len(parts[3]) <= 10:
                language_code = parts[3]
                slug = parts[4]
            else:
                language_code = None
                slug = parts[3]
            qs = PageSlugHistory.objects.filter(old_slug=slug)
            if municipality:
                qs = qs.filter(page__municipality=municipality)
            if language_code:
                qs = qs.filter(page__language_code=language_code)
            hist = qs.order_by("-changed_at").first()
            if hist:
                if language_code:
                    new_path = f"/public/pages/{language_code}/{hist.new_slug}/"
                else:
                    new_path = f"/public/pages/{hist.new_slug}/"
                return HttpResponsePermanentRedirect(new_path)
        return response
