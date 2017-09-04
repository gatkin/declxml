"""Defines the setup for the declxml library"""
from setuptools import setup

setup(
    name='declxml',
    description='Declarative XML processing library',
    version='0.9.1',
    url='http://declxml.readthedocs.io/',
    author='Greg Atkin',
    author_email='greg.scott.atkin@gmail.com',
    license='MIT',
    py_modules=['declxml'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='XML, Parsing, Serialization'
)
