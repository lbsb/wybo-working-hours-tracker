# -*- coding: utf-8 -*-

class User(object):
    _id = None
    _first_name = None
    _last_name = None
    _email = None
    _uuid = None

    def __init__(self, id = "", first_name = "", last_name = "", email = "", uuid = ""):
        self._id = id
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._uuid = uuid
