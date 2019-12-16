from bs4 import BeautifulSoup
import requests


class Product:
    def __init__(self, name, price, url, brand_name):
        self.url = url
        self.name = self.format_input(name)
        self.price = self.format_input(price)
        self.brand_name = self.format_input(brand_name)

    def format_input(self, input):
        res = input.replace("\n", "")
        return ' '.join(res.split())


    def print(self):
        print(self.name + "     brand: " + self.brand_name + "   price: " + self.price)

def find_product(html, url):
    try:
        soup = BeautifulSoup(html, "html.parser")
        name = soup.find("span", {"itemprop":"name"}).text.strip()
        price = soup.find("div", {"class":"price"}).text.strip()
    except:
        #print("No products found")
        return None
    brand_name = None
    try:
        brand_name = soup.find("span", {"itemprop":"brand"}).text.strip()
    except:
        brand_name = "Not found"
    p = Product(name, price, url, brand_name)
    p.print()
    return p
