import multiprocessing
import requests
import queue  # queue.Empty exception
import os
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from urllib import robotparser
import product_kolonial



class Scraper:
    def __init__(self, base_url, num_threads, max_requests_per_second, subdomains):
        manager = multiprocessing.Manager()
        self.base_url = base_url
        self.num_threads = num_threads
        self.max_requests_per_second = max_requests_per_second
        self.subdomains = subdomains
        
        self.robottxt = self.init_robot_parser()

        self.processed_urls = manager.list()
        self.local_urls = manager.list()
        self.foreign_urls = manager.list()
        self.broken_urls = manager.list()
        self.ignored_urls = manager.list()

        self.url_queue = multiprocessing.Queue()
        self.queue_lock = multiprocessing.Lock()

        self.products = manager.list()
        self.product_lock = multiprocessing.Lock()

        self.initialize()
        
    def initialize(self):
        self.process_url(self.base_url)

    def init_robot_parser(self):
        robparser = robotparser.RobotFileParser()
        robparser.set_url(self.base_url + "/robots.txt")
        try:
            robparser.read()
            return robparser
        except Exception as e:
            print(e)
            print("could not find robots.txt on url: " + self.base_url + "/robots.txt")
            exit(0)
    
    def scrape(self, url_queue):
        proc = os.getpid()
        print("Thread: " + str(proc) +" started")
        while True:
            if len(self.processed_urls) % 200 == 0:
                print(" \n \n processed urls: " + str(len(self.processed_urls)) + "\n\n")

            # Ensure max requests per second
            time.sleep(self.num_threads / self.max_requests_per_second)

            url = self.get_unprocessed_url_from_queue(url_queue)
            if url != None:
                self.process_url(url)
                print(url)
            else:
                time.sleep(0.5)
                if url_queue.empty():
                    break
                else:
                    continue
        print("Thread: " + str(proc) + " Stopped")
        
    def get_unprocessed_url_from_queue(self, url_queue):
        self.queue_lock.acquire()
        try:
            url = url_queue.get_nowait()
            while url in self.processed_urls:
                url = url_queue.get_nowait()
            self.processed_urls.append(url)
            self.queue_lock.release()
            return url
        except queue.Empty:
            self.queue_lock.release()
            return None

    def process_url(self, url):
        try:
            res = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.TooManyRedirects):
            print("BROKEN URL")
            if url not in self.broken_urls:
                self.broken_urls.append(url)
        else:
            # Get links on page
            links = self.get_all_links_on_page(res.text)
            self.process_links(links, url)

            # Find product on page
            product = product_kolonial.find_product(res.text, url) 
            if product != None:
                self.append_product(product)

    def get_all_links_on_page(self, html):
        links = []
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                links.append(self.get_full_url(str(link.get("href"))))
        return links
        
    def process_links(self, links, url):    
        new_local_links = []
        for link in links:
            if self.ignore_url(link):
                # DISALLOW in robot.txt or outside user search filter 
                continue
            elif link.startswith(self.base_url):
                new_local_links.append(link)
            else:
                if link not in self.foreign_urls:
                    self.foreign_urls.append(link)
        for elem in new_local_links:
            if elem not in self.processed_urls:
                self.url_queue.put(elem)
            if elem not in self.local_urls:
                self.local_urls.append(elem)

    def get_full_url(self, url):
        if url.startswith("/"):
            return self.base_url + url
        else:
            return url

    def append_product(self, new_product):
        self.product_lock.acquire()
        # print(str(os.getpid()) + "Aquired lock")
        product_already_in_products = False
        for product in self.products:
            if new_product.name == product.name and new_product.price == product.price:
                product_already_in_products = True
        if not product_already_in_products:
            self.products.append(new_product)
        # print(str(os.getpid()) + "Releasing lock")
        self.product_lock.release()

    def ignore_url(self, full_url):
        if '?' in full_url:
            return True
        if self.robottxt.can_fetch("*", full_url) and self.url_in_user_search_filter(full_url):
            return False
        else:
            if not self.robottxt.can_fetch("*", full_url):
                print("robots.txt blocked request to: " + full_url)
            self.ignored_urls.append(full_url)
            return True

    def url_in_user_search_filter(self, full_url):
        if not self.subdomains:
            return True
        else:
            path = urlparse(full_url).path
            for subdomain in self.subdomains:
                if path.startswith(subdomain):
                    return True
        return False


    def start_worker_threads(self):
        processes = []
        for n in range(self.num_threads):
            p = multiprocessing.Process(target=self.scrape, args=(self.url_queue,))
            processes.append(p)
            p.start()
        try:
            for p in processes:
                p.join()
                p.terminate()
        except KeyboardInterrupt:
            for p in processes:
                p.terminate()
                p.join()


def start_scraper(base_url, num_threads, max_requests_per_second, subdomains):
    scraper = Scraper(base_url, num_threads, max_requests_per_second, subdomains)
    t0 = time.time()
    scraper.start_worker_threads()
    t1 = time.time()

    print("\n\n ##################################################### \n")
    print("Scraper finished")
    print("Elapsed time in seconds: " + str(t1-t0))
    print("Processed " + str(len(scraper.processed_urls)) + "  urls")
    print("Found " + str(len(scraper.foreign_urls)) + " foreign urls")
    print("Found " + str(len(scraper.broken_urls)) + " broken urls  (includes urls not starting with https or /)")
    print("Found " + str(len(scraper.local_urls)) + " local urls")
    print("Found " + str(len(scraper.products)) + " products")
    print(scraper.foreign_urls)
    timestr = time.strftime("%Y%m%d-%H%M%S")
    with open('products'+'_'+timestr+'.csv', 'w', encoding="utf-8") as file:
        file.write("Name;Brand;Price;URL\n")
        for product in scraper.products:
            file.write(product.name + ";" + product.brand_name + ";" + product.price + ";" + product.url  + "\n")

