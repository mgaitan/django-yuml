# -*- coding: utf-8 -*-
"""
Include utf-8 encoding for the README since we do not know the
contents of the file.

"""
from setuptools import setup, find_packages
 
VERSION = open('VERSION').read() 
LONG_DESCRIPTION = open('README.rst').read()
 
setup(
    name = 'django-yuml',
    version = VERSION,
    url = 'https://github.com/olopoly/django-yuml',
    description='A manage.py command to create UML images for your models',
    long_description = LONG_DESCRIPTION,
    classifiers=[
        "Framework :: Django",
        "License :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='uml,yuml,django',
    author='Nikolajus Krauklis, Andrea de Marco, Joshua Williams',
    author_email='williams.joshua.j@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
)

