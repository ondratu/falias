
import MySQLdb.cursors as cursors
from MySQLdb.connections import Connection

import re

from util import islistable, isnumber


class BaseCursor(cursors.BaseCursor):
    """
    BaseCursor extendet with tosql method, which covert types
    automatics to sql.

    logger - logging function of sql queries
    """

    def __init__(self, connection):
        cursors.BaseCursor.__init__(self, connection)
        self.logger = None

    def tosql(self, arg, charset):
        """ Automatics convert arguments to sql types """
        if arg is None:                                     # null
            arg = "NULL"
        elif isnumber(arg):                                 # float, int, long
            pass
        elif isinstance(arg, str) or isinstance(arg, unicode):  # str
            if isinstance(arg, unicode):
                arg = arg.encode(charset)
            arg = "'%s'" % self.connection.escape_string(arg)
        elif isinstance(arg, bool):                         # bool
            arg = 1 if arg else 0
        elif islistable(arg):                               # list, tuple, set
            arg = '(' + ','.join(self.tosql(a, charset) for a in arg) + ')'
        else:                                               #
            raise TypeError('Unsuported type')
        return arg

    def execute(self, query, args=()):
        """
        Execute method use tosql method fo conversation and self.logger
        to log query if logger was set.
        """
        # funcking conversion to db charset
        db = self._get_db()
        charset = db.character_set_name()

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
        return cursors.BaseCursor.execute(self, sql)

    def unlockTables(self):
        self.execute('UNLOCK TABLES')


class Cursor(BaseCursor, cursors.Cursor):
    """ Default cursor """
    def __init__(self, connection):
        cursors.Cursor.__init__(self, connection)


class DictCursor(BaseCursor, cursors.DictCursor):
    """ Dictionary cursor """
    def __init__(self, connection):
        cursors.DictCursor.__init__(self, connection)


class Transaction():
    """  Transaction connection class  """

    def __init__(self, connection, logger=None):
        """ logger is log handler with one text parametr """
        self.conn = connection
        self.conn.ping(True)
        self.commited = False
        self.logger = logger

    def cursor(self, cursorclass=Cursor):
        c = self.conn.cursor(cursorclass)
        c.logger = self.logger
        return c

    def commit(self):
        self.commited = True
        if self.logger is not None:
            self.logger('SQL: \33[3;34mcalling commit()\33[0m')
        return self.conn.commit()

    def rollback(self):
        self.commited = False
        if self.logger is not None:
            self.logger('SQL: \33[3;33mcalling rollback()\33[0m')
        return self.conn.rollback()

    def __del__(self):
        if not self.commited:
            self.rollback()


re_dsn = re.compile(r"""\w+://            # driver
                              (?P<user>\w+)
                              (:(?P<passwd>\w+))?
                              (@(?P<host>[\w\.]+))?
                              (:(?P<port>[0-9]+))?
                              /(?P<db>\w+)
                              (::(?P<charset>\w+))?
                           """, re.X)


def sql_init(self, dsn):
    match = re_dsn.match(dsn)
    if not match:
        raise RuntimeError("Bad MySQL Data Source Name `%s`", dsn)

    self.kwargs = {
        'host':     match.group('host') or "localhost",
        'port':     int(match.group('port') or 3306),
        'db':       match.group('db'),
        'charset':  match.group('charset') or "utf8",
        'user':     match.group('user')
    }

    passwd = match.group('passwd')
    if passwd:
        self.kwargs['passwd'] = passwd
    self.connection = None


def sql_reconnect(self):
    if self.connection is None:
        self.connection = Connection(**self.kwargs)


def sql_disconnect(self):
    pass


def sql_transaction(self, logger=None):
    self.reconnect()
    return Transaction(self.connection, logger)


def __str__(self):
    return "mysql://%s:%s@%s:%d/%s::%s" % \
        (self.kwargs['user'], self.kwargs.get('passwd', ''),
         self.kwargs['host'], self.kwargs['port'], self.kwargs['db'],
         self.kwargs['charset'])
