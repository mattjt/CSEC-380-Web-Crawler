# author: Matthew Turi <mxt9495@rit.edu>

import os

directories = set()


def split(string):
    delimiter = u"/"
    return [e + delimiter for e in string.split(delimiter) if e]


def main():
    for root, dirs, files in os.walk(u"./output"):
        # traverse root directory, and list directories as dirs and files as files
        for individual_file in files:
            file_path = os.path.join(root, individual_file)

            with open(file_path, "r", errors='ignore') as reader:
                for line in reader:
                    parts = split(line)
                    for part in parts:
                        directories.add(part.replace('\n', ''))

    with open('./output/paths.list', 'w', errors='ignore') as writer:
        for item in directories:
            writer.write(u"{0}\n".format(item))


if __name__ == '__main__':
    main()
