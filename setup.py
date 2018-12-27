#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import os.path

dir_path = os.path.dirname(os.path.realpath(__file__))

from setuptools import setup, find_packages

with open(os.path.join(dir_path, 'README.rst')) as readme_file:
    readme = readme_file.read()

with open(os.path.join(dir_path, 'HISTORY.rst')) as history_file:
    history = history_file.read()

requirements = [ ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Daniel Jay Haskin",
    author_email='djhaskin987@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Helps workloads find safe harbor.",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='pylighthouse',
    name='pylighthouse',
    packages=find_packages(include=['pylighthouse']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/djhaskin987/pylighthouse',
    version='0.1.0',
    zip_safe=False,
)
