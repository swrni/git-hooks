#!/usr/bin/env python3
# pyylint: max-line-length=100
# pylint: disable=invalid-name
# vim: ts=4 sw=4 tw=100 et ai si

"""
Git hook that is called before pushing. Runs Pylint on files that it recognizes as Python files,
and aborts pushing if there are errors or warnings.
"""

import sys
import time
import subprocess

SUCCESS = 0
ABORT = 1

class Error(Exception):
    """Exception for 'Process' class."""

    def __init__(self, *args):
        """Init method."""

        Exception.__init__(*args)

class Process():
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

        if isinstance(command, str):
            import shlex
            command = shlex.split(command)

        self.command = command
        self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, shell=False,
                                        universal_newlines=True)

    def join(self, timeout=5):
        """Wait for the 'self.process' to join. After 'timeout' seconds, kill the process."""

        try:
            self.stdout, self.stderr = self.process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as err:
            print(err, file=sys.stderr)
            self.process.kill()
            self.stdout, self.stderr = self.process.communicate()

        self.stdout = self.stdout.rstrip("\n\r")
        self.stderr = self.stderr.rstrip("\n\r")
        self.exitcode = self.process.returncode

    def run(self, command, timeout=5, verify=False):
        """
        Run 'command' and return a tuple of (stdout, stderr, exitcode).
        If 'verify' is 'True', verify the exitcode of the process.
        """

        self.run_async(command)
        self.join(timeout=timeout)

        if verify and self.exitcode != 0:
            raise Error("Process returned with non-zero exitcode.")

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
            process.join(timeout=max(stop_time - time.time(), 0))
