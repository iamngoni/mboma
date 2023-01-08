from django.http import HttpResponse
from loguru import logger
from rest_framework.views import APIView

from api.views.shop.serializers import ProductSerializer
from services.helpers.api_response import api_response
from services.helpers.products_csv_builder import products_csv_builder
from shop.models import Product


class ProductsCSVView(APIView):
    def get(self, request):
        products = Product.objects.all()
        logger.info(f"products -> {products}")
        csv = products_csv_builder(products)
        logger.info(f"csv string -> {csv}")
        csv_content = csv.encode("utf-8")
        logger.info(f"csv content -> {csv_content}")
        return HttpResponse(
            status=200,
            content_type="application/octet-stream",
            content=csv_content,
        )


class ProductDetailsView(APIView):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return api_response(request, data={"product": ProductSerializer(product).data})
