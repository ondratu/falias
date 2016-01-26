"""Run test by:
    $~ py.test tests/test_smtp.py
"""

from sys import path as python_path
from os import path

python_path.insert(0, path.abspath(
                   path.join(path.dirname(__file__), path.pardir)))

from falias.smtp import Smtp


def test_smtp():
    Smtp('smtp://localhost/mcbig@localhost')
    Smtp('smtp://10.0.0.19/mcbig@zeropage.cz')
