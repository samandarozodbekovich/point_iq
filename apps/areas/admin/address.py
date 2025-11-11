from django.contrib import admin

from apps.areas.address.models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name_uz','district')
    search_fields = ('name_uz',)
    list_filter = ('district',)