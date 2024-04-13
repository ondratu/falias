# -*- coding: utf-8 -*-
"""Run test by:
    $~ py.test tests/test_sqlite.py
"""

from os import path
from sys import path as python_path

python_path.insert(0, path.abspath(
                   path.join(path.dirname(__file__), path.pardir)))

from logging import error

from falias.sql import Sql


class TestSqlite():
    def test_select(self):
        db = Sql("sqlite:memory:")
        tr = db.transaction(logger=error)
        c = tr.cursor()
        c.execute("SELECT DATE('2015-12-24') WHERE 1 == %d", 1)
        assert c.fetchone()[0] == "2015-12-24"

    def test_insert(self):
        db = Sql("sqlite:memory:")
        tr = db.transaction(logger=error)
        c = tr.cursor()
        c.execute("CREATE TABLE test (value text)")
        c.execute("INSERT INTO test (value) VALUES (%s)", "cc")
        c.execute("INSERT INTO test (value) VALUES (%s)", "čč")
        c.execute("INSERT INTO test (value) VALUES (%s)", u"čč")
        c.execute(u"INSERT INTO test (value) VALUES (%s)", "čč")
        c.execute(u"INSERT INTO test (value) VALUES (%s)", u"čč")
