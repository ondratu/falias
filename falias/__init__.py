""" Falias is library of some code wrappers.

This package contains these modules:

falias.sql
    Global sql wrapper for universal using depend on driver.

falias.mysql
    Wrapper around MySQL-python connection.s

falias.sqlite
    Wrapper around sqlite3 connection.

falias.security
    Security library is based on smartsalt function which salt text depend
    on input text.

falias.util
    Support library for auto convert or check types.

falias.smtp
    Contains some end-user classes for mailing.

falias.parser
    ConfigParser wrapper for type conversation
"""

__all__ = ['mysql', 'sqlite', 'sql', 'security', 'util', 'smtp', 'parser']

__date__ = "25 Mar 2016"
__version__ = "0.2.1.dev0"
