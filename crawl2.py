from multiprocessing import Pool
import requests
from bs4 import BeautifulSoup



class Scraper:
    def __init__(self, base_url):
        #base_url = 'http://quotes.toscrape.com/'
        self.base_url = base_url
        self.all_urls = list()
        self.unvisited_local_urls = list()
        self.processed_urls = list()
        self.local_urls = list()
        self.foreign_urls = list()
        self.broken_urls = list()
        self.initialize()

    def initialize(self):
        self.unvisited_local_urls.append(self.base_url)
        self.scrape(self.base_url)
        
    
    def scrape(self, url):
        res = None
        if (url.startswith('/')):
            url = self.base_url + url
        try:
            res = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
            self.broken_urls.append(url)
            return
        print("URL: " + url)
        #print(res.text)
        links = self.get_all_links_on_page(res.text)
        self.filter_links(links)
        #print(links)
        self.processed_urls.append(url)
        self.unvisited_local_urls.remove(url)

                

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
                self.foreign_urls.append(link_str)
        self.unvisited_local_urls = self.get_unique_elems_in_list(self.unvisited_local_urls, new_local_links)


    def get_unique_elems_in_list(self, list1, list2):
        unique_elem_list = list1
        for elem in list2:
            if elem not in list1:
                unique_elem_list.append(elem)
        return unique_elem_list

    def get_unvisited_url(self):
        try:
            print("HEI")
            print(self.unvisited_local_urls)
            url = self.unvisited_local_urls[0]

            while url not in self.processed_urls:
                self.unvisited_local_urls.remove(url)
                url = self.unvisited_local_urls[0]
            return url    
        except Exception as e:
            print(e)
            return None
        
    def start_worker_thread(self):
        url = self.get_unvisited_url()
        print("HALLO:  " + str(url))
        if url != None:
            self.scrape(url)

    def start_worker_threads(self):
        print(self.unvisited_local_urls)
        while (len(self.unvisited_local_urls)):
            p = Pool(10)
            p.map(self.start_worker_thread, None) 
            p.terminate()
            p.join()


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
    scraper.start_worker_threads()
    # print(scraper.all_urls)
    print(scraper.foreign_urls)
# initialize()
# start_worker_threads()
# print(broken_urls)
# print(unvisited_local_urls)
# print(visited_urls)