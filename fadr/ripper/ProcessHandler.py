"""
Function definition
  Wrapper for the python subprocess module
"""
from __future__ import annotations

import logging
import subprocess


def fadr_subprocess(cmd, in_shell):
    """
    Handle creating new subprocesses and catch any errors
    """
    fadr_process = ""
    try:
        fadr_process = subprocess.check_output(
            cmd,
            shell=in_shell
        )
    except subprocess.CalledProcessError as error:
        logging.error(f"Error executing command {cmd}")
        logging.error(f"Subprocess error {error}")
        fadr_process = None

    return fadr_process
