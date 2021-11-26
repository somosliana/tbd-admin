from suppliers import bfa, cocolea
import shop

def run_bfa():
    products = bfa.get_products()
    for x in products:
        p = shop.create_bfa_product(x)
        print(f"🔗 https://thebigdino.myshopify.com/admin/products/{p['id']}")

def run_cocolea():
    products = cocolea.get_products()
    for x in products:
        p = cocolea.init(x)
        print(f"🔗 https://thebigdino.myshopify.com/admin/products/{p['id']}")

try:
    run_bfa()
except KeyboardInterrupt:
    pass
