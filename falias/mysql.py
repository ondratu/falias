"""Wrapper around MySQL-python connection.

Example of use:

>>> from logging import error
>>> from falias.sql import Sql
>>> db = Sql('mysql://localhost/test')
>>> tr = db.transaction(logger=error)
>>> c = tr.cursor()
>>> c.execute("SELECT %d LIMIT 1", 1)
ERROR:root:SQL: SELECT 1 WHERE 1 = 1 LIMIT 1
>>> print(c.fetchone()[0])
1
>>> del(tr)
ERROR:root:SQL: calling rollback()
"""

import re

from pymysql import cursors
from pymysql.connections import Connection

from .util import islistable, isnumber


class BaseCursor(cursors.Cursor):
    """
    BaseCursor extendet with tosql method, which covert types
    automatics to sql.

    logger - logging function of sql queries
    """

    def __init__(self, connection):
        super().__init__(connection)
        self.logger = None

    def tosql(self, arg, charset):
        """ Automatics convert arguments to sql types """
        if arg is None:                                     # null
            arg = "NULL"
        elif isnumber(arg):                                 # float, int, long
            pass
        elif isinstance(arg, str):  # str
            arg = "'%s'" % self.connection.escape_string(arg)
        elif isinstance(arg, bool):                         # bool
            arg = 1 if arg else 0
        elif islistable(arg):                               # list, tuple, set
            arg = "(" + ",".join(self.tosql(a, charset) for a in arg) + ")"
        else:                                               #
            msg = "Unsuported type"
            raise TypeError(msg)
        return arg

    def execute(self, query, args=()):
        """
        Execute method use tosql method fo conversation and self.logger
        to log query if logger was set.
        """
        # funcking conversion to db charset
        db = self._get_db()
        charset = db.character_set_name()

        if isinstance(args, (list, tuple)):
            _args = []
            for arg in args:
                _args.append(self.tosql(arg, charset))
            args = tuple(_args)
        else:
            args = self.tosql(args, charset)

        sql = query % args
        if self.logger is not None:
            self.logger("SQL: \33[0;32m%s\33[0m" % sql)
        return super().execute(sql)

    def unlock_tables(self):
        """Call unlock tables."""
        self.execute("UNLOCK TABLES")


class Cursor(BaseCursor, cursors.Cursor):
    """ Default cursor """
    def __init__(self, connection):
        cursors.Cursor.__init__(self, connection)


class DictCursor(BaseCursor, cursors.DictCursor):
    """ Dictionary cursor """
    def __init__(self, connection):
        cursors.DictCursor.__init__(self, connection)


class Transaction():
    """Transaction connection class with automatic rollback in destructor."""

    def __init__(self, connection, logger=None, ctx_cursor=Cursor):
        """ logger is log handler with one text parametr """
        self.conn = connection
        self.conn.ping(True)
        self.commited = False
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
        c = self.conn.cursor(cursorclass)
        c.logger = self.logger
        c.transaction = self
        return c

    def commit(self):
        """Commit transaction and log it when logger was set."""
        self.commited = True
        if self.logger is not None:
            self.logger("SQL: \33[3;34mcalling commit()\33[0m")
        return self.conn.commit()

    def rollback(self):
        """Rollback transaction and log it when logger was set."""
        self.commited = False
        if self.logger is not None:
            self.logger("SQL: \33[3;33mcalling rollback()\33[0m")
        return self.conn.rollback()

    def __del__(self):
        """If transaction was not committed, call rollback."""
        if not self.commited:
            self.rollback()


# Data Source Name regular expression for mysql connection
re_dsn = re.compile(r"""\w+://            # driver
                              (?P<user>\w+)
                              (:(?P<passwd>\w+))?
                              (@(?P<host>[\w\.]+))?
                              (:(?P<port>[0-9]+))?
                              /(?P<db>\w+)
                              (::(?P<charset>\w+))?
                           """, re.X)


def __init__(self, dsn):
    """__init__ method for Sql object."""
    match = re_dsn.match(dsn)
    if not match:
        msg = "Bad MySQL Data Source Name `%s`"
        raise RuntimeError(msg, dsn)

    self.kwargs = {
        "host":     match.group("host") or "localhost",
        "port":     int(match.group("port") or 3306),
        "db":       match.group("db"),
        "charset":  match.group("charset") or "utf8",
        "user":     match.group("user"),
    }

    passwd = match.group("passwd")
    if passwd:
        self.kwargs["passwd"] = passwd
    self.connection = None


def connect(self):
    """Reconect method for Sql object."""
    if self.connection is not None:
        return self.connection

    self.connection = Connection(**self.kwargs)
    return None


def close(self):
    """Close connection."""
    self.connection.close()


def transaction(self, **kwargs):
    """Create and return Transaction object as method in Sql object."""
    self.connect()
    return Transaction(self.connection, **kwargs)


def __str__(self):
    return "mysql://%s:%s@%s:%d/%s::%s" % \
        (self.kwargs["user"], self.kwargs.get("passwd", ""),
         self.kwargs["host"], self.kwargs["port"], self.kwargs["db"],
         self.kwargs["charset"])
