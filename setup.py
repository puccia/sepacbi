#!/usr/bin/python

"""
Setup routines.
"""

__copyright__ = 'Copyright (c) 2014 Emanuele Pucciarelli, C.O.R.P. s.n.c.'
__license__ = '3-clause BSD'

from setuptools import setup, find_packages

setup(
    name="sepacbi",
    version="0.1.1",
    description="SEPA Credit Transfer request (CBI) XML generator",
    long_description="{0:s}\n\n".format(
        open("README.rst").read()
    ),
    author="Emanuele Pucciarelli",
    author_email="ep@corp.it",
    url="http://github.com/puccia/sepacbi/",
    download_url="http://github.com/puccia/sepacbi/",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial",
    ],
    license="3-clause BSD",
    keywords="xml finance banking payments",
    platforms="All",
    packages=find_packages("."),
    install_requires=['lxml'],
    zip_safe=True
)
