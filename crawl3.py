import multiprocessing
import requests
import queue
import logging
import os
import signal
from bs4 import BeautifulSoup
import time



class Scraper:
    def __init__(self, base_url):
        #base_url = 'http://quotes.toscrape.com/'
        manager = multiprocessing.Manager()
        self.base_url = base_url
        self.processed_urls = manager.list()
        self.local_urls = manager.list()
        self.foreign_urls = manager.list()
        self.broken_urls = manager.list()
        self.url_queue = manager.list()
        # self.url_queue = multiprocessing.Queue()
        self.logger = self.create_logger()
        self.initialize()


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
        #logger = multiprocessing.get_logger()
        print("THREAD")
        self.logger.info("QUEUELENGTH:  " + str(url_queue.qsize()))
        proc = os.getpid()
        #print(url_queue.get())
        
        while not url_queue.empty():
            #print("QUEUELENGTH:  " + str(url_queue.qsize()))
            try:
                url = url_queue.get()   
                while (url in self.processed_urls):
                    url = url_queue.get()
                self.logger.info(str(proc) + ", url: " + url)  
                self.find_links(url)
            except:
                print("Could not get from queue")
                os.kill(proc, signal.SIGTERM)
                break
        print("threadStopped")

    def scrape(self, url):
        #logger = multiprocessing.get_logger()
        print("THREAD")
        self.logger.info("QUEUELENGTH:  " + str(len(url_queue)))
        proc = os.getpid()
        #print(url_queue.get())
        
        while not url_queue.empty():
            #print("QUEUELENGTH:  " + str(url_queue.qsize()))
            try:
                url = url_queue.get()   
                while (url in self.processed_urls):
                    url = url_queue.get()
                self.logger.info(str(proc) + ", url: " + url)  
                self.find_links(url)
            except:
                print("Could not get from queue")
                os.kill(proc, signal.SIGTERM)
                break
        print("threadStopped")
        
        

    def find_links(self, url):
        try:
            res = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
            self.add_elem_if_not_in_list(self.broken_urls, url)
            self.add_elem_if_not_in_list(self.processed_urls, url)
            return
        #print(res.text)
        links = self.get_all_links_on_page(res.text)
        self.filter_links(links)
        #print(links)
        #proc = os.getpid()
        self.add_elem_if_not_in_list(self.processed_urls, url)
        
        #print(self.processed_urls)


    def add_elem_if_not_in_list(self, lst, elem):
        if elem not in lst:
            lst.append(elem)

    def get_all_links_on_page(self, html):
        links = []
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all('a'):
            if link.has_attr('href'):
                links.append(link.get("href"))
        # print("LLL:  " + links[0])
        return links
        
    def filter_links(self, links):
        new_local_links = []
        for link in links:
            link_str = str(link)
            if link_str.startswith("/"):
                new_local_links.append(self.base_url+link_str)
            elif link_str.startswith(self.base_url):
                new_local_links.append(link_str)
            else:
                self.add_elem_if_not_in_list(self.foreign_urls, link_str)
        for elem in new_local_links:
            if elem not in self.processed_urls:
                proc = os.getpid()
                # print("#####################################")
                # print(str(proc) + "   " + elem)
                # print(str(proc) + "   " + str(self.processed_urls))
                # print("#####################################")
                self.url_queue.append(elem)
            if elem not in self.local_urls:
                self.local_urls.append(elem)

    def start_worker_threads(self):
        p = multiprocessing.Pool(7)
        p.map(self.find_links, self.url_queue)




        # print("Start")
        # processes = []
        # #print("HEI:  " + self.url_queue)
        # for n in range(10):
        #     p = multiprocessing.Process(target=self.scrape, args=(self.url_queue,))
        #     # p.daemon = True
        #     processes.append(p)
        #     p.start()
        # try:
            
        #     for p in processes:
        #         print("Joining proc: " + str(p))
        #         p.join()
        #         p.terminate()
        # except KeyboardInterrupt:
        #     for p in processes:
        #         p.terminate()
        #         p.join()
        # p = Pool(10)
        # p.map(self.scrape, self.url_queue) 
        # p.terminate()
        # p.join()


# scraper = Scraper('http://quotes.toscrape.com')
# print(scraper.unvisited_local_urls)
# scraper.start_worker_threads()
# # print(scraper.all_urls)
# print(scraper.foreign_urls)
# print(scraper.processed_urls)
# print(scraper.unvisited_local_urls)
# print(scraper.broken_urls)




if __name__ == '__main__':    
    scraper = Scraper('http://quotes.toscrape.com')
    #scraper.runInParallel(numProcesses=2, numThreads=4)
    
    #print(scraper.unvisited_local_urls)
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
    # print(scraper.all_urls)
# initialize()
# start_worker_threads()
# print(broken_urls)
# print(unvisited_local_urls)
# print(visited_urls)