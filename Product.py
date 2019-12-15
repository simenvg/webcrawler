from bs4 import BeautifulSoup
import requests


class Product:
    def __init__(self, name, price, brand_name="not found"):
        self.name = self.format_input(name)
        self.price = self.format_input(price)
        self.brand_name = self.format_input(brand_name)

    def format_input(self, input):
        res = input.replace("\n", "")
        return ' '.join(res.split())


    def print(self):
        print(self.name + "     brand: " + self.brand_name + "   price: " + self.price)



def find_product(html):
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
    p = Product(name, price, brand_name)
    p.print()
    return p
    


# res = requests.get("https://kolonial.no/produkter/27594-sotpotet-i-beger-usa/")
# p = find_product(res.text)
# if p != None:
#     with open('products.csv', 'w', encoding="utf-8") as file:
#         file.write("name;brand;price\n")
#         file.write(p.name + ";" + p.brand_name + ";" + p.price + "\n")
#     p.print()



        
