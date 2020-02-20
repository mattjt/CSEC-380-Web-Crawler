# author: Matthew Turi <mxt9495@rit.edu>

from HTTP import request


def main():
    a = request.get("https://www.rit.edu/study/computing-security-bs")
    # proxy = {
    #     "http": "http://127.0.0.1:8080",
    #     "https": "https://127.0.0.1:8080"
    # }
    # a = requests.get("https://www.rit.edu/study/computing-security-bs", proxies=proxy, verify=False)
    print(a.headers)
    print(a.data)


if __name__ == '__main__':
    main()
