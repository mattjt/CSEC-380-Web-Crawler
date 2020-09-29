# author: Matthew Turi <mxt9495@rit.edu>

from HTTP import request
from bs4 import BeautifulSoup


def main():
    """
    Activity 1
    """
    a = request.get("https://www.rit.edu/study/computing-security-bs/")

    soup = BeautifulSoup(a.data, 'html.parser')

    course_table = soup.find_all('table', class_="table-curriculum")

    course_list = set()

    for table in course_table:
        rows = table.find_all('tr')

        for tr in rows:
            td = tr.find_all('td')

            if len(td) == 3 and td[0].contents[0].strip() != '':
                course_num = td[0].contents[0].strip()
                course_name = td[1].find('div', class_="course-name").contents[0].strip()
                course_list.update(["{0}, {1}".format(course_num, course_name)])

    with open('./output/act1-courselist.csv', 'w', newline='') as file:
        file.write("course_num, course_title\n")

        print("course_num, course_title")
        for row in list(course_list):
            print(row)
            file.write(row)
            file.write("\n")


if __name__ == '__main__':
    main()
