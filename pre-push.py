#!/usr/bin/env python3
# pyylint: max-line-length=100
# pylint: disable=invalid-name

"""
Git hook that is called before pushing. Runs Pylint on files that it recognizes as Python files,
and aborts pushing if there are errors or warnings.
"""

import sys
import time
import argparse
import subprocess

SUCCESS = 0
ABORT = 1

class Process(object):
    """Process object."""

    def __init__(self):
        """Init method."""

        self.command = None
        self.process = None

        self.stdout = None
        self.stderr = None
        self.exitcode = None

    def run_async(self, command):
        """Run 'command' asynchronously."""

        self.command = command
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=False,
                                        universal_newlines=True)

    def join(self, timeout=5):
        """Wait for the 'self.process' to join. After 'timeout' seconds, kill the process."""

        try:
            self.stdout, self.stderr = self.process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.stdout, self.stderr = self.process.communicate()
        self.exitcode = self.process.returncode

    def run(self, command, timeout=5, verify=False):
        """
        Run 'command' and return a tuple of (stdout, stderr, exitcode).
        If 'verify' is 'True', verify the exitcode of the process.
        """

        self.run_async(command)
        self.join(timeout=timeout)

        if verify and self.exitcode != 0:
            print(self.stderr, file=sys.stderr)
            sys.exit(1)

        return self.stdout, self.stderr, self.exitcode

    @staticmethod
    def run_many_async(commands):
        """Run a collection of commands asynchronously."""

        processes = []
        for command in commands:
            process = Process()
            process.run_async(command)
            processes.append(process)
        return processes

    @staticmethod
    def join_many(processes, timeout):
        """Wait for processes to join for the total of 'timeout' seconds."""

        stop_time = time.time() + timeout
        for process in processes:
            timeout = stop_time - time.time()
            print("timeout: %s" % timeout)
            process.join(timeout=timeout)

def get_files():
    """Return a list of python files that differs from the remote."""

    # Figure out the remote name.
    branch_name, _, _ = Process().run("git rev-parse --abbrev-ref HEAD")
    print(branch_name)
    remote = "origin/" + branch_name

    # Get all the files that differ from 'remote'.
    stdout, _, _ = Process().run("git diff %s --name-only" % remote, verify=True)
    files = [line for line in stdout.split("\n") if line]

    # Check which files are python files.
    python_files = []
    for file in files:
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

    commands = ("pylint --output-format=colorized %s" % file for file in files)
    processes = Process.run_many_async(commands)
    Process.join_many(processes, timeout=5)

    return any([process.exitcode != 0 for process in processes])

def parse_arguments():
    """Parse arguments."""

    description = "kvak"
    parser = argparse.ArgumentParser(description=description)
    # parser.add_argument("-h", "--help")
    parser.add_argument(dest="remote-name", action="store") #, required=True)
    parser.add_argument(dest="remote-location", action="store") #, required=True)
    parser.add_argument(dest="refs-to-update", nargs=argparse.REMAINDER) #, required=True)

    return parser.parse_args(sys.argv[1:])

print("shit", file=sys.stderr)

def main():
    """Main entry point."""

    print("kvak")
    print("parse: %s" % str(parse_arguments()))
    files = get_files()
    success = lint_files(files)
    if success:
        return SUCCESS
    # print("To bypass 'pre-push' git hook, run 'git push' with '--no-verify'.", file=sys.stderr)
    print("To bypass 'pre-push' git hook, run 'git push' with '--no-verify'.")
    return ABORT

if __name__ == "__main__":
    sys.exit(main())

print("loaded")