from django.http import HttpResponseNotFound

from .models import Municipality
from apps.core.tenant_context import set_current_tenant, clear_current_tenant

class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        parts = host.split(".")
        if len(parts) < 2:
            return HttpResponseNotFound("Invalid domain format")
        subdomain = parts[0].lower()
        try:
            tenant = Municipality.objects.get(unique_slug=subdomain)
            request.tenant = tenant
            set_current_tenant(tenant)
        except Municipality.DoesNotExist:
            return HttpResponseNotFound("Tenant not found")
        response = self.get_response(request)
        clear_current_tenant()
        return response
