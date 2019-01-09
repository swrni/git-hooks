#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si

"""Tool that runs pylint on python files in a chosen directory."""

import os
import sys
import argparse

from process import Process

OWN_NAME = "find_pylint_errors"

def parse_arguments():
    """Parse arguments to get the subdirectory."""

    def parse_list(items):
        """Make 'items' string into list of comma separated items."""

        return {item.strip() for item in items.split(",")}

    text = sys.modules[__name__].__doc__
    parser = argparse.ArgumentParser(description=text, prog=OWN_NAME)
    parser.add_argument("--only", help="Show only these pylint warnings.", type=parse_list)
    parser.add_argument("directory", help="Find files inside this directory.", default="",
                        nargs="?")
    return parser.parse_args(sys.argv[1:])

def get_files(args):
    """Call 'find_python_files.py' and return python files."""

    filter_list = [".git", "__pycache__"]
    find_files_command = "python ./find_python_files.py"
    if args.debug:
        find_files_command += " -d"

    if filter_list:
        find_files_command += " -f \"%s\"" % ", ".join(filter_list)

    find_files_command += " %s" % args.directory
    if args.debug:
        print(find_files_command)

    stdout, stderr, _ = Process().run(find_files_command) # , cwd=os.getcwd())
    if stderr:
        print(stderr, file=sys.stderr)
    return stdout

def main():
    """Entry point."""

    args = parse_arguments()

    directory = args.directory
    if not os.path.isdir(directory):
        print("Pass subdirectory to find python files.", file=sys.stderr)
        return 0

    if args.debug:
        print("directory: %s" % directory)

    python_files = get_files(args)
    if args.debug:
        print(python_files)

    command = "pylint --output-format=colorized --score=no --jobs=0 --verbose %s" % python_files

    stdout, stderr, _ = Process().run(command)
    if args.only:
        for line in stdout.split("\n"):
            if any([warning in line for warning in args.only]):
                print(line)
    else:
        print(stdout)

    if stderr:
        print(stderr, file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
    # stdout, stderr, exitcode = Procs.run(["git", "powerlab", "grep", "" ])
