from django.urls import path

from api.views.bot.views import WhatsAppView, PaynowView
from api.views.shop.views import ProductDetailsView, ProductsCSVView

urlpatterns = [
    path("bot", WhatsAppView.as_view(), name="WhatsApp View"),
    path("paynow", PaynowView.as_view(), name="Paynow View"),
    path(
        "products_catalog/csv",
        ProductsCSVView.as_view(),
        name="Products Catalog Upload View",
    ),
    path(
        "products/<str:pk>", ProductDetailsView.as_view(), name="Product Details View"
    ),
]
