from django.urls import path

from api.views.bot.views import WebhookView
from api.views.shop.views import ProductDetailsView, ProductsCSVView

urlpatterns = [
    path("bot", WebhookView.as_view(), name="bot"),
    path("products_catalog/csv", ProductsCSVView.as_view(), name="products csv view"),
    path(
        "products/<str:pk>", ProductDetailsView.as_view(), name="product details view"
    ),
]
