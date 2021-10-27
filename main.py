import bfa
import shop


def main():
    products = bfa.get_products()
    for x in products:
        p = shop.create(x)
        print(f"Created: https://thebigdino.myshopify.com/admin/products/{p['id']}")


try:
    main()
except KeyboardInterrupt:
    pass
