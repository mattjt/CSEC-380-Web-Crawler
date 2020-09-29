# author: Matthew Turi <mxt9495@rit.edu>

import os

url_pieces = set()


def split(string):
    """
    Custom split function that preserves the delimiter character

    :param string: String to split
    :return: String in it's split pieces
    """
    delimiter = u"/"
    return [e + delimiter for e in string.split(delimiter) if e]


def main():
    """
    Walk through all of the files generated by the crawl in './output' and parse them into one file

    :return: Nothing. Writes './output/paths.list'
    """

    # Walk through every file in the output directory
    for root, dirs, files in os.walk(u"./output"):
        for individual_file in files:
            file_path = os.path.join(root, individual_file)

            # Read every line in the file, split it by forward-slash characters, and add it to the set
            with open(file_path, "r", errors='ignore') as reader:
                for line in reader:
                    parts = split(line)
                    for part in parts:
                        url_pieces.add(part.replace('\n', ''))

    # Write all of the unique elements from the set to the output file on their own lines
    with open('./output/paths.list', 'w', errors='ignore') as writer:
        for item in url_pieces:
            writer.write(u"{0}\n".format(item))


if __name__ == '__main__':
    main()