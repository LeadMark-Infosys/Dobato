from django.http import HttpResponseNotFound
from .models import Municipality
from apps.core.tenant_context import set_current_tenant, clear_current_tenant
import logging

logger = logging.getLogger("django")

class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        subdomain = request.get_host().split(":")[0].split(".")[0].lower()
        try:
            tenant = Municipality.objects.get(unique_slug=subdomain)
        except Municipality.DoesNotExist:
            return HttpResponseNotFound("Tenant not found")
        except Exception as e:
            logger.exception(f"Tenant lookup error for '{subdomain}': {e}")
            return HttpResponseNotFound("Tenant lookup error")

        request.tenant = tenant
        set_current_tenant(tenant)
        try:
            return self.get_response(request)
        finally:
            clear_current_tenant()
