# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
from functools import wraps
import time
import ConfigParser

from retrying import retry

import pepper


def login_required(func):
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        if not getattr(self, 'auth', None):
            self.login()
        elif time.time() > self.auth['expire']:
            self.login()
        try:
            ret = func(self, *args, **kwargs)
        except pepper.PepperException as e:
            if str(e) == "Authentication denied":
                # when service salt-api restart, the old tokens are revoked,
                # the client does not konw that, and still use the old token.
                # So when we got 'Authentication denied', we re-login once,
                # and try again.
                self.login()
                ret = func(self, *args, **kwargs)
            else:
                raise
        return ret
    return func_wrapper

def retry_if_empty_result(result):
    return result == {}

class Mill(object):
    def __init__(self, debug_http=False, *args, **kwargs):
        self.configure(**kwargs)
        self._pepper = pepper.Pepper(self.confs['SALTAPI_URL'],
                                     debug_http=debug_http)

    def configure(self, **kwargs):
        '''
        Get salt-api login configurations.
        Source & order:
        kwargs > environment variables > ~/.pepperrc
        '''
        # default settings
        confs = {
            'SALTAPI_URL': 'https://localhost:8000/',
            'SALTAPI_USER': 'saltdev',
            'SALTAPI_PASS': 'saltdev',
            'SALTAPI_EAUTH': 'auto',
            'SALTAPI_DEFAULT_TIMEOUT': 60,
            'SALTAPI_WAIT_PER_POOL': 3,
        }

        # read from ~/.pepperrc
        file_config = ConfigParser.RawConfigParser()
        file_config.read(os.path.expanduser('~/.pepperrc'))
        profile = 'main'
        if file_config.has_section(profile):
            for key, value in file_config.items(profile):
                key = key.upper()
                confs[key] = file_config.get(profile, key)

        # get environment values
        for key, value in confs.items():
            confs[key] = os.environ.get(key, confs[key])

        # get Mill().__init__ parameters
        for key, value in confs.items():
            confs[key] = kwargs.get(
                key.lower().lstrip('saltapi_'), confs[key]
            )
        # pass is a Python keyword, use password instead
        confs['SALTAPI_PASS'] = kwargs.get('password', confs['SALTAPI_PASS'])  # noqa

        self.confs = confs

    def login(self):
        '''
        simple wrapper for Pepper.login()
        '''
        self.auth = self._pepper.login(
            self.confs['SALTAPI_USER'],
            self.confs['SALTAPI_PASS'],
            self.confs['SALTAPI_EAUTH'],
        )

    @retry(stop_max_attempt_number=3,
           retry_on_result=retry_if_empty_result)
    @login_required
    def lookup_jid(self, jid):
        return self._pepper.lookup_jid(jid)

    @login_required
    def local(self, *args, **kwargs):
        return self._pepper.local(*args, **kwargs)

    @login_required
    def local_async(self, *args, **kwargs):
        return self._pepper.local_async(*args, **kwargs)

    @login_required
    def runner(self, *args, **kwargs):
        return self._pepper.runner(*args, **kwargs)

    @login_required
    def local_poll(self, *args, **kwargs):
        # timeout is a valid argument for pepper.local()
        # we use the `poll_timeout` argument for the poll
        # timeout
        timeout = kwargs.pop(
            'poll_timeout',
            self.confs['SALTAPI_DEFAULT_TIMEOUT']
        )
        if 'expr_form' not in kwargs:
            kwargs['expr_form'] = 'compound'

        async_ret = self.local_async(*args, **kwargs)
        jid = async_ret['return'][0]['jid']
        nodes = async_ret['return'][0]['minions']

        # keep trying until all expected nodes return
        total_time = 0
        start_time = time.time()
        exit_code = 0
        while True:
            total_time = time.time() - start_time
            if total_time > timeout:
                exit_code = 1
                break

            jid_ret = self.lookup_jid(jid)
            ret_nodes = list(jid_ret['return'][0].keys())
            if set(ret_nodes) == set(nodes):
                break
            else:
                time.sleep(self.confs['SALTAPI_WAIT_PER_POOL'])

        # Set non response minions to  {}
        ret_nodes = jid_ret['return'][0]
        for node in nodes:
            if node not in ret_nodes:
                ret_nodes[node] = {}
        return jid_ret

default_mill = Mill()
