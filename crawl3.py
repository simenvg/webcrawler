import multiprocessing
import requests
import queue  # queue.Empty exception
import logging
import os
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse



class Scraper:
    def __init__(self, base_url, restricted_urls, subdomains):
        manager = multiprocessing.Manager()
        self.base_url = base_url
        self.restricted_urls = restricted_urls
        self.subdomains = subdomains
        self.processed_urls = manager.list()
        self.local_urls = manager.list()
        self.foreign_urls = manager.list()
        self.broken_urls = manager.list()
        self.url_queue = multiprocessing.Queue()
        self.logger = self.create_logger()
        self.initialize()
        self.max_requests_per_second = 3
        self.num_threads = 15


    def initialize(self):
        self.find_links(self.base_url)

    def create_logger(self):
        logger = multiprocessing.get_logger()
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('process.log')
        fmt = '%(asctime)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(fmt)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger  
    
    def scrape(self, url_queue):
        proc = os.getpid()
        print("Thread: " + str(proc) +" started")
        proc = os.getpid()
        while True:
            print("processed urls: " + str(len(self.processed_urls)))
            print("unprocessed urls: " + str(len(self.local_urls) - len(self.processed_urls)))
            time.sleep(self.num_threads / self.max_requests_per_second)
            try:
                url = url_queue.get_nowait()
                while url in self.processed_urls:
                    url = url_queue.get_nowait()
                self.find_links(url)
            except queue.Empty:
                time.sleep(0.5)
                if url_queue.empty():
                    break
                else:
                    continue
            except Exception as e:
                print("Excepition : " + e)
                continue
            
        print("Thread: " + str(proc) + " Stopped")
        

    def find_links(self, url):
        try:
            # Add time restriction here?
            res = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.TooManyRedirects):
            print("BROKEN URL")
            self.add_elem_if_not_in_list(self.broken_urls, url)
            self.add_elem_if_not_in_list(self.processed_urls, url)
        else:
            links = self.get_all_links_on_page(res.text)
            self.filter_links(links, url)
            self.add_elem_if_not_in_list(self.processed_urls, url)


    def add_elem_if_not_in_list(self, lst, elem):
        if elem not in lst:
            lst.append(elem)

    def get_all_links_on_page(self, html):
        links = []
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                links.append(link.get("href"))
        return links
        
    def filter_links(self, links, url):
        new_local_links = []
        for link in links:
            link_str = str(link)
            if self.ignore_url(link_str):
                continue
            elif link_str.startswith("/"):
                #Should be url, and not baseurl
                new_local_links.append(self.base_url+link_str)
            elif link_str.startswith(self.base_url):
                new_local_links.append(link_str)
            else:
                self.add_elem_if_not_in_list(self.foreign_urls, link_str)
        for elem in new_local_links:
            if elem not in self.processed_urls:
                self.url_queue.put(elem)
            if elem not in self.local_urls:
                self.local_urls.append(elem)

    def ignore_url(self, url):
        if url.startswith("/"):
            url = self.base_url + url
        path = urlparse(url).path
        if path == "":
            return False
        for elem in self.restricted_urls:
            if elem.startswith(path):
                #print("IGNORING:   " + url)
                return True
        for elem in self.subdomains:
            if  path.startswith(elem):                
                return False
        return True

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





if __name__ == '__main__':    
    ignore = ["/handlekurv/partial/", "/handlekurv/products/", "/handlekurv/toggle/", "/handlelister/ajax/0/products/", "/handlelister/ajax/new/", "/sok/boost/", "/utlevering/postnummeroppslag/â€Ž", "/utlevering/postnummeroppslag/â€Žbedrift/", "/utlevering/ajax/delivery-availability/"]    
    subdomains = ["/produkter", "/kategorier", "/oppskrifter"]
    scraper = Scraper('https://kolonial.no', ignore, subdomains)
    
    print("HEI")
    t0 = time.time()
    scraper.start_worker_threads()
    t1 = time.time()
    print("TIME: " + str(t1-t0))
    print("broken: " + str(scraper.broken_urls)+ "    length: " + str(len(scraper.broken_urls)))
    print("foreign: " + str(scraper.foreign_urls) + "    length: " + str(len(scraper.foreign_urls)))
    print("local: " + str(scraper.local_urls)+ "    length: " + str(len(scraper.local_urls)))
    print("processed: " + str(scraper.processed_urls) + "    length: " + str(len(scraper.processed_urls)))
    print("TIME: " + str(t1-t0))
