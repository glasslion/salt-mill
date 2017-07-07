#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'salt-pepper>=0.4.0'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='salt-mill',
    version='1.0.0',
    description="Saltstack API Client for Humans",
    long_description=readme + '\n\n' + history,
    author="Leo Zhou",
    author_email='glasslion@gmail.com',
    url='https://github.com/glasslion/salt-mill',
    packages=[
        'saltmill',
    ],
    package_dir={'saltmill':
                 'saltmill'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='salt-mill',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
