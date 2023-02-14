from django.db import models

from mboma.model import SoftDeleteModel
from users.models import User


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

    def __str__(self):
        return self.name


class Product(SoftDeleteModel):
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products"
    )
    SKU = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    image = models.ImageField(upload_to="images/", null=False, blank=False)
    image_alt = models.ImageField(upload_to="images/", null=False, blank=False)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        table_prefix = "prod"

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        # use inventory to determine if product is available
        return self.inventory.quantity > 0


class ProductInventory(SoftDeleteModel):
    quantity = models.IntegerField(default=0)
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="inventory"
    )

    class Meta:
        verbose_name = "Product Inventory"
        verbose_name_plural = "Product Inventories"
        table_prefix = "inv"

    def __str__(self):
        return self.product.name


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

    def __str__(self):
        return f"Discount - {self.name} - {self.product.name}"


class Order(SoftDeleteModel):
    user = models.ForeignKey(
        "users.User",
        related_name="orders",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    amount = models.FloatField(default=0, blank=False, null=False)
    paid = models.BooleanField(default=False, blank=False, null=False)
    payment_method = models.CharField(max_length=10, blank=False, null=False)
    narration = models.TextField(blank=False, null=False)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        table_prefix = "ord"


class Cart(SoftDeleteModel):
    user = models.OneToOneField(
        "users.User",
        related_name="cart",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = "Shopping Cart"
        verbose_name_plural = "Shopping Carts"
        table_prefix = "shcart"

    @classmethod
    def create_cart_or_get_cart(cls, user: User):
        try:
            return cls.objects.get(user=user)
        except cls.DoesNotExist:
            cart = cls(user=user)
            cart.save()
            return cart

    def add_cart_item_or_create_cart_item(self, product: Product, quantity: int):
        try:
            cart_item = self.items.get(product=product)
            cart_item.quantity = quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            cart_item = CartItem(
                cart=self,
                product=product,
                quantity=quantity,
            )
            cart_item.save()
            return cart_item

    @property
    def total(self):
        amount = 0
        for item in self.items.all():
            amount += item.product.price * item.quantity

        return amount


class CartItem(SoftDeleteModel):
    cart = models.ForeignKey(
        "shop.Cart",
        related_name="items",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    product = models.ForeignKey(
        "shop.Product",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    quantity = models.IntegerField(default=1, null=False, blank=False)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        table_prefix = "shcart_itm"

    @property
    def total(self):
        return self.quantity * self.product.price
