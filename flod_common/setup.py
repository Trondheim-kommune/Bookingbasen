#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='flod_common',
    version='0.1',
    description='Common code for FLOD',
    author='Martin Polden',
    author_email='martin.polden@gmail.com',
    packages=['flod_common'],
    install_requires=['itsdangerous>=0.24']
)
