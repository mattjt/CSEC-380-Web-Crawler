# author: Matthew Turi <mxt9495@rit.edu>

from HTTP import request


def main():
    """
    Activity 1
    """
    a = request.get("https://www.rit.edu/study/computing-security-bs/")
    print(a.headers)
    print(a.data)


if __name__ == '__main__':
    main()
