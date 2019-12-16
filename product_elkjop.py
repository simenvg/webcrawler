from bs4 import BeautifulSoup
import requests


class Product:
    def __init__(self, name, price, url):
        self.name = self.format_input(name)
        self.price = self.format_input(price)
        self.brand_name = "Not found"
        self.url = url

    def format_input(self, input):
        res = input.replace("\n", "")
        return ' '.join(res.split())


    def print(self):
        print(self.name + "     price: " + self.price)

def find_product(html, url):
    try:
        soup = BeautifulSoup(html, "html.parser")
        name = soup.find("h1", {"class":"product-title"}).text.strip()
        price = soup.find("div", {"class":"product-price-container"}).text.strip()
    except:
        return None
    p = Product(name, price, url)
    p.print()
    return p