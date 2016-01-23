# -*- coding: utf-8 -*-
import os
from functools import wraps
import time
import ConfigParser

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


class Mill(object):
    def __init__(self, debug_http=False, *args, **kwargs):
        self.configure(**kwargs)
        self._pepper = pepper.Pepper(self.login_details['SALTAPI_URL'],
                                     debug_http=debug_http)

    def configure(self, **kwargs):
        '''
        Get salt-api login configurations.
        Source & order:
        kwargs > environment variables > ~/.pepperrc
        '''
        # default settings
        details = {
            'SALTAPI_URL': 'https://localhost:8000/',
            'SALTAPI_USER': 'saltdev',
            'SALTAPI_PASS': 'saltdev',
            'SALTAPI_EAUTH': 'auto',
        }

        # read from ~/.pepperrc
        config = ConfigParser.RawConfigParser()
        config.read(os.path.expanduser('~/.pepperrc'))
        profile = 'main'
        if config.has_section(profile):
            for key, value in config.items(profile):
                key = key.upper()
                details[key] = config.get(profile, key)

        # get environment values
        for key, value in details.items():
            details[key] = os.environ.get(key, details[key])

        # get Mill().__init__ parameters
        for key, value in details.items():
            details[key] = kwargs.get(key.lower().lstrip('saltapi_'),
                                      details[key])
        # pass is a Python keyword, use password instead
        details['SALTAPI_PASS'] = kwargs.get('password', details['SALTAPI_PASS'])  # noqa

        self.login_details = details

    def login(self):
        '''
        simple wrapper for Pepper.login()
        '''
        self.auth = self._pepper.login(
            self.login_details['SALTAPI_USER'],
            self.login_details['SALTAPI_PASS'],
            self.login_details['SALTAPI_EAUTH'],
        )

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


default_mill = Mill()
