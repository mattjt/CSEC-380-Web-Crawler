# author: Matthew Turi <mxt9495@rit.edu>

import crawler


def main():
    """
    Activity 2
    """

    crawler.crawl("https://www.rit.edu", max_depth=2)


if __name__ == '__main__':
    main()
