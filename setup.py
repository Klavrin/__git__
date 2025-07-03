#!/usr/bin/env python3

from setuptools import setup

setup(name='__git__',
    version='1.0',
    packages=['__git__'],
    entry_points = {
        'console_scripts': [
            '__git__ = __git__.cli:main'
        ]
    }
)

