#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from aip import __version__

README = \
'''
ArduPy Integrated Platform
'''


requirements = [
    'pyusb',
    'demjson',
    'pyserial',
    'colorama',
    'ardupy-mpfshell',
    'pip >= 20.1'
]

setup_requirements = [
    # TODO: put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest'
]

setup(
    name='ardupy-aip',
    version=__version__,
    description="ArduPy Integrated Platform",
    long_description=README,
    author="Baozhu Zuo",
    author_email='zuobaozhu@gmail.com',
    url='https://github.com/seeed-studio/ardupy-aip',
    packages=find_packages(include=['aip']),
    scripts=['ardupy-aip'],
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'aip=aip.main:main'
        ],
    },
    license="MIT License",
    zip_safe=False,
    keywords='voice doa beamforming kws',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
