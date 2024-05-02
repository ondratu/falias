"""Run test by:
    $~ py.test tests/test_smtp.py
"""

from os import path
from sys import path as python_path

from pytest import fixture

python_path.insert(0, path.abspath(
                   path.join(path.dirname(__file__), path.pardir)))

from falias.smtp import Smtp

DSNS = (
    {"host": "localhost", "port": 125, "sender": "sender@localhost",
         "user": "user@localhost", "password": "password"},
    {"host": "10.0.0.19", "port": 100, "sender": "sender@example.net",
         "user": "user@example.net", "password": "seecret"},
    {"host": "example.net", "port": 25, "sender": "no-replay@example.net",
         "user": "mr.user@example.net", "password": "bž86@67Kl!"},
)


@fixture(params=DSNS)
def dsn_host(request):
    obj = request.param.copy()
    obj["dsn"] = "smtp://{host}/".format(**obj)
    return obj


@fixture(params=DSNS)
def dsn_tls(request):
    obj = request.param.copy()
    obj["dsn"] = "smtps://{host}/".format(**obj)
    return obj


@fixture(params=DSNS)
def dsn_port(request):
    obj = request.param.copy()
    if obj["port"] != 25:
        obj["dsn"] = "smtp://{host}:{port}/{sender}".format(**obj)
    else:
        obj["dsn"] = "smtp://{host}/{sender}".format(**obj)
    return obj


@fixture(params=DSNS)
def dsn_sender(request):
    obj = request.param.copy()
    obj["dsn"] = "smtp://{host}:{port}/{sender}".format(**obj)
    return obj


@fixture(params=DSNS)
def dsn_user(request):
    obj = request.param.copy()
    obj["dsn"] = "smtp://{user}@{host}:{port}/{sender}".format(**obj)
    return obj


@fixture(params=DSNS)
def dsn_password(request):
    obj = request.param.copy()
    obj["dsn"] = "smtp://{user}:{password}@{host}:{port}/{sender}".format(
            **obj)
    return obj


class TestParse:
    def test_url(self, dsn_host):
        smtp = Smtp(dsn_host["dsn"])
        assert smtp.host == dsn_host["host"]

    def test_tls(self, dsn_tls):
        smtp = Smtp(dsn_tls["dsn"])
        assert smtp.protocol == "smtps"
        assert smtp.host == dsn_tls["host"]

    def test_port(self, dsn_port):
        smtp = Smtp(dsn_port["dsn"])
        assert smtp.host == dsn_port["host"]
        assert smtp.port == dsn_port["port"]

    def test_sender(self, dsn_sender):
        smtp = Smtp(dsn_sender["dsn"])
        assert smtp.host == dsn_sender["host"]
        assert smtp.port == dsn_sender["port"]
        assert smtp.sender == dsn_sender["sender"]

    def test_user(self, dsn_user):
        smtp = Smtp(dsn_user["dsn"])
        assert smtp.host == dsn_user["host"]
        assert smtp.port == dsn_user["port"]
        assert smtp.sender == dsn_user["sender"]
        assert smtp.user == dsn_user["user"]

    def test_password(self, dsn_password):
        smtp = Smtp(dsn_password["dsn"])
        assert smtp.host == dsn_password["host"]
        assert smtp.port == dsn_password["port"]
        assert smtp.sender == dsn_password["sender"]
        assert smtp.user == dsn_password["user"]
        assert smtp.passwd == dsn_password["password"]
