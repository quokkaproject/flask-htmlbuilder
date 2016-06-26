#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='quokka-flask-htmlbuilder',
    version='0.13',
    url='http://github.com/quokkaproject/flask-htmlbuilder',
    license='MIT',
    author='QuokkaProject',
    author_email='rochacbruno@gmail.com',
    description='Fork of Flexible Python-only HTML generation for Flask',
    long_description=__doc__,
    packages=['flask_htmlbuilder'],
    namespace_packages=['flask_htmlbuilder'],
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    tests_require=[
        'nose'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
