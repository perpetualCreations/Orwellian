"""
Main backend application.

Handles database requests, parsing submitted images, and logging events.

Project Orwellian,
By Delta Legacy
"""

import sqlite3
import threading
from time import time
from hashlib import sha3_512
from os import remove
from typing import Union
from datetime import date, datetime
from base64 import decodebytes as decodeBase64
import qrcode
import cv2
from pyzbar import pyzbar


class Application:
    """Main application class."""

    def __init__(self, file: str, debug: bool):
        """Initialize Manager class."""
        self.file = file
        self.debug = debug
        self.database_lock = threading.Lock()
        self.database_updated_event = threading.Event()
        connection, cursor = self.create_connection()
        try:
            cursor.execute("SELECT * FROM users")
        except sqlite3.OperationalError:
            cursor.execute("CREATE TABLE users (nid INTEGER NOT NULL"
                           " PRIMARY KEY AUTOINCREMENT, name TEXT)")
            connection.commit()
        try:
            cursor.execute("SELECT * FROM log")
        except sqlite3.OperationalError:
            cursor.execute("CREATE TABLE log (nid INTEGER NOT NULL"
                           " PRIMARY KEY AUTOINCREMENT, user TEXT NOT"
                           " NULL, wasLogin BOOL NOT NULL, time "
                           "TEXT NOT NULL, date TEXT NOT NULL)")
            connection.commit()
        self.database_lock.release()

    def create_connection(self, read_only: bool = False) -> \
            Union[tuple, sqlite3.Cursor]:
        """
        Return SQL connection.

        :param read_only: if True, skip lock acquisition and return cursor only
        :type read_only: bool
        :return: tuple containing connection and cursor respectively, or only
            cursor if read_only is True
        :rtype: Union[tuple, sqlite3.Cursor]
        """
        connection = sqlite3.connect(self.file)
        cursor = connection.cursor()
        if read_only is True:
            return cursor
        self.database_lock.acquire(True)
        return (connection, cursor)

    def add_user(self, name: str) -> None:
        """
        Add user to user database table.

        :param name: human-readable name of user to be identified by
        :type name: str
        """
        connection, cursor = self.create_connection()
        qrc = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qrc.add_data(name)
        qrc.make(fit=True)
        image = qrc.make_image()
        image.save(
            "./qr/" + sha3_512(name.encode("ascii", "replace")).hexdigest() +
            ".png")
        cursor.execute("INSERT INTO users (name) VALUES (:name)",
                       {"name": name})
        connection.commit()
        self.database_lock.release()
        self.database_updated_event.set()

    def remove_user(self, name: str) -> None:
        """
        Remove user from user database table.

        :param name: human-readable name of user to be identified by
        :type name: str
        """
        connection, cursor = self.create_connection()
        remove("./qr/" + sha3_512(name.encode("ascii", "replace"))
               .hexdigest() + ".png")
        cursor.execute("DELETE FROM users WHERE name=:name",
                       {"name": name})
        connection.commit()
        self.database_lock.release()
        self.database_updated_event.set()

    def log_user(self, name: str, is_login: bool) -> None:
        """
        Create entry in log database table.

        :param name: human-readable name of user to be identified by
        :type name: str
        :param is_login: if True, record log entry as a login event
        :type is_login: bool
        """
        if name is None:
            return None
        connection, cursor = self.create_connection()
        cursor.execute("INSERT INTO log (user, wasLogin, time, date) VALUES "
                       "(:user, :was_login, :time, :date)",
                       {"user": name, "was_login": is_login,
                        "time": str(datetime.now().strftime("%H:%M:%S")),
                        "date": str(date.today())})
        connection.commit()
        self.database_lock.release()
        self.database_updated_event.set()

    def get_all_logs(self) -> Union[None, list]:
        """Collect all log entries."""
        cursor = self.create_connection(True)
        return list(cursor.execute("SELECT * FROM log").fetchall())

    def get_all_users(self) -> list:
        """Collect all user entries."""
        cursor = self.create_connection(True)
        return list(cursor.execute("SELECT * FROM users").fetchall())

    def get_all_logs_with_user(self, name: str) -> list:
        """
        Collect all log entries where the user matches given name.

        :param name: human-readable name of user to be identified by
        :type name: str
        :return: list of all log entries with given name
        :rtype: list
        """
        cursor = self.create_connection(True)
        return list(cursor.execute("SELECT * FROM log WHERE user=:user",
                                   {"user": name}).fetchall())

    def was_last_signin_login(self, name: str) -> bool:
        """
        With self.get_all_logs_with_user, check if given name's last signin \
            event was a login.

        :param name: human-readable name of user to be identified by
        :type name: str
        :return: if True, last signin was login
        :rtype: bool
        """
        if name is None:
            return True
        try:
            entries = self.get_all_logs_with_user(name)
            return not bool(entries[len(entries) - 1][2])
        except IndexError:
            return True

    def scan(self, image: str) -> Union[None, str]:
        """Convert given base64 string into image, scan image for any \
            recognizable QR code."""
        image = image.replace("data:image/jpeg;base64,", "")
        cache_filename = "./imagecache/" + str(time()) + ".jpeg"
        with open(cache_filename, "wb") as file_handle:
            file_handle.write(decodeBase64(image.encode("ascii")))
        data = pyzbar.decode(cv2.imread(cache_filename))
        if self.debug is not True:
            remove(cache_filename)
        for qrc in data:
            if qrc.type == "QRCODE":
                return qrc.data.decode("utf-8")
