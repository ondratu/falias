import pytest

from sys import path
path.insert(0, '../')

from falias.smtp import *

def test_smtp():
    Smtp('smtp://localhost/mcbig@localhost')
    Smtp('smtp://10.0.0.19/mcbig@zeropage.cz')
