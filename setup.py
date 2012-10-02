#!/usr/bin/env python

from distutils.core import setup
from catkin_pkg.package import parse_package_for_distutils

d = parse_package_for_distutils()
d['packages'] = ['rosdoc_lite']
d['package_dir'] = {'rosdoc_lite':'src/rosdoc_lite'}
d['scripts'] = ['scripts/rosdoc_lite']
d['package_data'] = {'rosdoc_lite': ['templates/*']}

setup(**d)
