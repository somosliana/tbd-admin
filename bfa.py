import json
from dotenv import dotenv_values
import requests
import htmlmin
from bs4 import BeautifulSoup
from requests.models import HTTPBasicAuth

SECRETS = dotenv_values(".env")


def fetch():
    endpoint = SECRETS["BAR_FRIDGES_AUSTRALIA_ENDPOINT"]
    username = SECRETS["BAR_FRIDGES_AUSTRALIA_USERNAME"]
    password = SECRETS["BAR_FRIDGES_AUSTRALIA_PASSWORD"]
    r = requests.get(endpoint, auth=HTTPBasicAuth(username, password))
    return r.json()


def get_url(sku):
    api_key = SECRETS["SEARCHANISE_API_KEY"]
    url = f"https://www.searchanise.com/getwidgets?api_key={api_key}&maxResults=100&q={sku}"
    r = requests.get(url)
    items = r.json()["items"]
    result = list(
        filter(lambda x: x["product_code"] == sku and int(x["quantity"]) >= 0, items)
    )[0]

    return result["link"]


def get_images(images):
    formated = []
    for i in images:
        formated.append({"src": i})
    return formated


def get_body_html(soup):
    def clean_soup(soup):
        for tag in soup():
            for attribute in ["class", "id"]:
                del tag[attribute]
        return soup

    def fix_anchors(soup):
        for a in soup.findAll("a"):
            a["href"] = f"https://www.bar-fridges-australia.com.au{a['href']}"
        return soup

    soup = soup.find(id="product-guide-hook-energy")
    soup = clean_soup(soup)
    soup = fix_anchors(soup)
    prettified = soup.prettify()
    minified = htmlmin.minify(prettified)
    return minified


def get_initial_state(soup):
    raw = soup.find("script").string.strip()
    data = raw.split("window.__INITIAL_STATE__ = ")[1].split(";\n")[0]
    parsed = json.loads(data)
    return parsed["products_view_extended_product"]


def get_products():
    back = fetch()
    active = list(filter(lambda x: x["active"], back))
    products = []
    for x in active[:2]:
        url = get_url(x["product_code"])
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        front = get_initial_state(soup)
        p = {
            "title": x["product_name"],
            "vendor": x["brand"],
            "tags": "Bar Fridges Australia",
            "sku": x["product_code"],
            "price": x["price"],
            "url": url,
            "weight": x["weight"],
            "width": x["width"],
            "height": x["height"],
            "depth": x["depth"],
            "images": get_images(x["product_images"]),
            "body_html": get_body_html(soup),
            "available": front["quantity"],
        }
        products.append(p)
    return products
