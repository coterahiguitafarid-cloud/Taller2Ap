from django.contrib import admin

from store.models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "api_customer_id")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("api_customer_id",)
