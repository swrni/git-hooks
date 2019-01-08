#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si

"""Tool that finds and prints python files."""

import os
import sys
import argparse

OWN_NAME = "find_pylint_errors"

class Error(Exception):
    """Custom exception for this module."""

    def __init__(self, *args, **kwargs):
        """Init method."""

        Exception.__init__(self, *args, **kwargs)

def iterate_files(args):
    """
    Return all the files in 'args.directory' and in its subdirectories. Directory and file names in
    'args.filter' are skipped.
    """

    files = []
    directory = os.path.relpath(args.directory)

    def find_files(directory_path):
        """Find all the files in the directory and append them to 'files'."""

        with os.scandir(directory_path) as iterator:
            for entry in iterator:
                if entry.name in args.filter:
                    if args.debug:
                        print(" [skipping] %s" % directory_path)
                elif entry.is_dir():
                    # Call 'find_files' recursively.
                    find_files(entry.path)
                elif entry.is_file():
                    # Append file path to 'files'.
                    files.append(entry.path)
                elif args.debug:
                    print(" [unrecognized] %s" % entry.path)

    find_files(directory)
    return files

def is_python_file(path):
    """Return boolean value indicating if 'path' points to a python file."""

    if path.endswith(".py"):
        return True
    if os.path.isfile(path):
        with open(path, errors="ignore") as open_file:
            return "python" in open_file.readline()
    return False

def parse_arguments():
    """A helper function which parses the input arguments."""

    def parse_path(path):
        """Validate that 'path' exists and turn it into absolute path."""

        if not os.path.isdir(path):
            raise Error("Path does not exist: '%s'" % path)
        return path

    def parse_list(items):
        """Make 'items' string into list of comma separated items."""

        return {item.strip() for item in items.split(",")}

    text = sys.modules[__name__].__doc__
    parser = argparse.ArgumentParser(description=text, prog=OWN_NAME)
    parser.add_argument("directory", help="Directory to look files from.", type=parse_path)
    parser.add_argument("-d", "--debug", help="Use debug logging.", action="store_true")
    parser.add_argument("--absolute-paths", help="Use absolute paths.", action="store_true")
    parser.add_argument("-f", "--filter", help="Skip these directory names when searching files.",
                        type=parse_list, default="")
    return parser.parse_args(sys.argv[1:])

def main():
    """Entry point."""

    args = parse_arguments()
    if args.debug:
        print(args)

    python_files = [file for file in iterate_files(args)
                    if is_python_file(file)]

    for path in python_files:
        if args.absolute_paths:
            path = os.path.abspath(path)
        print(path)

    return 0

if __name__ == '__main__':
    sys.exit(main())
