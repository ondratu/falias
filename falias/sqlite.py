"""Wrapper around sqlite3 connection.

Example of use:

>>> from logging import error
>>> from falias.sql import Sql
>>> db = Sql('sqlite:memory:')
>>> tr = db.transaction(logger=error)
>>> c = tr.cursor()
>>> c.execute("SELECT DATE('2015-12-24') WHERE 1 == %d", 1)
ERROR:root:SQL: SELECT DATE() AS NOW WHERE 1 == 1
>>> print(c.fetchone()[0])
2015-12-24
>>> del(tr)
ERROR:root:SQL: calling rollback()
"""

import re
import sqlite3

from falias.util import islistable, isnumber


def regexp(pattern, string):
    """regexp function for use in sql queries."""
    return (re.search(pattern, (string if string is not None else "")))


class Cursor(sqlite3.Cursor):
    """Extended cursor with tosql function, for better query arguments and
    logging."""
    def __init__(self, connection):
        sqlite3.Cursor.__init__(self, connection)
        self.transaction = None
        self.logger = None

    def __del__(self):
        """Automatics closing cursor on destructor."""
        sqlite3.Cursor.close(self)

    def tosql(self, arg, charset):
        """Convert arguments to right sql strings."""
        if arg is None:                                     # null
            arg = "NULL"
        elif isnumber(arg):                                 # float, int
            pass                                            # num
        elif isinstance(arg, str):                          # str
            # arg = arg.encode(charset)
            arg = arg.replace("'", "''")
            arg = f"'{arg}'"
        elif isinstance(arg, bool):                         # bool
            arg = 1 if arg else 0
        elif islistable(arg):                               # list, tuple, set
            arg = "(" + ",".join(self.tosql(a, charset) for a in arg) + ")"
        else:                                               #
            msg = "Unsupported type"
            raise TypeError(msg)
        return arg

    def execute(self, query, args=(), charset="utf-8"):
        """Execute query.

        Arguments are convert to right SQL types, so sql could not be
        injected with them. Unicode strings are automatically converts
        to string encoded with charset which could be UTF-8, UTF-16BE
        or UTF-16LE.

        When logger was set, query was log with them.
        """
        assert isinstance(query, str)
        # query = query.encode(charset)

        if isinstance(args, (list, tuple)):
            _args = []
            for arg in args:
                _args.append(self.tosql(arg, charset))
            args = tuple(_args)
        else:
            args = self.tosql(args, charset)

        try:
            sql = query % args if args else query
        except Exception:
            if self.logger is not None:
                self.logger("SQL \33[0;31mquery: %s\33[0m" % query)
                self.logger("SQL args: %s" % str(args))
            raise

        if self.logger is not None:
            self.logger("SQL: \33[0;32m%s\33[0m" % sql)
        return sqlite3.Cursor.execute(self, sql)

    def executescript(self, sql_script):
        if self.logger is not None:
            self.logger("SQL: \33[0;32mcalling sql script\33[0m")
        return sqlite3.Cursor.executescript(self, sql_script)


class DictCursor(Cursor):
    """Implementation of Dictionary cursor for sqlite."""
    def fetchone(self):
        """Fetches a single row from the cursor.

        None indicates that no more rows are available."""
        row = super().fetchone()
        return sqlite3.Row(self, row) if row else row

    def fetchall(self):
        """Fetchs all available rows from the cursor."""
        rows = super().fetchall()
        return [sqlite3.Row(self, row) for row in rows]

    def fetchmany(self, size=-1):
        """Fetch up to size rows from the cursor.

        Result set may be smaller than size. If size is not defined,
        cursor.arraysize is used."""
        size = size if size > -1 else self.arraysize
        rows = super().fetchmany(size)
        return [sqlite3.Row(self, row) for row in rows]


class Transaction():
    """Transaction connection class with automatic rollback in destructor."""

    def __init__(self, connection, logger=None, ctx_cursor=Cursor):
        """logger is log handler with one text parametr."""
        self.connection = connection
        self.done = False
        self.logger = logger
        self.ctx_cursor = ctx_cursor

    def __enter__(self):
        return self.cursor(self.ctx_cursor)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def cursor(self, cursorclass=Cursor):
        """Create and return cursor.

        Cursor could be Cursor (default) or DictCursor."""
        c = cursorclass(self.connection)
        c.logger = self.logger
        c.transaction = self
        return c

    def commit(self):
        """Commit transaction and log it when logger was set."""
        self.done = True
        if self.logger is not None:
            self.logger("SQL: \33[3;34mcalling commit()\33[0m")
        return self.connection.commit()

    def rollback(self):
        """Rollback transaction and log it when logger was set."""
        self.done = True
        if self.logger is not None:
            self.logger("SQL: \33[3;33mcalling rollback()\33[0m")
        return self.connection.rollback()

    def __del__(self):
        """If transaction was not done, call rollback."""
        if not self.done:
            self.rollback()


# Data Source Name regular expression for sqlite connection
re_dsn = re.compile(r"""\w+:       # driver
                        ((?P<memory>memory)|/(?P<dbfile>[\w\.\/]+))
                        (::)?(?P<charset>[\w\-]+)?
                    """, re.X)


def __init__(self, dsn, **kwargs):
    """__init__ method for Sql object."""
    if kwargs:
        self.dbfile = kwargs.get("dbfile")
        self.memory = kwargs.get("memory")
        self.charset = kwargs.get("charset", "utf-8")

    else:
        match = re_dsn.match(dsn)
        if not match:
            msg = "Bad SQLite Data Source Name `%s`"
            raise RuntimeError(msg, dsn)
        self.dbfile = match.group("dbfile")
        self.memory = match.group("memory")
        self.charset = match.group("charset") or "utf-8"


def connect(self):
    """Reconect method for Sql object."""
    if self.connection is not None:
        return self.connection

    if self.dbfile:
        try:
            self.connection = sqlite3.connect(self.dbfile)
        except sqlite3.OperationalError as e:
            e.args = (*e.args, self.dbfile)
            raise
    else:
        self.connection = sqlite3.connect(":memory:")

    # PRAGMA encoding = "UTF-8"; # UTF-8 | UTF-16 | UTF-16le | UTF-16be
    self.connection.execute("PRAGMA foreign_keys = ON")  # eneble foreign keys
    return None
# enddef


def close(self):
    """Close connection."""
    if self.connection is not None:
        self.connection.close()


def transaction(self, **kwargs):
    """Create and return Transaction object as method in Sql object."""
    self.connect()
    return Transaction(self.connection, **kwargs)


def __copy__(self):
    """Return copy of object for new thread or new proccess."""
    return self.__class__("", driver=self.driver, dbfile=self.dbfile,
                          memory=self.memory)


def __str__(self):
    """Return Data Source Name string from Sql object."""
    return "sqlite:/%s::%s" % (self.dbfile or "memory", self.charset)
