import csv

from dotenv import dotenv_values
import requests

SECRETS = dotenv_values(".env")
ROOT = SECRETS["SHOPIFY_URL"]


def get_products():
    def get_images(images):
        formated = []
        for i in images.split(", "):
            formated.append({"src": i})
        return formated

    # -fix.csv file removes some problematic chars
    with open("data/cocolea/cocolea-products-fix.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        products = []
        for row in reader:
            product = {
                # hardcoded
                "product_type": "Forniture",
                "vendor": "Cocolea",
                "tags": "Cocolea, " + row["Attribute 2 value(s)"].replace(" &gt; ", ", ").replace("&amp;", "&"),
                "template_suffix": "",
                # Init
                "title": row["Name"],
                "sku": row["SKU"],
                "body_html": f'{row["Description"]}\n{row["Short description"]}',
                "price": row["Regular price"],
                "images": get_images(row["Images"]),
                "weight": row["Weight (kg)"],
                # Metafields
                "foreign_id": row["ID"],
                "lenght": row["Length (cm)"],
                "price_sale": row["Sale price"],
                "width": row["Width (cm)"],
                "height": row["Height (cm)"],
                "categories": row["Categories"],
                "google_product_category": row["Attribute 2 value(s)"],
            }
            products.append(product)
        return products


def create_product(p):
    payload = {
        "product": {
            "title": p["title"],
            "product_type": p["product_type"],
            "template_suffix": p["template_suffix"],
            "body_html": p["body_html"],
            "vendor": p["vendor"],
            "tags": p["tags"],
            "variants": [{"price": p["price"], "weight": p["weight"], "sku": p["sku"]}],
            "images": p["images"],
        }
    }

    r = requests.post(
        url=f"{ROOT}/products.json",
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json=payload,
    )

    return r.json()["product"]


def add_source_id(product, value):
    payload = {
        "product": {
            "id": product["id"],
            "metafields": [
                {
                    "namespace": "source",
                    "key": "product_id",
                    "value": value,
                    "value_type": "string",
                }
            ],
        }
    }

    r = requests.put(
        url=f"{ROOT}/products/{product['id']}.json",
        json=payload,
        headers={"Content-Type": "application/json"},
    )
    return r.json()["product"]


def init(p):
    x = create_product(p)
    add_source_id(x, p["foreign_id"])
    return x
