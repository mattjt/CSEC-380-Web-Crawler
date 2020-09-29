# author: Matthew Turi <mxt9495@rit.edu>
import multiprocessing
from datetime import datetime
from queue import Queue
from threading import Lock, Thread

from HTTP.request import Request

ROOT_URI = "http://csec380-core.csec.rit.edu:83/"
mutex = Lock()
found_pages = set()
ignore_page_response_code = ['404']


def check_url(paths_list):
    while not paths_list.empty():
        path = paths_list.get()
        try:
            a = Request().get(ROOT_URI + path, ignore_body=True)

            # Page probably exists
            if not (a.response.status_code in ignore_page_response_code):
                mutex.acquire()
                found_pages.add(path)
                mutex.release()

        except AttributeError:
            pass

        paths_list.task_done()


def main():
    """
    Activity 4
    """

    paths_list = Queue()
    with open('./paths.list') as paths:
        for path in paths:
            paths_list.put(path.strip().replace(' ', ''))

    print("Starting crawl at {0}".format(datetime.now().strftime("%H:%M:%S")))

    # We're running 1 thread per core on the system
    num_threads = multiprocessing.cpu_count()

    for i in range(num_threads):
        worker = Thread(target=check_url, args=(paths_list,))
        worker.start()

    # Wait until all the queue items have been processed
    paths_list.join()

    print("Finished crawl at {0}".format(datetime.now().strftime("%H:%M:%S")))

    print("Found paths:")
    for found in found_pages:
        print(found)

    with open('./found-pages.list', 'w') as fp:
        for page in found_pages:
            fp.write('{0}\n'.format(page))


if __name__ == '__main__':
    main()
