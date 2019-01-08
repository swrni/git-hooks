"""Kvak."""

#pylint: disable=invalid-name

import os
import sys
# # from powerlablibs import Exceptions
# from helperlibs import Procs, Logging
from helperlibs import ArgParse, Procs

VERSION = "0.1"
OWN_NAME = "find_pylint_errors"

def iterate_files(directory, filter_list):
    """
    Walk through all the directories in 'directory' and yield each file. Path names in
    'filter_list' are skipped.
    """

    # path_prefix = os.path.relpath(directory, os.getcwd())
    for dir_path, dir_names, filenames in os.walk(directory):
        # Filter directories from dir_path.
        for index, path in enumerate(dir_names):
            if path in filter_list:
                del dir_names[index]
        # Iterate files in dir_path.
        for path in filenames:
            yield os.path.join(dir_path, path)

def is_python_file(path):
    """Return boolean value indicating if 'path' points to a python file."""

    if path.endswith(".py"):
        return True
    try:
        with open(path, errors="ignore") as open_file:
            if "python" in open_file.readline():
                return True
    except FileNotFoundError as err:
        raise RuntimeError("'%s' cannot be opened:\n\t %s" % (path, err), file=sys.stderr)

    return False

def parse_arguments():
    """Parse arguments to get the subdirectory."""

    directory = os.getcwd()

    arguments = sys.argv[1:]
    if arguments:
        directory = os.path.join(directory, arguments[0])

    return directory

    """A helper function which parses the input arguments."""

    text = sys.modules[__name__].__doc__
    parser = ArgParse.ArgsParser(description=text, prog=OWN_NAME, ver=VERSION)
    subparsers = parser.add_subparsers(title="commands", metavar="")

    text = "Clone all Server Power Lab projects."
    subparsers.add_parser("clone", help=text)

    text = "A git command to run in every Server Power Lab project"
    subparsers.add_parser("<cmd>", help=text)
    return parser.parse_args()

def main():
    """Entry point."""

    directory = parse_arguments()
    if not os.path.isdir(directory):
        print("Pass subdirectory to find python files.", file=sys.stderr)
        return 0

    print("directory: %s" % directory)

    filter_list = [".git", "__pycache__"]

    python_files = [file for file in iterate_files(directory, filter_list)
                    if is_python_file(file)]

    for path in python_files:
        print(path)
    print()

    command = "pylint --output-format=colorized --score=no --jobs=0 --verbose %s" \
              % " ".join(python_files)

    stdout, stderr, _ = Procs.run(command)
    print(stdout)
    print(stderr, file=sys.stderr)

if __name__ == '__main__':
    sys.exit(main())
    # stdout, stderr, exitcode = Procs.run(["git", "powerlab", "grep", "" ])
