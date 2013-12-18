#!/usr/bin/env python3

from distutils.core import setup

readme = open("README.md", "r")

setup(name='pyknc',
      version='0.1',
      author='Maksym Borodin',
      author_email='maksym_b@orsoc.se',
      url='https://github.com/mborodin/pyknc',
      license='GPLv2+',
      packages=['knc'],
      long_description=readme.read())