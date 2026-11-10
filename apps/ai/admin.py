from django.contrib import admin
from django.db import models  # needed for formfield_overrides
from django_json_widget.widgets import JSONEditorWidget

from apps.ai.models import QueryHistory


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    # 1. List view columns
    list_display = (
        "id",
        "get_user_phone",  # user's phone number
        "user_query_short",  # long queries truncated
        "business_type",
        "region",
        "status_styled",  # colored status
        "created_at",
    )

    # 2. Filtrlarni qulaylashtirish
    list_filter = ("status", "business_type", "created_at", "user")

    # 3. Search
    search_fields = ("user__phone_number", "user_query", "region")

    # 4. Read-only fields
    readonly_fields = ("created_at", "status")

    # 5. JSON editor widget for JSON fields
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    # 6. Fieldsets
    fieldsets = (
        ("Client", {
            "fields": ("user",),
            "description": "The user who sent the query."
        }),
        ("Query details", {
            "fields": ("user_query", "business_type", "region", "status"),
        }),
        ("AI analysis (JSON)", {
            "fields": ("response_json",),
            "classes": ("extrapretty",),  # custom CSS
        }),
        ("Time", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

    # --- Display helpers ---

    @admin.display(description="User")
    def get_user_phone(self, obj):
        return obj.user.phone_number if obj.user else "Guest"

    @admin.display(description="Query")
    def user_query_short(self, obj):
        if len(obj.user_query) > 50:
            return f"{obj.user_query[:50]}..."
        return obj.user_query

    @admin.display(description="Status")
    def status_styled(self, obj):
        from django.utils.html import format_html
        colors = {
            'done': '#28a745',  # green
            'processing': '#ffc107',  # yellow
            'failed': '#dc3545',  # red
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<b style="color: {}; text-transform: uppercase;">{}</b>',
            color, obj.status
        )

    # Sahifadagi elementlar soni
    list_per_page = 20