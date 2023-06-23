#!/usr/bin/env python

from setuptools import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rosdoc_lite'],
    package_dir={'': 'src'},
    scripts=['scripts/rosdoc_lite'],
    package_data={'rosdoc_lite': ['templates/*']}
)

setup(**d)
