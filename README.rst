===============================
Salt Mill
===============================

.. image:: https://img.shields.io/pypi/v/salt-mill.svg
        :target: https://pypi.python.org/pypi/salt-mill


Saltstack API Client for Humans

* Free software: BSD license

Features
--------

* auto login
* auto renew auth-token

Usage
---------------

.. code-block:: python

    from saltmill import Mill
    # By default, mill try to get the authentication configs from
    # func kwarsg, environment variables, and ~/.pepperrc, same as pepper
    mill = Mill()
    mill.local('*', 'test.ping')
