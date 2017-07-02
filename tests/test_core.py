# -*- coding: utf-8 -*-
from saltmill import Mill


def test_login():
    mill = Mill()
    mill.login()


def test_auto_login():
    mill = Mill()
    MSG = 'This is a test.'
    ret = mill.local('*', 'test.echo', MSG)
    assert len(ret['return'][0]) > 0
    for salt_id, msg in ret['return'][0].iteritems():
        assert msg == MSG


def test_renew_auth_token():
    mill = Mill()
    mill.login()

    mill.auth['token'] = 'invalid'
    MSG = 'This is a test.'
    ret = mill.local('*', 'test.echo', MSG)
    assert len(ret['return'][0]) > 0


def test_local_poll():
    mill = Mill()
    mill.login()
    MSG = 'This is a test.'
    ret = mill.local_poll('*', 'test.echo', MSG)
    assert len(ret['return'][0]) > 0