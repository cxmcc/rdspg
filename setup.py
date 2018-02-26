#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'boto3>=1.4.5',
    'click>=6.7',
    'Jinja2>=2.9.6'
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Topic :: System :: Clustering',
]

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='rdspg',
    version='20170909',
    description='Toolkit to extract and simplify information of existing RDS parameter groups.',
    long_description=long_description,
    author='Xiuming Chen',
    author_email='cc@cxm.cc',
    url='https://github.com/cxmcc/rdspg',
    packages=['rdspg'],
    package_data={'rdspg': ['terraform.jinja']},
    entry_points={'console_scripts': ['rdspg = rdspg.__main__:main']},
    install_requires=install_requires,
    keywords=['AWS', 'RDS'],
    classifiers=classifiers,
)
