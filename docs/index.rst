.. declxml documentation master file, created by
   sphinx-quickstart on Sat Sep  2 08:22:41 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

declxml - Declarative XML Processing
====================================

The declxml library provides a simple, declarative API for parsing and
serializing XML documents. For the most common and straightforward processing
tasks, declxml aims to replace the need for writing and maintaining dozens or
hundreds of lines of imperative serialization and parsing logic required when
using lower-level APIs such as ElementTree directly. The declxml library was
inspired by the simplicity and declarative nature of Golang's XML processing
library.

declxml works with *processors* which declaratively define the structure of an
XML document. Processors are used to both serialize and parse XML data as well
as to perform a basic level of validation.


Installation
------------
Install with pip

.. sourcecode:: bash

    pip install -U declxml


.. toctree::
   :maxdepth: 2

   guide
   advanced_guide
   api


Usage
-----
With declxml, you declaratively define the structure of your XML document using
processors which can be used for both parsing and serialization.

.. sourcecode:: py

    >>> import declxml as xml
    >>> from pprint import pprint

    >>> author_processor = xml.dictionary('author', [
    ...     xml.string('name'),
    ...     xml.integer('birth-year'),
    ...     xml.array(xml.dictionary('book', [
    ...         xml.string('title'),
    ...         xml.integer('published')
    ...     ]), alias='books')
    ... ])

    >>> author_xml = """
    ... <author>
    ...     <name>Robert A. Heinlein</name>
    ...     <birth-year>1907</birth-year>
    ...     <book>
    ...         <title>Starship Troopers</title>
    ...         <published>1959</published>
    ...     </book>
    ...     <book>
    ...         <title>Stranger in a Strange Land</title>
    ...         <published>1961</published>
    ...     </book>
    ... </author>
    ... """

    >>> pprint(xml.parse_from_string(author_processor, author_xml))
    {'birth-year': 1907,
     'books': [{'published': 1959, 'title': 'Starship Troopers'},
               {'published': 1961, 'title': 'Stranger in a Strange Land'}],
     'name': 'Robert A. Heinlein'}

    # The same processor is used for serializing as well.
    >>> author = {
    ...     'birth-year': 1920,
    ...     'name': 'Issac Asimov',
    ...     'books': [
    ...         {
    ...             'title': 'I, Robot',
    ...             'published': 1950
    ...         },
    ...         {
    ...             'title': 'Foundation',
    ...             'published': 1951
    ...         }
    ...     ]
    ... }

    >>> print(xml.serialize_to_string(author_processor, author, indent='   '))
    <?xml version="1.0" encoding="utf-8"?>
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

