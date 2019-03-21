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
    parser.add_argument("-d", "--debug", help="Use debug logging.", action="store_true")
    parser.add_argument("--warnings", help="Show only these pylint warnings.", type=parse_list,
                        default=[])
    parser.add_argument("--skip-warnings", help="Filter these pylint warnings.", type=parse_list,
                        default=[])
    parser.add_argument("directory", help="Find files inside this directory.", default="",
                        nargs="?")
    return parser.parse_args(sys.argv[1:])

def get_files(args):
    """Call 'find_python_files.py' and return python files as a list of lines."""

    filter_list = [".git", "__pycache__", "__init__.py"]

    find_files_command = ["python", "./find_python_files.py"]
    if args.debug:
        find_files_command += ["-d"]

    if filter_list:
        find_files_command += ["-f", ", ".join(filter_list)]

    find_files_command += [args.directory]

    if args.debug:
        print(find_files_command)

    stdout, stderr, _ = Process().run(find_files_command) # , cwd=os.getcwd())
    if stderr and args.debug:
        print(stderr, file=sys.stderr)
    return stdout.split("\n")

def parse_pylint_output(stdout, coloring=False):
    """Parse pylint output and return dictionary of files and output lines: (filename, lines)."""

    lines = stdout.split("\n")
    module_name_identifier = "************* Module"

    for line in lines:
        print(line)
    sys.exit(2)

    # def parse_module_name(line):
    #     if coloring:
    #         # line = line.split(module_name_identifier)[1].strip()
    #         end_index = line.find("\x1b[0m")
    #         return line[:end_index]
    #     return line

    data = {}
    module_name = None
    for line in lines:
        # print(line)
        if module_name_identifier in line:
            print("line: '%s'" % line)
            line = line.split(module_name_identifier)[1].strip()
            end_index = line.find("\n") # end_index = line.find("\x1b[0m")
            module_name = line[:end_index]
            print("module_name: '%s'" % module_name)
            # # module_name = parse_module_name(line)
            # module_name = line
            data[module_name] = []
        elif module_name and line:
            data[module_name].append(line)
    return data

def main():
    """Entry point."""

    args = parse_arguments()

    directory = args.directory
    if not os.path.isdir(directory):
        print("Pass subdirectory to find python files.", file=sys.stderr)
        return 0

    if args.debug:
        print("directory: %s" % directory)

    items_in_line = lambda items, line: any([item in line for item in items])

    python_files = get_files(args) 
    # for f in python_files:
    #     print(f)
    # # print(python_files)
    # sys.exit(2)
    print("\nEnnen:\n")
    for f in python_files:
        print(f)
    print("\n")
    if args.debug:
        skip_line_flags = ("[skipping]", "[unrecognized]", "Namespace(")
        python_files = list(line for line in python_files
                            if not items_in_line(skip_line_flags, line))
    print("\nJalkeen:\n")
    for f in python_files:
        print(f)
    # sys.exit(2)

    # print(python_files[0:2])
    # sys.exit(0)
    commands = ("pylint --output-format=colorized --score=no %s" % python_file
                for python_file in python_files)
    command = "pylint --output-format=colorized --score=no %s" % " ".join(python_files[0:2])
    print(command)
    procs = Process.run_many_async(command)
    Process.join_many(procs, timeout=10)

    # stdout, stderr, _ = Process.run_many(command, timeout=10)
    # if stderr:
    #     print(stderr, file=sys.stderr)

    # print("\n\n\nstdout: '%s'" % stdout)
    # sys.exit(2)

    # data = parse_pylint_output(stdout)

    # if data:
    #     print("here2")
    #     for name, lines in data.items():
    #         if args.warnings:
    #             data[name] = [line for line in lines
    #                           if items_in_line(args.warnings, line)]
    #         if args.skip_warnings:
    #             data[name] = [line for line in lines
    #                           if not items_in_line(args.skip_warnings, line)]

    #     data = {name:lines for name, lines in data.items() if lines}

    #     for name, lines in data.items():
    #         # print("\x1b[100;5;1m %s \x1b[0m", name)
    #         print(name)
    #         for line in lines:
    #             print("  %s" % line)
    # print("here")

    # # stdout, stderr, _ = Process().run(command, timeout=10)
    # # if args.only:
    # #     for line in stdout.split("\n"):
    # #         if any([warning in line for warning in args.only]):
    # #             print(line)
    # # else:
    # #     print("stdout: '%s'" % stdout)

    # # if stderr:
    # #     print(stderr, file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
    # stdout, stderr, exitcode = Procs.run(["git", "powerlab", "grep", "" ])
