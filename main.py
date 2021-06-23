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
from datetime import date
import qrcode
import cv2


class Application:
    """Main application class."""

    def __init__(self, file: str):
        """Initialize Manager class."""
        self.connection = sqlite3.connect(file)
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute("SELECT * FROM users")
        except sqlite3.OperationalError:
            self.cursor.execute("CREATE TABLE users (nid INTEGER NOT NULL"
                                " PRIMARY KEY AUTOINCREMENT, name TEXT)")
            self.connection.commit()
        try:
            self.cursor.execute("SELECT * FROM log")
        except sqlite3.OperationalError:
            self.cursor.execute("CREATE TABLE log (nid INTEGER NOT NULL"
                                " PRIMARY KEY AUTOINCREMENT, user TEXT NOT"
                                " NULL, wasLogin BOOL NOT NULL", "unix "
                                "INTEGER NOT NULL, date TEXT NOT NULL)")
            self.connection.commit()
        self.database_updated_event = threading.Event()
        self.database_updated_event.set()

    def add_user(self, name: str) -> None:
        """
        Add user to user database table.

        :param name: human-readable name of user to be identified by
        :type name: str
        """
        qrcode.make(name, fit=True).save(
            "./qr/" + sha3_512(name.encode("ascii", "replace")).hexdigest() +
            ".png")
        self.cursor.execute("INSERT INTO users (name) VALUES (:name)",
                            {"name": name})
        self.connection.commit()
        self.database_updated_event.set()

    def remove_user(self, name: str) -> None:
        """
        Remove user from user database table.

        :param name: human-readable name of user to be identified by
        :type name: str
        """
        remove("./qr/" + sha3_512(name.encode("ascii", "replace"))
               .hexdigest() + ".png")
        self.cursor.execute("DELETE FROM users WHERE name=:name",
                            {"name": name})
        self.connection.commit()
        self.database_updated_event.set()

    def log_user(self, name: str, is_login: bool) -> None:
        """
        Create entry in log database table.

        :param name: human-readable name of user to be identified by
        :type name: str
        :param is_login: if True, record log entry as a login event
        :type is_login: bool
        """
        self.cursor.execute("INSERT INTO log (user, wasLogin, unix) VALUES "
                            "(:user, :was_login, :unix, :date)",
                            {"user": name, "was_login": is_login,
                             "unix": time(), "date": str(date.today())})
        self.connection.commit()
        self.database_updated_event.set()

    def get_all_logs(self) -> Union[None, list]:
        """Collect all log entries."""
        # remove NID with POP, apply with list comp
        return [x.pop(0) for x in self.cursor.execute("SELECT * FROM log"
                                                      ).fetchall()]

    def get_all_users(self) -> list:
        """Collect all user entries."""
        # remove NID with POP, apply with list comp
        return [x.pop(0) for x in self.cursor.execute("SELECT * FROM users"
                                                      ).fetchall()]

    def get_all_logs_with_user(self, name: str) -> list:
        """
        Collect all log entries where the user matches given name.

        :param name: human-readable name of user to be identified by
        :type name: str
        :return: list of all log entries with given name
        :rtype: list
        """
        return self.cursor.execute("SELECT * FROM log WHERE user=:user",
                                   {"user": name})

    @staticmethod
    def scan(image) -> Union[None, str]:
        """Scan image for any recognizable QR code."""
        data = cv2.QRCodeDetector().decodeAndDecode(image)
        if data[1] is not None:
            return data[0]
