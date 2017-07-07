===============================
Salt Mill
===============================

.. image:: https://img.shields.io/pypi/v/salt-mill.svg
        :target: https://pypi.python.org/pypi/salt-mill

Saltstack API Client for Humans

.. image:: https://glasslion.github.io/salt-mill/assets/Salt%2C_sugar_and_pepper_shakers.jpg
        :target: https://commons.wikimedia.org/wiki/File:Salt,_sugar_and_pepper_shakers.jpg

* Free software: BSD license

Features
--------

* auto login
* auto renew auth-token
* asynchronous polling

Usage
---------------

.. code-block:: python

    from saltmill import Mill

    # By default, mill try to get the authentication configs from
    # func kwarsg, environment variables, and ~/.pepperrc, same as pepper
    mill = Mill()
    mill.local('*', 'test.ping')

    # Create a job with local_async and poll the result with lookup_jid
    # Works well on long running tasks and unstable network conditions
    mill.local_pool('*', 'test.ping')
