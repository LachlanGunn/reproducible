#!/usr/bin/env python3

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='reproducible',
    version='0.0.1',
    description='Aid to reproducible computation.',
    author='Lachlan Gunn',
    author_email='lachlan@twopif.net',
    license='none',
    classifiers=[
        'Development Status :: 1 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
    ],
    keywords='science reproducibility',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'numpy',
    ],
    python_requires='>=3')
