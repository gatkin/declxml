# declxml - Declarative XML Processing
[![Build Status](https://travis-ci.org/gatkin/declxml.svg?branch=master)](https://travis-ci.org/gatkin/declxml)
[![codecov](https://codecov.io/gh/gatkin/declxml/branch/master/graph/badge.svg)](https://codecov.io/gh/gatkin/declxml)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/declxml/)

XML processing made easy. No more writing and maintaining dozens or hundreds of lines of imperitive serialization and parsing logic. With declxml, you declaratively define the structure of your XML docuement and let declxml handle the rest.

## Installation
```
pip install declxml
```

## Usage
Given some XML to process
```xml
<author>
    <name>Robert A. Heinlein</name>
    <birth-year>1907</birth-year>
    <book>
        <title>Starship Troopers</title>
        <published>1959</published>
    </book>
    <book>
        <title>Stranger in a Strange Land</title>
        <published>1961</published>
    </book>
</author>
```

Create a declxml processor that defines the structure of the document
```python
import declxml as xml

author_processor = xml.dictionary('author', [
    xml.string('name'),
    xml.integer('birth-year'),
    xml.array(xml.dictionary('book', [
        xml.string('title'),
        xml.integer('published')
    ]), alias='books')
])
```

Then use the processor to parse XML data
```python
import declxml as xml

author_xml = """
<author>
    <name>Robert A. Heinlein</name>
    <birth-year>1907</birth-year>
    <book>
        <title>Starship Troopers</title>
        <published>1959</published>
    </book>
    <book>
        <title>Stranger in a Strange Land</title>
        <published>1961</published>
    </book>
</author>
"""

xml.parse_from_string(author_processor, author_xml)

{
    'birth-year': 1907,
    'name': 'Robert A. Heinlein',
    'books': [
        {
            'title': 'Starship Troopers',
            'published': 1959
        },
        {
            'title': 'Stranger in a Strange Land',
            'published': 1961
        }
    ]
 }
```

The same processor can also be used to serialize data to XML
```python
import declxml as xml

author = {
    'birth-year': 1920,
    'name': 'Issac Asimov',
    'books': [
        {
            'title': 'I, Robot',
            'published': 1950
        },
        {
            'title': 'Foundation',
            'published': 1951
        }
    ]
 }

xml.serialize_to_string(author_processor, author)

"""
<author>
    <name>Issac Asimov</name>
    <birth-year>1920</birth-year>
    <book>
        <title>I, Robot</title>
        <published>1950</published>
    </book>
    <book>
        <title>Foundation</title>
        <published>1951</published>
    </book>
</author>
"""
```

Want to work with objects instead of dictionaries? You can do that with declxml too.
```python
import declxml as xml


class Author:

    def __init__(self):
        self.name = None
        self.birth_year = None
        self.books = []

    def __repr__(self):
        return 'Author(name={}, birth_year={}, books={})'.format(
            self.name, self.birth_year, self.books)


class Book:

    def __init__(self):
        self.title = None
        self.published = None

    def __repr__(self):
        return 'Book(title={}, published={})'.format(self.title, self.published)


author_processor = xml.user_object('author', Author, [
    xml.string('name'),
    xml.integer('birth-year', alias='birth_year'),
    xml.array(xml.user_object('book', Book, [
        xml.string('title'),
        xml.integer('published')
    ]), alias='books')
])

xml.parse_from_string(author_processor, author_xml)
# Author(name=Robert A. Heinlein, birth_year=1907, books=[Book(title=Starship Troopers, published=1950), Book(title=Stranger in a Strange Land, published=1951)])
```

What about namedtuples, you say? Those are extremely useful, and declxml lets you work with them as well
```python
from collections import namedtuple

import declxml as xml


Author = namedtuple('Author', ['name', 'birth_year', 'books'])
Book = namedtuple('Book', ['title', 'published'])


author_processor = xml.named_tuple('author', Author, [
    xml.string('name'),
    xml.integer('birth-year', alias='birth_year'),
    xml.array(xml.named_tuple('book', Book, [
        xml.string('title'),
        xml.integer('published')
    ]), alias='books')
])


xml.parse_from_string(author_processor, author_xml)
# Author(name='Robert A. Heinlein', birth_year=1907, books=[Book(title='Starship Troopers', published=1959), Book(title='Stranger in a Strange Land', published=1961)])
```
