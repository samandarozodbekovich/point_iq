from django.contrib import admin

from apps.users.models.user_confirmation import UserConfirmation


@admin.register(UserConfirmation)
class UserConfirmationAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'expiration_time', 'is_confirmed']
    list_filter = ['is_confirmed']
    search_fields = ['code']
    ordering = ['-expiration_time']

