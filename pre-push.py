#!/usr/bin/env python3
# pylint: disable=invalid-name
# vim: ts=4 sw=4 tw=100 et ai si

"""
Git hook that is called before pushing. Runs Pylint on files that it recognizes as Python files,
and aborts pushing if there are errors or warnings.
"""

import sys
from process import Process

SUCCESS = 0
ABORT = 1

def get_files():
    """Return a list of python files that differs from the remote."""

    # Figure out the remote name.
    branch_name, _, _ = Process().run("git rev-parse --abbrev-ref HEAD")
    remote = "origin/" + branch_name

    # Get all the files that differ from 'remote'.
    stdout, _, _ = Process().run("git diff %s --name-only" % remote, verify=True)
    if not stdout:
        return []

    # Check which files are python files.
    python_files = []
    for file in (line for line in stdout.split("\n") if line):
        if file.endswith(".py"):
            python_files.append(file)
        else:
            try:
                with open(file) as edited_file:
                    # Check the shebang from the first line.
                    if "python" in edited_file.readline():
                        python_files.append(file)
            except FileNotFoundError:
                print("'%s' cannot be opened." % file, file=sys.stderr)
    return python_files

def lint_files(files):
    """Run pylint on files."""

    commands = ("pylint --output-format=colorized --score=no --jobs=0 %s" %
                file for file in files)
    processes = Process.run_many_async(commands)
    Process.join_many(processes, timeout=15)

    return processes

def main():
    """Main entry point."""

    files = get_files()
    processes = lint_files(files)

    for process in processes:
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr, file=sys.stderr)

    if any([process.exitcode == 0 for process in processes]):
        return SUCCESS

    print("To bypass 'pre-push' git hook, run 'git push' with '--no-verify'.", file=sys.stderr)
    return ABORT

if __name__ == "__main__":
    sys.exit(main())
