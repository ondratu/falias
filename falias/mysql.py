#
# $Id: mysql.py 46 2012-05-23 04:12:58Z mcbig $
#

import MySQLdb.cursors as cursors
from MySQLdb.connections import Connection

import re

from util import islistable, isnumber

class BaseCursor(cursors.BaseCursor):
    def __init__(self, connection):
        cursors.BaseCursor.__init__(self, connection)
        self.logger = None
    #enddef

    def tosql(self, arg, charset):
        if arg is None:                                     # null
            arg = "NULL"
        elif isnumber(arg):                                 # float, int, long
            pass                                            # num 
        elif isinstance(arg, str) or isinstance(arg, unicode):  # str
            if isinstance(arg, unicode):
                arg = arg.encode(charset)
            arg = "'%s'" % self.connection.escape_string(arg)
        elif isinstance(arg, bool):                         # bool
            arg = 1 if arg else 0
        elif islistable(arg):                               # list, tuple, set
            arg = '(' + ','.join( self.tosql(a, charset) for a in arg )  + ')'
        else:                                               #
            raise TypeError('Unsuported type')
        #endif
        return arg
    #enddef

    def execute(self, query, args = ()):
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
        #endif
        
        sql = query % args
        if not self.logger is None:
            self.logger("SQL: \33[0;32m%s\33[0m" % sql)
        return cursors.BaseCursor.execute(self, sql)
    #enddef

    def unlockTables(self):
        self.execute('UNLOCK TABLES')
    #enddef
#endclass

class Cursor(BaseCursor, cursors.Cursor):
    def __init__(self, connection):
        cursors.Cursor.__init__(self, connection)
    #enddef
#endclass

class DictCursor(BaseCursor, cursors.DictCursor):
    def __init__(self, connection):
        cursors.DictCursor.__init__(self, connection)
    #enddef
#endclass

class Transaction():
    """  Transaction connection class  """

    def __init__(self, connection, logger = None):
        """ logger is log handler with one text parametr """
        self.conn = connection
        self.conn.ping(True)
        self.commited = False
        self.logger = logger
    #enddef

    def cursor(self, cursorclass = Cursor):
        c = self.conn.cursor(cursorclass)
        c.logger = self.logger
        return c
    #enddef

    def commit(self):
        self.commited = True
        if not self.logger is None:
            self.logger('SQL: \33[3;34mcalling commit()\33[0m')
        return self.conn.commit()
    #enddefu

    def rollback(self):
        self.commited = False
        if not self.logger is None:
            self.logger('SQL: \33[3;33mcalling rollback()\33[0m')
        return self.conn.rollback()
    #enddef

    def __del__(self):
        if not self.commited:
            self.rollback()
    #enddef

#endclass

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
        'host'    : match.group('host') or "localhost",
        'port'    : int(match.group('port') or 3306),
        'db'      : match.group('db'),
        'charset' : match.group('charset') or "utf8",
        'user'    : match.group('user')
    }
    
    passwd = match.group('passwd')
    if passwd:
        self.kwargs['passwd'] = passwd

    self.connection = None
#enddef

def sql_reconnect(self):
    if self.connection is None:
        print str(self.kwargs)
        self.connection  = Connection(**self.kwargs)

def sql_disconnect(self):
    pass

def sql_transaction(self, logger = None):
    self.reconnect()
    return Transaction(self.connection, logger)

def mysql_parse_DSN(dsn):
    """
    Parsing DSN - The Data Source Name
    example: mysql://user:passwd@host:port/database
    """

    match = re_mysql_DSN.match(dsn.strip())
    if match is None:
        raise RuntimeError(
                'DSN must be look like mysql://user:passwd@host:port/database::charset')

    user, passwd, host, port, db, charset = match.groups()
    retval = {}
    retval["host"] = host[1:] if not host is None else 'localhost'
    retval["port"] = int(port[1:]) if not port is None else 3306
    retval["db"] = db
    retval["charset"] = charset[2:] if not charset is None else 'utf8'
    retval["user"] = user
    if not passwd is None:
        retval["passwd"] = passwd[1:]

    return retval
#enddef
