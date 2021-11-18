from dotenv import dotenv_values
import requests

SECRETS = dotenv_values(".env")
ROOT = SECRETS["SHOPIFY_URL"]


def init(title, body_html, vendor, tags, sku, price, weight, images):
    payload = {
        "product": {
            "title": title,
            "product_type": "Refrigerators",
            "body_html": body_html,
            "vendor": vendor,
            "tags": tags,
            "variants": [{"price": price, "weight": weight, "sku": sku}],
            "images": images,
            "template_suffix": "barfridgesaustralia",
        }
    }

    r = requests.post(
        url=f"{ROOT}/products.json",
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json=payload,
    )

    return r.json()["product"]


def add_metadata(product, namespace, key, value, value_type):
    id = product["id"]
    payload = {
        "product": {
            "id": id,
            "metafields": [
                {
                    "namespace": namespace,
                    "key": key,
                    "value": value,
                    "value_type": value_type,
                }
            ],
        }
    }

    r = requests.put(
        url=f"{ROOT}/products/{id}.json",
        json=payload,
        headers={"Content-Type": "application/json"},
    )


def add_nontaxable(product):
    variant = product["variants"][0]
    id = variant["id"]
    payload = {"variant": {"taxable": False}}

    r = requests.put(
        url=f"{ROOT}/variants/{id}.json",
        json=payload,
        headers={"Content-Type": "application/json"},
    )


def add_cost(product, price):
    def calculate_cost(price):
        price = float(price)
        margin = 12
        difference = price * margin * 0.01
        return price - difference

    variant = product["variants"][0]
    inventory_item_id = variant["inventory_item_id"]
    cost = calculate_cost(price)
    tracked = True
    payload = {
        "inventory_item": {"id": inventory_item_id, "cost": cost, "tracked": tracked}
    }

    r = requests.put(
        url=f"{ROOT}/inventory_items/{inventory_item_id}.json",
        json=payload,
        headers={"Content-Type": "application/json"},
    )


def add_quantity(product, available):
    inventory_item_id = product["variants"][0]["inventory_item_id"]
    location_id = 65102381243
    payload = {
        "location_id": location_id,
        "inventory_item_id": inventory_item_id,
        "available": available,
    }

    r = requests.post(
        url=f"{ROOT}/inventory_levels/set.json",
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json=payload,
    )

def add_product_variants(product, options):
    for o in options:
        title = o.option_name
        options = []
        for k, v in o.variants:
            options.append(v.variant_name)
        print(title)
        print(options)

def create_bfa_product(p):
    title = p["title"]
    body_html = p["body_html"]
    vendor = p["vendor"]
    tags = p["tags"]
    sku = p["sku"]
    price = p["price"]
    weight = p["weight"]
    images = p["images"]
    available = p["available"]

    pointer = init(title, body_html, vendor, tags, sku, price, weight, images)

    add_nontaxable(pointer)
    add_cost(pointer, price)
    add_quantity(pointer, available)

    # metafields
    id = p["id"]
    url = p["url"]
    width = p["width"]
    depth = p["depth"]
    height = p["height"]
    add_metadata(pointer, "source", "product_id", id, "string")
    add_metadata(pointer, "source", "url", url, "string")
    add_metadata(pointer, "dimensions", "depth", depth, "integer")
    add_metadata(pointer, "dimensions", "height", height, "integer")
    add_metadata(pointer, "dimensions", "width", width, "integer")

    # product variant
    add_product_variants(pointer, p["options"])

    return pointer


def create_cocolea_product(p):
    title = p["title"]
    body_html = p["body_html"]
    vendor = p["vendor"]
    tags = p["tags"]
    sku = p["sku"]
    price = p["price"]
    weight = p["weight"]
    images = p["images"]
    pointer = init(title, body_html, vendor, tags, sku, price, weight, images)
