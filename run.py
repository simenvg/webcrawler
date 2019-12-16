import argparse
import textwrap
import Scraper



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Webcrawler",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=textwrap.dedent("""
    This program finds href links in html a element, and adds them to a queue. 
    Threads go through the links and continously adds unvisited links to the 
    queue. On each link the crawler tries to find a product and its price, 
    and adds this to a list. When the program finishes it writes all found 
    products are written to products to csv in project root folder"""),
    usage=textwrap.dedent(
    '''
    python main.py https://kolonial.no 6 10 /produkter,/oppskrifter,/kategorier
    '''))



    parser.add_argument("base_url", help="Base url for where the crawler should start")
    parser.add_argument("num_threads", type=int, help="Number of threads running")
    parser.add_argument("rps", type=int, help="Max requests per second")
    parser.add_argument("search_paths", help="Only request pages that begins with these paths, separate with comma")
    args = parser.parse_args()

    base_url = args.base_url
    num_threads = args.num_threads
    max_requests_per_second = args.rps
    subdomains = args.search_paths.split(',')

    print(base_url)
    print(num_threads)
    print(max_requests_per_second)
    print(subdomains)


    Scraper.start_scraper(base_url, num_threads, max_requests_per_second, subdomains)





