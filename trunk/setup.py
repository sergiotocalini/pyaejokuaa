#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from glob import glob
import os

dir_extra = ['themes/*/*', 'doc/*']
data_project = [(os.path.dirname(i), [i]) for x in dir_extra for i in glob(x)]

setup(name = 'pyAeJokuaa',
      version = '9999',
      description = 'pyAeJokuaa is a pluggable application to securely store passwords.',
      author = 'Sergio Tocalini Joerg',
      author_email = 'sergiotocalini@gmail.com',
      url = 'http://code.google.com/p/pyaejokuaa/',
      license = 'GNU GPLv3',
      scripts = ['pyAeJokuaa'],
      install_requires = ['paramiko', 'Elixir', 'DateTime',
                          'zope.interface', 'pytz', 'configobj'],
      packages = find_packages(),
      data_files = data_project,
      include_package_data = True,
      exclude_package_data = { '': ['README.txt'] },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: X11 Applications',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: System :: Systems Administration',
          ],      
)
