from typing import List

from loguru import logger
import csv

from shop.models import Product


class CsvTextBuilder(object):
    def __init__(self):
        self.csv_string = []

    def write(self, row):
        self.csv_string.append(row)


def products_csv_builder(products: List[Product]):
    csv_items_array = [
        [
            "id",
            "title",
            "description",
            "rich_text_description",
            "availability",
            "condition",
            "price",
            "link",
            "image_link",
            "brand",
            "additional_image_link",
            "product_type",
            "sale_price",
            "size",
            "status",
            "inventory",
        ]
    ]
    for product in products:
        csv_items_array.append(
            [
                product.id,
                product.name,
                product.description,
                product.description,
                "in stock" if product.is_available else "out of stock",
                "new",
                f"{product.price} USD",
                f"https://mboma.modestnerd.co/api/1.0/products/{product.id}",
                product.image.url,
                "Tregers",
                product.image_alt.url,
                f"{product.price} USD",
                "published",
                product.inventory.quantity,
            ]
        )

    logger.info(f"csv items -> {csv_items_array}")
    csv_file = CsvTextBuilder()
    writer = csv.writer(csv_file)
    writer.writerows(csv_items_array)
    csv_string = csv_file.csv_string
    logger.info(f"csv string -> {csv_string}")
    return "".join(csv_string)
