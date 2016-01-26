"""Run test by:
    $~ py.test tests/test_parser.py
"""

from sys import path as python_path
from os import path

python_path.insert(0, path.abspath(
                   path.join(path.dirname(__file__), path.pardir)))

from falias.parser import Options


class Test_Parser:
    pass


class Test_Options:
    def test_options(self):
        opt = Options({'test_one': 1, 'test_two': 2})
        assert opt.options('test') == ['one', 'two']
