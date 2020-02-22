# author: Matthew Turi <mxt9495@rit.edu>

from pathlib import Path

from bs4 import BeautifulSoup

from HTTP import request


def download_image(filename, url):
    img = request.get(url)
    file_ext = img.headers.get('Content-Type').rsplit("/", 1)[-1]
    tmp = open("./output/{0}.{1}".format(filename, file_ext), 'w+b')
    tmp.write(img.data)
    tmp.close()


def main():
    """
    Activity 1.2
    """

    a = request.get("https://www.rit.edu/computing/directory?term_node_tid_depth=4919")
    soup = BeautifulSoup(a.data, 'html.parser')

    staff_imgs = soup.findAll("img", class_="card-img-top")

    Path("./output").mkdir(exist_ok=True)

    for img in staff_imgs:
        download_image(img['alt'], img['data-src'])


if __name__ == '__main__':
    main()
