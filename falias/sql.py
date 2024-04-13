"""Global sql wrapper for universal using depend on driver."""

from importlib import import_module

# list of Falias suported sql drivers
drivers = ("sqlite", "mysql")


class Sql:
    """ SQL backend wrapper for drivers """
    def __init__(self, dsn="", **kwargs):
        driver = kwargs.get("driver")
        if driver is None:
            driver = dsn[:dsn.find(":")]
        if driver not in drivers:
            raise RuntimeError(f"Uknow Data Source Name `{driver}`")

        self.driver = driver
        self.m = import_module(f"falias.{driver}")

        self.connection = None
        self.m.__init__(self, dsn, **kwargs)

    def connect(self):
        return self.m.connect(self)

    def close(self):
        return self.m.close(self)

    def transaction(self, logger=None, cursor=None):
        kwargs = {}
        if logger:
            kwargs["logger"] = logger
        if cursor:
            kwargs["ctx_cursor"] = cursor
        return self.m.transaction(self, **kwargs)

    def __copy__(self):
        return self.m.__copy__(self)

    def copy(self):
        return self.__copy__()

    def __str__(self):
        return self.m.__str__(self)

    def __del__(self):
        self.close()
