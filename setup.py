#!/usr/bin/env python
"""
    File            : setup.py
    Package         :
    Description     :
    Project Name    : BaseModule
    Created by Sabariram on 28-Dec-2018
    Copyright (c) KNAB Finance Advisors Pvt. Ltd. All rights reserved.
"""

__author__ = "sabariram"
__version__ = "1.0"

from setuptools import setup, find_packages

setup(name='Flask-RequestPreProcessor',
      version='1.0.0',
      python_requires='>=3.6',
      description='Preprocessor for flask requests',
      url='https://github.com/sabariramc/flask_requestpreprocesser',
      author='Sabariram',
      author_email='c.sabariram@gmail.com',
      license='MIT Licence',
      packages=find_packages(),
      install_requires=[
          'Flask>=1.1.*'
      ],
      zip_safe=False)
