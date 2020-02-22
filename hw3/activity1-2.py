# author: Matthew Turi <mxt9495@rit.edu>

import multiprocessing
from pathlib import Path
from queue import Queue
from threading import Thread

from bs4 import BeautifulSoup

from HTTP import request


def download_image(download_queue):
    while not download_queue.empty():
        item = download_queue.get()
        img = request.get(item['data-src'])
        file_ext = img.headers.get('Content-Type').rsplit("/", 1)[-1]
        tmp = open("./output/{0}.{1}".format(item['alt'], file_ext), 'w+b')
        tmp.write(img.data)
        tmp.close()
        download_queue.task_done()


def main():
    """
    Activity 1.2
    """

    a = request.get("https://www.rit.edu/computing/directory?term_node_tid_depth=4919")
    soup = BeautifulSoup(a.data, 'html.parser')

    staff_imgs = soup.findAll("img", class_="card-img-top")

    Path("./output").mkdir(exist_ok=True)

    download_queue = Queue()
    for img in staff_imgs:
        download_queue.put(img)

    # We're running 1 thread per core on the system
    num_threads = multiprocessing.cpu_count()

    for i in range(num_threads):
        worker = Thread(target=download_image, args=(download_queue,))
        worker.start()

    # Wait until all the queue items have been processed
    download_queue.join()


if __name__ == '__main__':
    main()
