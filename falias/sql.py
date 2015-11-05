"""Global sql wrapper for universal using depend on driver."""

from types import MethodType
from importlib import import_module

# list of Falias suported sql drivers
drivers = ("sqlite", "mysql")


class Sql:
    """ SQL backend wrapper for drivers """
    def __init__(self, dsn):
        driver = dsn[:dsn.find(':')]
        if driver not in drivers:
            raise RuntimeError("Uknow Data Source Name `%s`" % driver)
        print driver

        m = import_module('falias.%s' % driver)
        print m
        self.driver = driver

        m.sql_init(self, dsn)
        self.reconnect = MethodType(m.sql_reconnect, self)
        self.disconnect = MethodType(m.sql_disconnect, self)
        self.transaction = MethodType(m.sql_transaction, self)

        self.__str__ = MethodType(m.__str__, self)
