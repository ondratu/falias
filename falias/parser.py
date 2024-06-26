"""
ConfigParser wrapper for type conversation
"""
from configparser import ConfigParser, NoOptionError, NoSectionError


def smart_get(value, cls=str, delimiter=","):
    """ Smart convert function, which convert value to cls. """

    if issubclass(cls, str):
        return value
    if issubclass(cls, bool):
        if value.lower() in ("true", "yes", "1", "on", "enable"):
            return True
        elif value.lower() in ("false", "no", "0", "off", "disable"):
            return False
        else:
            raise ValueError("%s is not boolean value" % value)
    if cls in (list, tuple):
        if value:
            return cls((s.strip() for s in value.split(delimiter)))
        return cls()
    else:
        return cls(value)


class Parser(ConfigParser):
    """ Wrapper to ConfigParser class, with better get method. """

    def get(self, section, option, default=None, cls=str, delimiter=","):
        """
        Method do the same as original get, but it can work with default value
        and use smart_get convert function to converting values to classes.
        """

        default = None if default is None else str(default)

        try:
            value = ConfigParser.get(self, section, option).strip()
        except NoSectionError:
            if default is None:
                raise
            value = default
        except NoOptionError:
            if default is None:
                raise
            value = default
        return smart_get(value, cls, delimiter)


class Options:
    """
    Compatible like class to ConfigParser, for read values from dictionary
    (options) with syntax section_option.
    """

    def __init__(self, options):
        self.o = options

    def get(self, sec, key, default=None, cls=str, delimiter=","):
        default = None if default is None else str(default)

        key = "%s_%s" % (sec, key)
        if default is None and key not in self.o:
            raise RuntimeError("Envirnonment variable `%s` is not set" % key)
        value = self.o.get(key, default).strip()
        return smart_get(value, cls, delimiter)

    def options(self, section):
        """Returns options in section like in ConfigParser."""
        sec_len = len(section) + 1
        return [key[sec_len:] for key, value in self.o.items()
                    if key.startswith("%s_" % section)]
