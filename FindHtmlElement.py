from bs4 import BeautifulSoup
import requests


# This file is for testing new sites, inspect the 
# site and find the html elements that suits your needs.

URL = "https://www.elkjop.no/product/styling-og-velvare/barbermaskin-og-trimmer/MG771015/philips-series-7000-multitrimmer-mg7710-15"
HTML_ELEMENT = "div"
TAG = "class"
TAG_VALUE = "product-price-container"


def format_input(input):
    res = input.replace("\n", "")
    return ' '.join(res.split())

name = None
try:
    # Add time restriction here?
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")
    name = format_input(soup.find(HTML_ELEMENT, {TAG:TAG_VALUE}).text.strip())
except Exception as e:
    print("error")
    print(e)
    exit(0)


print("Requested url: " + URL)
print("Found element: " + HTML_ELEMENT + "  with tag: " + TAG + " = " + TAG_VALUE)
print(" RESULT: " + name)