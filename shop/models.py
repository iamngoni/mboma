from django.db import models

from mboma.model import SoftDeleteModel


class ApiRequest(SoftDeleteModel):
    method = models.CharField(max_length=6, default="GET", blank=True, null=True)
    path = models.CharField(max_length=255, blank=True, null=True)
    headers = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "API Request"
        verbose_name_plural = "API Requests"
        table_prefix = "req"


class ProductCategory(SoftDeleteModel):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        table_prefix = "cat"


class ProductInventory(SoftDeleteModel):
    quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Product Inventory"
        verbose_name_plural = "Product Inventories"
        table_prefix = "inv"


class Product(SoftDeleteModel):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products"
    )
    SKU = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    inventory = models.OneToOneField(
        ProductInventory, on_delete=models.CASCADE, related_name="product"
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        table_prefix = "prod"


class Discount(SoftDeleteModel):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    active = models.BooleanField(default=False)
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="discount"
    )

    class Meta:
        verbose_name = "Discount"
        verbose_name_plural = "Discounts"
        table_prefix = "disc"
