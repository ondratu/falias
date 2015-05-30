from types import MethodType

_drivers = ("sqlite", "mysql")

def sql_from_dsn(dsn):
    driver = dsn[:dsn.find(':')]
    if driver not in _drivers:
        raise RuntimeError("Uknow Data Source Name `%s`" % driver)
    return _drivers[driver](dsn)
#enddef

class Sql:
    def __init__(self, dsn):
        driver = dsn[:dsn.find(':')]
        if driver not in _drivers:
            raise RuntimeError("Uknow Data Source Name `%s`" % driver)

        m = __import__(driver)
        self.driver = driver

        m.sql_init(self, dsn)
        self.reconnect = MethodType (m.sql_reconnect, self)
        self.disconnect = MethodType (m.sql_disconnect, self)
        self.transaction = MethodType (m.sql_transaction, self)

        self.__str__ = MethodType(m.__str__, self)
