from django.contrib import admin
from django.forms import JSONField
from django_json_widget.widgets import JSONEditorWidget

from apps.ai.models import QueryHistory


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "user_query",
        "business_type",
        "region",
        "created_at",
    )
    list_filter = (
        "business_type",
        "created_at",
        "user",
    )
    search_fields = ("user__phone_number", "user_query", "region")
    ordering = ("-created_at",)


    # JSONField ni chiroyli editor bilan ochish
    # open JSONField comfortably by editor

    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }

    readonly_fields = ("created_at",)

    fieldsets = (
        ("User Info", {
            "fields": ("user",)
        }),
        ("Query Info", {
            "fields": ("user_query", "business_type", "region")
        }),
        ("AI Response", {
            "fields": ("response_json",)
        }),
        ("Meta", {
            "fields": ("created_at",),
            "classes": ("collapse",)   # collapsed section
        }),
    )
