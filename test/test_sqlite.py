# -*- coding: utf-8 -*-
"""Run test by:
    $~ py.test tests/test_sqlite.py
"""

from sys import path as python_path
from os import path

python_path.insert(0, path.abspath(
                   path.join(path.dirname(__file__), path.pardir)))

from falias.sql import Sql
from logging import error


class TestSqlite():
    def test_select(self):
        db = Sql('sqlite:memory:')
        tr = db.transaction(logger=error)
        c = tr.cursor()
        c.execute("SELECT DATE('2015-12-24') WHERE 1 == %d", 1)
        assert c.fetchone()[0] == '2015-12-24'

    def test_insert(self):
        db = Sql('sqlite:memory:')
        tr = db.transaction(logger=error)
        c = tr.cursor()
        c.execute('CREATE TABLE test (value text)')
        c.execute("INSERT INTO test (value) VALUES (%s)", 'cc')
        c.execute("INSERT INTO test (value) VALUES (%s)", 'čč')
        c.execute("INSERT INTO test (value) VALUES (%s)", u'čč')
        c.execute(u"INSERT INTO test (value) VALUES (%s)", 'čč')
        c.execute(u"INSERT INTO test (value) VALUES (%s)", u'čč')
