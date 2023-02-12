#
#  product_section.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.
from typing import List

from shop.models import Product


class ProductSection:
    def __init__(self, title: str, products: List[Product]):
        self.title = title
        self.products = products
