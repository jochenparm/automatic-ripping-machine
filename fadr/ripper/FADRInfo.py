"""
Class definition
 FADR system information and version numbers
"""
from __future__ import annotations

import getpass  # noqa E402
import logging  # noqa: E402
import os
import re
import sqlite3
import sys

from alembic.config import Config
from alembic.script import ScriptDirectory

from fadr.ripper import ProcessHandler


class FADRInfo:
    fadr_version = 0
    python_version = 0
    git_branch = ""
    git_commit = ""
    user = ""
    userenv = ""
    install_path = ""
    db_version = ""
    head_version = ""

    def __init__(self, install_path, db_file):
        self.install_path = install_path
        self.db_file = db_file
        self.get_git_commit()
        self.get_fadr_version()
        self.get_python_version()
        self.get_user_details()
        self.get_db_head_version()
        self.get_db_version()

    def get_values(self):
        logging.info(f"FADR version: {self.fadr_version}")
        logging.info(f"Python version: {self.python_version}")
        logging.info(f"User is: {self.user}")
        logging.info(f"Alembic head is: {self.head_version}")
        logging.info(f"Database version is: {self.db_version}")

    def get_git_commit(self):
        """
        Function to get the current fadr git version
        """
        branch_len = 10
        cmd = "cd /opt/fadr && git branch && git log -1"
        git_output = ProcessHandler.fadr_subprocess(cmd, True)
        git_regex = r"\*\s(\S+)\n(?:\s*\S*\n){1,10}(?:commit )([a-z\d]{5,7})"
        git_match = re.search(git_regex, str(git_output.decode("utf-8")))

        if git_match:
            (self.git_branch, self.git_commit) = git_match.groups()
            if len(self.git_branch) > branch_len:
                self.git_branch = self.git_branch[0:branch_len] + "..."
        else:
            self.git_branch = "unknown"
            self.git_commit = "unknown"

    def get_fadr_version(self):
        try:
            version_file = open(os.path.join(self.install_path, 'VERSION'))

            try:
                self.fadr_version = version_file.read().strip()

            except OSError as e:
                logging.info(f"FADR Version error: {e}")
                self.fadr_version = "unknown"

        except FileNotFoundError:
            self.fadr_version = "unknown"

    def get_python_version(self):
        version = sys.version
        if version:
            self.python_version = version
        else:
            self.python_version = "unknown"

    def get_user_details(self):
        """
        Get the user FADR is running
        getuser reports the process/efective user
        """
        user = getpass.getuser()
        if user:
            self.user = user
        else:
            self.user = "unknown"

    def get_db_head_version(self):
        """
        Get the FADR database version from Alembic
        """
        try:
            mig_dir = os.path.join(self.install_path, "fadr/migrations")
            config = Config()
            config.set_main_option("script_location", mig_dir)
            script = ScriptDirectory.from_config(config)
            self.head_version = script.get_current_head()
        except Exception as e:
            logging.info(f"DB Head error: {e}")
            self.head_version = "unknown"

    def get_db_version(self):
        """
        Get the FADR database version from the database file
        """
        if os.path.isfile(self.db_file):
            conn = sqlite3.connect(self.db_file)
            db_c = conn.cursor()
            db_c.execute("SELECT version_num FROM alembic_version")
            self.db_version = db_c.fetchone()[0]
        else:
            self.db_version = "unknown"
