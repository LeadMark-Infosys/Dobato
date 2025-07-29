from django.contrib import admin
from .models import User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in User._meta.fields]
    search_fields = ('email', 'name', 'user_type')
    ordering = ('name',)
