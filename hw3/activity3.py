# author: Matthew Turi <mxt9495@rit.edu>
import concurrent
import csv
import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from queue import Queue

from crawler import spawn_crawler, CrawlerMeta


def main():
    """
    Activity 3
    """

    companies = Queue()
    with open('companies.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        counter = 0
        for row in csv_reader:
            if counter >= 25:
                break
            else:
                counter += 1
                companies.put(row)

    # We're running 1 thread per core on the system
    max_num_threads = multiprocessing.cpu_count()

    mutex = multiprocessing.Lock()
    print("Starting multi-site crawl at {0}".format(datetime.now().strftime("%H:%M:%S")))
    with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
        threads = []
        while not companies.empty():
            mutex.acquire()
            node = companies.get()
            mutex.release()
            crawler_meta = CrawlerMeta(node[0], node[1], max_depth=4)
            threads.append(executor.submit(spawn_crawler, crawler_meta))

        concurrent.futures.wait(threads)
    print("Finished crawl at {0}".format(datetime.now().strftime("%H:%M:%S")))


if __name__ == '__main__':
    main()
