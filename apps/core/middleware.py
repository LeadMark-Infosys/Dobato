from django.http import HttpResponseRedirect
import logging
from django.conf import settings

api_logger = logging.getLogger('api_log')

class TenantRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.global_domains = ['dobato.net', 'www.dobato.net']
        self.global_homepage = getattr(settings, "GLOBAL_HOMEPAGE", "https://dobato.net/")

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        api_logger.info(f"[TENANT CHECK] Middleware called for host: {host}, path: {request.path}")

        # Skip global domains
        if host in self.global_domains:
            return self.get_response(request)

        # Extract subdomain
        subdomain = host.split('.')[0] if '.' in host else None
        if not subdomain:
            api_logger.warning(f"No subdomain found in host '{host}', redirecting to global homepage")
            return HttpResponseRedirect(self.global_homepage)

        try:
            from apps.municipality.models import Municipality

            # Use the correct field here!
            if not Municipality.objects.filter(unique_slug=subdomain).exists():
                api_logger.info(f"Tenant '{subdomain}' not found - redirecting to global homepage")
                return HttpResponseRedirect(self.global_homepage)

        except Exception as e:
            api_logger.error(f"Tenant check failed: {e}")
            return HttpResponseRedirect(self.global_homepage)

        # Tenant exists
        return self.get_response(request)
