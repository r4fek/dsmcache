# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import dsmcache as meta

setup(name="dsmcache",
      version='.'.join(map(str, meta.__version__)),
      description="Simple, pure python memcached client",
      keywords="python memcache memcached client",
      author=meta.__author__,
      author_email=meta.__contact__,
      url=meta.__homepage__,
      download_url="http://github.com/r4fek/dsmcache/tarball/master",
      py_modules=["dsmcache"],
      packages=find_packages(exclude=['tests']),
      install_requires=['six'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'mock'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Python Software Foundation License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4"
          ])
