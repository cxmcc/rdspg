#!/usr/bin/env python

from setuptools import setup

install_requires = [
    'boto3>=1.4.5',
    'click>=6.7',
    'tabulate>=0.7.7',
    'Jinja2>=2.9.6'
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Topic :: System :: Clustering',
]

with open('README.rst', 'r') as f:
    long_description = f.read()

description = ('Command-line toolkit to help understand information '
               'about your AWS RDS Parameter Groups.')

setup(
    name='rdspg',
    version='0.1.6',
    description=description,
    long_description=long_description,
    author='Xiuming Chen',
    author_email='cc@cxm.cc',
    url='https://github.com/cxmcc/rdspg',
    packages=['rdspg'],
    package_data={'rdspg': ['terraform.jinja']},
    entry_points={'console_scripts': ['rdspg = rdspg.__main__:main']},
    install_requires=install_requires,
    keywords=['AWS', 'RDS', 'Parameter Groups', 'Relational Database Service'],
    classifiers=classifiers,
)
