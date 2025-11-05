from django.contrib import admin

from apps.users.models.user import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name','is_staff')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ("-created_at",)
    readonly_fields = ('created_at',"updated_at")

admin.site.register(User, UserAdmin)