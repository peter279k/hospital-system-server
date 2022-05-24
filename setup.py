# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='hospital-system-server',
      version='0.1',
      description='The hospital system server',
      url='https://gitlab.com/iii-api-platform/hospital-system-server',
      author='peter279k',
      author_email='peter279k@gmail.com',
      packages=['FHIRClient', 'TWCAClient'],
      license='MIT',
      python_requires=">=3.7",
      zip_safe=False)

