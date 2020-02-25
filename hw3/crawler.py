# author: Matthew Turi <mxt9495@rit.edu>
import concurrent
import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from queue import Queue
from threading import Lock
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from HTTP.request import Request, MaxRedirectsExceededError


def spawn_crawler(crawler_meta):
    """
    Crawl a URL to a given depth
    """

    Crawler(crawler_meta)


class CrawlerMeta:
    """
    Stores meta information about the site we'd like to crawl and the configuration
    options that the crawl was started with
    """

    def __init__(self, filename, start_uri, max_depth=1000, limit_to_base_uri=True):
        self.filename = filename
        self.start_uri = start_uri
        self.limit_to_base_uri = limit_to_base_uri
        self.max_depth = max_depth


class Node:
    def __init__(self, name, depth, parent):
        self.name = name
        self.depth = depth
        self.parent = parent

    def __repr__(self):
        return self.name


class Crawler:
    def __init__(self, crawler_meta):
        self.filename = crawler_meta.filename
        self.start_uri = crawler_meta.start_uri
        self.LIMIT_TO_BASE_URI = crawler_meta.limit_to_base_uri
        self.MAX_DEPTH = crawler_meta.max_depth
        self.mutex = Lock()
        self.crawled_uris = Queue()
        self.uris_to_crawl = Queue()

        root = Node(self.start_uri, 0, None)
        self.mutex.acquire()
        self.uris_to_crawl.put(root)
        self.mutex.release()

        Path("./output").mkdir(exist_ok=True)

        # We're running 1 thread per core on the system
        max_num_threads = multiprocessing.cpu_count()

        with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
            threads = []
            while not self.uris_to_crawl.empty():
                # This will empty out the queue of URLs to crawl and then wait
                while not self.uris_to_crawl.empty():
                    self.mutex.acquire()
                    node = self.uris_to_crawl.get()
                    self.mutex.release()
                    self.crawled_uris.put(node)

                    threads.append(executor.submit(self.crawl_uri, node))

                concurrent.futures.wait(threads)

    def add_new_uri_to_crawl(self, node):
        """
        Add a new URL to the set of URLs we need to crawl if it hasn't
        a.) been crawled already
        b.) been already added to the to-be-crawled list

        :param node: Node to add
        :return: Nothing
        """

        if not ((any(node.name == n.name for n in self.uris_to_crawl.queue)) or (
                any(node.name == n.name for n in self.crawled_uris.queue))):
            self.mutex.acquire()
            self.uris_to_crawl.put(node)
            with open('./output/{0}.txt'.format(self.filename), 'a') as f:
                path = urlparse(node.name).path
                f.write("{0}\n".format(path))
            self.mutex.release()

    def crawl_uri(self, current_node):
        """
        Extract all the links from a webpage

        :param current_node Node representing the current page we're crawling
        :return: nothing
        """

        if current_node.depth > self.MAX_DEPTH:
            self.mutex.acquire()
            self.uris_to_crawl.task_done()
            self.mutex.release()
            return

        try:
            a = Request().get(current_node.name)
            if current_node.depth == 0:
                current_node.name = a.uri.parsed.geturl()
            a = a.response
        except MaxRedirectsExceededError:
            return

        # We only care about parsing HTML pages, ignore everything else
        if "text/html" in a.headers.get('Content-Type'):
            soup = BeautifulSoup(a.data, 'html.parser')
        else:
            self.mutex.acquire()
            self.uris_to_crawl.task_done()
            self.mutex.release()
            return

        # Harvest links
        for link in soup.findAll('a'):
            href = link.get('href')

            # Skip links back to the base URI and page anchors
            if href in ("/", "", None) or href[:1] == "#":
                continue

            base_uri = urlparse(current_node.name)
            # Fix relative paths into absolute paths
            if href[:4] != "http":
                href = base_uri.scheme + "://" + base_uri.netloc + href

            node = Node(href, current_node.depth + 1, current_node)

            # Determine if we are scoping URLs
            if self.LIMIT_TO_BASE_URI:
                # Determine if the current URL falls into our scope
                parsed_href = urlparse(href)
                if parsed_href.netloc == base_uri.netloc:
                    # URL is in our scope. Check that it isn't a URL we've already visited
                    if parsed_href.path == "/":
                        continue

                    self.add_new_uri_to_crawl(node)
                else:
                    # Out of scope. Skip the result
                    continue
            else:
                self.add_new_uri_to_crawl(node)

        self.mutex.acquire()
        self.uris_to_crawl.task_done()
        self.mutex.release()
