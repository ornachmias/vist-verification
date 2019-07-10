import logging
import os

import mysql.connector
from mysql.connector import Error

import configurations
import logHandler
from vistDataset import VistDataset


class DatabaseAccess(object):
    def __init__(self, scripts_root) -> None:
        self._scripts_root = scripts_root
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
            self.add_albums(vist_dataset.data["train"]["albums"]
                            + vist_dataset.data["val"]["albums"]
                            + vist_dataset.data["test"]["albums"])

            self.add_annotations(vist_dataset.data["train"]["annotations"]
                                 + vist_dataset.data["val"]["annotations"]
                                 + vist_dataset.data["test"]["annotations"])

            self.add_images(vist_dataset.data["train"]["images"]
                            + vist_dataset.data["val"]["images"]
                            + vist_dataset.data["test"]["images"])

            return True
        except Error as e:
            self._logger.error("Failed to initialize database.")
            self._logger.exception(e)
            return False

    def add_albums(self, albums):
        if self._validate_content("Albums", albums):
            return

        cursor = self._mysql.cursor()
        try:
            self._logger.info("Starting to insert {} albums to database.".format(len(albums)))
            insert_albums_query = """ INSERT INTO Albums (Id, Description, Title, Photos, VistLabel) 
                           VALUES (%s,%s,%s,%s,%s) """
            albums_to_insert = [(x["id"], x["description"], x["title"], x["photos"], x["vist_label"]) for x in albums]
            cursor.executemany(insert_albums_query, albums_to_insert)
            self._mysql.commit()
            self._logger.info("{} Albums inserted successfully.".format(cursor.rowcount))
        except mysql.connector.Error as error:
            self._logger.error("Failed inserting albums. {}".format(error), error)
        finally:
            if self._mysql.is_connected():
                cursor.close()

    def add_annotations(self, annotations):
        if self._validate_content("Annotations", annotations):
            return

        cursor = self._mysql.cursor()
        try:
            self._logger.info("Starting to insert {} annotations to database.".format(len(annotations)))
            insert_annotations_query = """ INSERT INTO Annotations (StoryletId, PhotoOrder, 
                            PhotoFlickrId, AlbumId, StoryId, OriginalText, Text) 
                           VALUES (%s,%s,%s,%s,%s,%s,%s) """
            annotations_to_insert = [(x[0]["storylet_id"], x[0]["worker_arranged_photo_order"], x[0]["photo_flickr_id"], x[0]["album_id"], x[0]["story_id"], x[0]["original_text"], x[0]["text"]) for x in annotations]
            cursor.executemany(insert_annotations_query, annotations_to_insert)
            self._mysql.commit()
            self._logger.info("{} Annotations inserted successfully.".format(cursor.rowcount))
        except mysql.connector.Error as error:
            self._logger.error("Failed inserting annotations. {}".format(error), error)
        finally:
            if self._mysql.is_connected():
                cursor.close()

    def add_images(self, images):
        if self._validate_content("Images", images):
            return

        cursor = self._mysql.cursor()
        try:
            self._logger.info("Starting to insert {} images to database.".format(len(images)))
            insert_images_query = """ INSERT INTO Images (Id, Title, Text, AlbumId, Tags) 
                           VALUES (%s,%s,%s,%s,%s) """
            images_to_insert = [(x["id"], x["title"], x["text"], x["album_id"], x["tags"]) for x in images]
            cursor.executemany(insert_images_query, images_to_insert)
            self._mysql.commit()
            self._logger.info("{} Images inserted successfully.".format(cursor.rowcount))
        except mysql.connector.Error as error:
            self._logger.error("Failed inserting images. {}".format(error), error)
        finally:
            if self._mysql.is_connected():
                cursor.close()

    def _create_database(self):
        cursor = self._mysql.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(self._db_name))
        cursor.close()

    def _create_tables(self):
        cursor = self._mysql.cursor()
        for file in os.listdir(self._scripts_root):
            if file.startswith("table."):
                self._logger.info("Running {}".format(file))
                cursor.execute(self._read_file(os.path.join(self._scripts_root, file)))
        cursor.close()

    def _read_file(self, path):
        with open(path, 'r') as f:
            return f.read()

    def _validate_content(self, table_name, objects):
        current_rows_count = self._count_rows(table_name)
        current_objects_count = len(objects)
        if current_rows_count < current_objects_count:
            self._logger.warning("Current number of rows in database are {} "
                                 "while requested to add {} objects. Resetting table."
                                 .format(current_rows_count, current_objects_count))
            self._delete_table_content(table_name)
            return False

        self._logger.info("All rows exists in table '{}', validation succeeded.".format(table_name))
        return True

    def _count_rows(self, table_name):
        count_query = "SELECT COUNT(*) FROM {}".format(table_name)
        cursor = self._mysql.cursor(buffered=True)
        cursor.execute(count_query)
        number_of_rows = cursor.fetchone()

        if number_of_rows is None:
            number_of_rows = 0

        cursor.close()
        return number_of_rows[0]

    def _delete_table_content(self, table_name):
        count_query = "DELETE FROM {}".format(table_name)
        cursor = self._mysql.cursor()
        cursor.execute(count_query)
        cursor.close()









