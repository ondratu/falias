
import re, sqlite3

from util import islistable, isnumber

class Cursor(sqlite3.Cursor):
    def __init__(self, connection):
        sqlite3.Cursor.__init__(self, connection)
        self.logger = None
    #enddef

    def __del__(self):
        sqlite3.Cursor.close(self)
    #enddef

    def tosql(self, arg, charset):
        if arg is None:                                     # null
            arg = "NULL"
        elif isnumber(arg):                                 # float, int, long
            pass                                            # num
        elif isinstance(arg, str) or isinstance(arg, unicode):  # str & unicode
            if isinstance(arg, unicode):
                arg = arg.encode(charset)
            #arg = arg.replace("'", "\\'").replace('"', '\\"')
            arg = arg.replace("'", "''")
            arg = "'%s'" % arg
        elif isinstance(arg, bool):                         # bool
            arg = 1 if arg else 0
        elif islistable(arg):                               # list, tuple, set
            arg = '(' + ','.join( self.tosql(a, charset) for a in arg )  + ')'
        else:                                               #
            raise TypeError('Unsuported type')
        #endif
        return arg
    #enddef

    def execute(self, query, args = (), charset = "utf-8"):
        """ charset could be UTF-8, UTF-16BE or UTF-16LE """

        if isinstance(args, tuple) or isinstance(args, list):
            _args = []
            for arg in args:
                _args.append(self.tosql(arg, charset))
            args = tuple(_args)
        else:
            args = self.tosql(args, charset)
        #endif

        sql = query % args
        if not self.logger is None:
            self.logger("SQL: \33[0;32m%s\33[0m" % sql)
        return sqlite3.Cursor.execute(self, sql)
    #enddef
#endclass

class Transaction():
    """  Transaction connection class  """

    def __init__(self, connection, logger = None):
        """ logger is log handler with one text parametr """
        self.connection = connection
        self.commited = False
        self.logger = logger
    #enddef

    def cursor(self, cursorclass = Cursor):
        c = cursorclass(self.connection)
        c.logger = self.logger
        return c
    #enddef

    def commit(self):
        self.commited = True
        if not self.logger is None:
            self.logger("SQL: \33[3;34mcalling commit()\33[0m")
        return self.connection.commit()
    #enddef

    def rollback(self):
        self.commited = False
        if not self.logger is None:
            self.logger("SQL: \33[3;33mcalling rollback()\33[0m")
        return self.connection.rollback()
    #enddef

    def __del__(self):
        if not self.commited:
            self.rollback()
    #enddef

#endclass


re_dsn = re.compile("\w+:((?P<memory>memory)|/(?P<dbfile>[\w\.\/]+))(::)?(?P<charset>[\w\-]+)?")

def sql_init(self, dsn):
    match = re_dsn.match(dsn)
    if not match:
        raise RuntimeError("Bad SQLite Data Source Name `%s`", dsn)
    self.dbfile = match.group('dbfile')
    self.memory = match.group('memory')
    self.charset = match.group('charset') or "utf-8"
#enddef

def sql_reconnect(self):
    if self.dbfile:
        try:
            return sqlite3.connect(self.dbfile)
        except sqlite3.OperationalError as e:
            e.args = e.args + (self.dbfile,)
            raise e
    else:
        return sqlite3.connect(":memory:")
    # PRAGMA encoding = "UTF-8"; # UTF-8 | UTF-16 | UTF-16le | UTF-16be
#enddef

def sql_disconnect(self):
    pass

def sql_transaction(self, logger = None):
    return Transaction(self.reconnect(), logger)
