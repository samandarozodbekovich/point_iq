from django.contrib import admin
from django.db import models  # Muhim: formfield_overrides uchun db.models kerak
from django_json_widget.widgets import JSONEditorWidget

from apps.ai.models import QueryHistory


@admin.register(QueryHistory)
class QueryHistoryAdmin(admin.ModelAdmin):
    # 1. Ro'yxat ko'rinishini boyitish
    list_display = (
        "id",
        "get_user_phone",  # Telefon raqamini chiroyli ko'rsatish
        "user_query_short",  # Uzun so'rovlarni qisqartirib ko'rsatish
        "business_type",
        "region",
        "status_styled",  # Statusni rangli ko'rsatish
        "created_at",
    )

    # 2. Filtrlarni qulaylashtirish
    list_filter = ("status", "business_type", "created_at", "user")

    # 3. Qidiruvni kuchaytirish
    search_fields = ("user__phone_number", "user_query", "region")

    # 4. Faqat o'qish uchun maydonlar
    readonly_fields = ("created_at", "status")

    # 5. JSON Editor widgetini to'g'ri ulash
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    # 6. Admin paneldagi maydonlar strukturasi (Fieldsets)
    fieldsets = (
        ("Mijoz haqida", {
            "fields": ("user",),
            "description": "So'rov yuborgan foydalanuvchi ma'lumotlari."
        }),
        ("So'rov tafsilotlari", {
            "fields": ("user_query", "business_type", "region", "status"),
        }),
        ("AI Tahlili (JSON)", {
            "fields": ("response_json",),
            "classes": ("extrapretty",),  # Custom CSS uchun
        }),
        ("Vaqt", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )

    # --- Yordamchi metodlar (Optimallashtirish uchun) ---

    @admin.display(description="Foydalanuvchi")
    def get_user_phone(self, obj):
        return obj.user.phone_number if obj.user else "Mehmon"

    @admin.display(description="So'rov")
    def user_query_short(self, obj):
        if len(obj.user_query) > 50:
            return f"{obj.user_query[:50]}..."
        return obj.user_query

    @admin.display(description="Status")
    def status_styled(self, obj):
        from django.utils.html import format_html
        colors = {
            'done': '#28a745',  # Yashil
            'processing': '#ffc107',  # Sariq
            'failed': '#dc3545',  # Qizil
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<b style="color: {}; text-transform: uppercase;">{}</b>',
            color, obj.status
        )

    # Sahifadagi elementlar soni
    list_per_page = 20