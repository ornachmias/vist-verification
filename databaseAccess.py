import logging
import os

import mysql.connector
from mysql.connector import Error

import configurations
import logHandler
from vistDataset import VistDataset


class DatabaseAccess(object):
    def __init__(self) -> None:
        self._logger = logging.getLogger(logHandler.general_logger)
        self._db_name = "VIST_Validation"
        self._mysql = None

    def initialize(self, vist_dataset: VistDataset):
        try:
            self._mysql = mysql.connector.connect(host=configurations.mysql_host,
                                                  user=configurations.mysql_user,
                                                  passwd=configurations.mysql_password)

            self._create_database()
            self._mysql = mysql.connector.connect(host=configurations.mysql_host,
                                                  user=configurations.mysql_user,
                                                  passwd=configurations.mysql_password,
                                                  database=self._db_name)

            vist_dataset.initialize()

            self._create_tables()

            return True
        except Error as e:
            self._logger.error("Failed to initialize database.")
            self._logger.exception(e)
            return False

    def _create_database(self):
        cursor = self._mysql.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(self._db_name))
        cursor.close()

    def _create_tables(self):
        cursor = self._mysql.cursor()
        base_path = "./mysql"
        for file in os.listdir("./mysql"):
            if file.startswith("table."):
                self._logger.info("Running {}".format(file))
                cursor.execute(self._read_file(os.path.join(base_path, file)))

    def _read_file(self, path):
        with open(path, 'r') as f:
            return f.read()








