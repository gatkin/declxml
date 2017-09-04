"""Defines the setup for the declxml library"""
from setuptools import setup

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='declxml',
    description='Declarative XML processing library',
    long_description=long_description,
    version='0.9.0',
    url='https://github.com/gatkin/declxml',
    author='Greg Atkin',
    author_email='greg.scott.atkin@gmail.com',
    license='MIT',
    py_modules=['declxml'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    keywords='XML, Parsing, Serialization'
)
