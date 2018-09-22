"""Defines the setup for the declxml library"""
from io import open
import os.path
from setuptools import setup


dir_path = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(dir_path, 'README.md')
with open(readme_path, encoding='utf-8') as readme:
    long_description = readme.read()


setup(
    name='declxml',
    description='Declarative XML processing library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.1.2-rc1',
    url='http://declxml.readthedocs.io/',
    project_urls={
        'Documentation': 'http://declxml.readthedocs.io/',
        'Source': 'https://github.com/gatkin/declxml',
        'Tracker': 'https://github.com/gatkin/declxml/issues',
    },
    author='Greg Atkin',
    author_email='greg.scott.atkin@gmail.com',
    license='MIT',
    py_modules=['declxml'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='XML, Parsing, Serialization'
)
