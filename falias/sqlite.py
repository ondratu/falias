
import re
import sqlite3

from util import islistable, isnumber


def regexp(pattern, string):
    return (re.search(pattern, (string if string is not None else '')))


class Cursor(sqlite3.Cursor):
    def __init__(self, connection):
        sqlite3.Cursor.__init__(self, connection)
        self.logger = None

    def __del__(self):
        sqlite3.Cursor.close(self)

    def tosql(self, arg, charset):
        if arg is None:                                     # null
            arg = "NULL"
        elif isnumber(arg):                                 # float, int, long
            pass                                            # num
        elif isinstance(arg, str) or isinstance(arg, unicode):  # str & unicode
            if isinstance(arg, unicode):
                arg = arg.encode(charset)
            arg = arg.replace("'", "''")
            arg = "'%s'" % arg
        elif isinstance(arg, bool):                         # bool
            arg = 1 if arg else 0
        elif islistable(arg):                               # list, tuple, set
            arg = '(' + ','.join(self.tosql(a, charset) for a in arg) + ')'
        else:                                               #
            raise TypeError('Unsuported type')
        return arg

    def execute(self, query, args=(), charset = "utf-8"):
        """ charset could be UTF-8, UTF-16BE or UTF-16LE """

        if isinstance(args, tuple) or isinstance(args, list):
            _args = []
            for arg in args:
                _args.append(self.tosql(arg, charset))
            args = tuple(_args)
        else:
            args = self.tosql(args, charset)

        sql = query % args
        if self.logger is not None:
            self.logger("SQL: \33[0;32m%s\33[0m" % sql)
        return sqlite3.Cursor.execute(self, sql)


class DictCursor(Cursor):
    def __init__(self, connection):
        super(DictCursor, self).__init__(connection)

    def fetchone(self):
        row = super(DictCursor, self).fetchone()
        return sqlite3.Row(self, row) if row else row

    def fetchall(self):
        rows = super(DictCursor, self).fetchall()
        return list(sqlite3.Row(self, row) for row in rows)

    def fetchmany(self, size=-1):
        size = size if size > -1 else self.arraysize
        rows = super(DictCursor, self).fetchmany(size)
        return list(sqlite3.Row(self, row) for row in rows)


class Transaction():
    """  Transaction connection class  """

    def __init__(self, connection, logger=None):
        """ logger is log handler with one text parametr """
        self.connection = connection
        self.commited = False
        self.logger = logger

    def cursor(self, cursorclass=Cursor):
        c = cursorclass(self.connection)
        c.logger = self.logger
        c.transaction = self
        return c

    def commit(self):
        self.commited = True
        if self.logger is not None:
            self.logger("SQL: \33[3;34mcalling commit()\33[0m")
        return self.connection.commit()

    def rollback(self):
        self.commited = False
        if self.logger is not None:
            self.logger("SQL: \33[3;33mcalling rollback()\33[0m")
        return self.connection.rollback()

    def __del__(self):
        if not self.commited:
            self.rollback()


re_dsn = re.compile("""\w+:       # driver
                        ((?P<memory>memory)|/(?P<dbfile>[\w\.\/]+))
                        (::)?(?P<charset>[\w\-]+)?
                    """, re.X)


def sql_init(self, dsn):
    match = re_dsn.match(dsn)
    if not match:
        raise RuntimeError("Bad SQLite Data Source Name `%s`", dsn)
    self.dbfile = match.group('dbfile')
    self.memory = match.group('memory')
    self.charset = match.group('charset') or "utf-8"


def sql_reconnect(self):
    if self.dbfile:
        try:
            conn = sqlite3.connect(self.dbfile)
        except sqlite3.OperationalError as e:
            e.args = e.args + (self.dbfile,)
            raise e
    else:
        conn = sqlite3.connect(":memory:")

    # PRAGMA encoding = "UTF-8"; # UTF-8 | UTF-16 | UTF-16le | UTF-16be
    conn.execute("PRAGMA foreign_keys = ON")    # eneble foreign keys
    return conn


def sql_disconnect(self):
    pass


def sql_transaction(self, logger=None):
    return Transaction(self.reconnect(), logger)


def __str__(self):
    return "sqlite:/%s::%s" % (self.dbfile or 'memory', self.charset)
