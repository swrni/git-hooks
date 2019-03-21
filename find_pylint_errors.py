#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 tw=100 et ai si

"""Tool that runs pylint on python files in a chosen directory."""

import os
import sys
import json
import argparse

from process import Process

OWN_NAME = "find_pylint_errors"

class Error(Exception):
    """Custom exception for this module."""

    def __init__(self, *args, **kwargs):
        """Init method."""

        Exception.__init__(self, *args, **kwargs)

def parse_arguments():
    """Parse arguments to get the subdirectory."""

    def parse_path(path):
        """Validate that 'path' exists and turn it into absolute path."""

        path = path.strip("\"")
        if not os.path.isdir(path):
            raise Error("Path does not exist: '%s'" % path)
        return path

    def parse_list(items):
        """Make 'items' string into list of comma separated items."""

        return {item.strip() for item in items.split(",")}

    text = sys.modules[__name__].__doc__
    parser = argparse.ArgumentParser(description=text, prog=OWN_NAME)
    parser.add_argument("-d", "--debug", help="Use debug logging.", action="store_true")
    parser.add_argument("--warnings", help="Show only these pylint warnings.", type=parse_list,
                        default=[])
    parser.add_argument("--skip-warnings", help="Filter these pylint warnings.", type=parse_list,
                        default=[])
    parser.add_argument("--color-output", help="Color the output.", action="store_true")
    parser.add_argument("directory", help="Directory to look files from.", type=parse_path)
    return parser.parse_args(sys.argv[1:])

def get_files(args):
    """Call 'find_python_files.py' and return python files as a list of lines."""

    filter_list = [".git", "__pycache__", "__init__.py"]

    find_files_command = "python ./find_python_files.py --absolute-paths"
    if args.debug:
        find_files_command += " -d"

    if filter_list:
        find_files_command += f" --filter=\"{', '.join(filter_list)}\""

    find_files_command += f' "{args.directory}"'

    if args.debug:
        print(find_files_command)

    stdout, stderr, _ = Process().run(find_files_command)
    if stderr and args.debug:
        print(stderr, file=sys.stderr)
    return stdout.split("\n")

def main():
    """Entry point."""

    args = parse_arguments()
    if args.color_output and os.name == "nt":
        raise Error("'args.color_output' is not supported on Windows")

    items_in_line = lambda items, line: any([item in line for item in items])

    python_files = get_files(args)
    if args.debug:
        skip_line_flags = ("[skipping]", "[unrecognized]", "Namespace(")
        python_files = list(line for line in python_files
                            if not items_in_line(skip_line_flags, line))

    cmd = "pylint --output-format=json --score=no "
    for python_file in python_files:
        cmd += f' "{python_file}"'

    stdout, _, _ = Process().run(cmd, timeout=100)

    data = {}
    for item in json.loads(stdout):
        name = item["path"]
        if name not in data:
            data[name] = []
        data[name].append(item)

    def color_string(string, color):
        """Return 'string' colored."""

        color_end_flag = "\x1b[0m"
        if args.color_output:
            return "%s%s%s" % (color, string, color_end_flag)
        return str(string)

    for name, items in data.items():
        print(color_string(name, u"\x1b[100;5;1m"))
        for item in items:
            line = color_string(item["line"], u"\u001b[35;1m")
            message = color_string(item["message"], u"\u001b[38;5;247m")
            print(f"  Line {line}: {message}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
