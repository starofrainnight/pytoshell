#!/usr/bin/env python

from pydgutils_bootstrap import use_pydgutils
use_pydgutils()

import pydgutils
import sys
from setuptools import setup, find_packages

package_name = "pytoshell"

source_dir = pydgutils.process()

packages = find_packages(where=source_dir)

long_description=(
     open("README.rst", "r").read()
     + "\n" +
     open("CHANGES.rst", "r").read()
     )

install_requires = ["jsonpickle", "simplejson"]

setup(
    name=package_name,
    version="0.0.1",
    author="Hong-She Liang",
    author_email="starofrainnight@gmail.com",
    url="https://github.com/starofrainnight/%s" % package_name,
    description="Wrote in python, compile to shell scripts (unix sh, windows batch)",
    long_description=long_description,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=install_requires,
    package_dir = {"": source_dir},
    packages=packages,
    entry_points = {
        'console_scripts': ['pytoshell=pytoshell.console:main'],
    },
    zip_safe=False, # Unpack the egg downloaded_file during installation.
    )
