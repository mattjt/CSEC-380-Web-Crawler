# author: Matthew Turi <mxt9495@rit.edu>
import concurrent
import multiprocessing
from concurrent.futures.thread import ThreadPoolExecutor
from queue import Queue
from threading import Lock
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from HTTP import request

mutex = Lock()
crawled_uris = Queue()
uris_to_crawl = Queue()
LIMIT_TO_BASE_URI = [True]
MAX_DEPTH = [1000]


class Node:
    def __init__(self, name, depth, parent):
        self.name = name
        self.depth = depth
        self.parent = parent

    def __repr__(self):
        return self.name


def add_new_uri_to_crawl(node):
    """
    Add a new URL to the set of URLs we need to crawl if it hasn't
    a.) been crawled already
    b.) been already added to the to-be-crawled list

    :param node: Node to add
    :return: Nothing
    """

    if not ((any(node.name == n.name for n in uris_to_crawl.queue)) or (
            any(node.name == n.name for n in crawled_uris.queue))):
        mutex.acquire()
        uris_to_crawl.put(node)
        mutex.release()


def crawl_uri(current_node):
    """
    Extract all the links from a webpage

    :param current_node Node representing the current page we're crawling
    :return: nothing
    """

    if current_node.depth >= MAX_DEPTH[0]:
        mutex.acquire()
        uris_to_crawl.task_done()
        mutex.release()
        return

    try:
        a = request.get(current_node.name)
    except request.MaxRedirectsExceededError:
        return

    # We only care about parsing HTML pages, ignore everything else
    if "text/html" in a.headers.get('Content-Type'):
        soup = BeautifulSoup(a.data, 'html.parser')
    else:
        mutex.acquire()
        uris_to_crawl.task_done()
        mutex.release()
        return

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
        if LIMIT_TO_BASE_URI[0]:
            # Determine if the current URL falls into our scope
            parsed_href = urlparse(href)
            if parsed_href.netloc == base_uri.netloc:
                # URL is in our scope. Check that it isn't a URL we've already visited
                if parsed_href.path == "/":
                    continue

                add_new_uri_to_crawl(node)
            else:
                # Out of scope. Skip the result
                continue
        else:
            add_new_uri_to_crawl(node)

    mutex.acquire()
    uris_to_crawl.task_done()
    mutex.release()


def crawl(start_uri, max_depth=1000, limit_to_base_uri=True):
    """
    Crawl a URL to a given depth

    :param start_uri: The URI to start crawling a site from
    :param max_depth: Maximum number of pages away from the start URI to crawl to
    :param limit_to_base_uri Should the search be limited to just domains the same as the starting URI
    :return:
    """
    MAX_DEPTH[0] = max_depth
    LIMIT_TO_BASE_URI[0] = limit_to_base_uri
    root = Node(start_uri, 0, None)
    mutex.acquire()
    uris_to_crawl.put(root)
    mutex.release()

    # We're running 1 thread per core on the system
    max_num_threads = multiprocessing.cpu_count()

    with ThreadPoolExecutor(max_workers=max_num_threads) as executor:
        threads = []
        while not uris_to_crawl.empty():
            # This will empty out the queue of URLs to crawl and then wait
            while not uris_to_crawl.empty():
                mutex.acquire()
                node = uris_to_crawl.get()
                mutex.release()
                crawled_uris.put(node)
                threads.append(executor.submit(crawl_uri, node))

            concurrent.futures.wait(threads)

    for item in crawled_uris.queue:
        print(item)
