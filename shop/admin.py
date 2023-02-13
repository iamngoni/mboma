from django.contrib import admin

from shop.models import (
    ApiRequest,
    ProductCategory,
    ProductInventory,
    Product,
    Discount,
    Order,
)


@admin.register(ApiRequest, ProductCategory, ProductInventory, Product, Discount, Order)
class UniversalAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.concrete_fields]
