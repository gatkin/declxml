Guide
=====
The basic building blocks used in the declxml library are *processor* objects. Processors are used to define the structure of the
XML document. There are two types of processors:

* **Primitive** processors - Used for processing simple, primitive values like booleans, integers, floats, and strings.
* **Aggregate** processors - Used for processing aggregate values such as dictionaries, arrays, and objects. Aggregate processors are themselves composed of other processors.


Primitive processors are created using the processor factory function that corresponds to the type of value to process. The
factory functions offer several options for configuring a processor. The following creates a basic processor for integer values
contained within an "id" element:

.. sourcecode:: py

    import declxml as xml

    xml.integer('id')

Aggregate processors are created by specifying a list of child processors that compose the aggregate. The following creates a processor
for a dictionary values contained within a "user" element that itself contains a "user-name" and an "id" sub-element:

.. sourcecode:: py

    import declxml as xml

    xml.dictionary('user', [
        xml.integer('id'),
        xml.string('user-name')
    ])


Parsing and Serialization
-------------------------
Processors define the structure of an XML document and are used to both parse and serialize data to and from XML.

.. sourcecode:: py

    import declxml as xml 

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
    </author>
    """

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year')
    ])

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Robert A. Heinlein', 'birth-year': 1907}


    author = {'name': 'Isaac Asimov', 'birth-year': 1920}
    xml.serialize_to_string(author_processor, author, indent='  ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """

Attributes
----------
Processors may be configured to read and write values from attributes.

.. sourcecode:: py

    import declxml as xml

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year'),
        xml.string('birth-year', attribute='birth-month')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year birth-month="July">1907</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Robert A. Heinlein', 'birth-year': 1907 'birth-month': 'July'}


    author = {'name': 'Isaac Asimov', 'birth-year': 1920, 'birth-month': 'January'}
    xml.serialize_to_string(author_processor, author, indent='    ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year birth-month="January">1920</birth-year>
    </author>
    """

Validation
----------
Processors can perform basic validation such as ensuring required elements are present.

.. sourcecode:: py

    import declxml as xml

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # MissingValue: Missing required element: "birth-year"


Processors also ensure values are of the correct type.

.. sourcecode:: py

    import declxml as xml

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>Hello</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # InvalidPrimitiveValue: Invalid integer value: "Hello"


Optional and Default Values
---------------------------
Processors may specify optional and default values.

.. sourcecode:: py

    import declxml as xml 

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year'),
        xml.string('genre', required=False, default='Science Fiction')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Robert A. Heinlein', 'birth-year': 1907 'genre': 'Science Fiction'}


    author_xml = """
    <author>
        <name>J. K. Rowling</name>
        <birth-year>1965</birth-year>
        <genre>Fantasy</genre>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'J. K. Rowling', 'birth-year': 1965, 'genre': 'Fantasy'}


Aliases
-------
By default, processors use the element name as the name of the value in Python. An alias can be provided to use a different name for
the value in Python.

.. sourcecode:: python

    import declxml as xml 

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
    </author>
    """

    author_processor = xml.dictionary('author', [
        xml.string('name', alias='author_name'),
        xml.integer('birth-year', alias='year_born')
    ])

    xml.parse_from_string(author_processor, author_xml)
    # {'author_name': 'Robert A. Heinlein', 'year_born': 1907}


    author = {'author_name': 'Isaac Asimov', 'year_born': 1920}
    xml.serialize_to_string(author_processor, author, indent='   ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """

Omitting Empty Values
---------------------
Processors can be configured to omit missing or falsey values when serializing. Only optional values may be omitted.

.. sourcecode:: python

    import declxml as xml

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year'),
        xml.integer('nationality', required=False, omit_empty=True)
    ])

    author = {'name': 'Isaac Asimov', 'birth-year': 1920, 'nationality': ''}
    xml.serialize_to_string(author_processor, author, indent='    ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """

    author = {'name': 'Robert A. Heinlein', 'birth-year': 1907, 'nationality': 'American'}
    xml.serialize_to_string(author_processor, author, indent='    ')
    """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
        <nationality>American</nationality>
    </author>
    """


Arrays
------
Processors can be defined for array values. When creating an array processor, a processor must be specified for processing
the array's items. An array is treated as optional if its item processor is configured as optional. .

An array can either be *embedded* or *nested*. An embedded is embedded directly within its parent

.. sourcecode:: py

    import declxml as xml

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.array(xml.string('book'), alias='books')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <book>Starship Troopers</book>
        <book>Stranger in a Strange Land</book>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Robert A. Heinlein', 'books': ['Starship Troopers', 'Stranger in a Strange Land']}

A nested array is nested within a separate array element

.. sourcecode:: py

    import declxml as xml

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.array(xml.string('book'), nested='books')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <books>
            <book>Starship Troopers</book>
            <book>Stranger in a Strange Land</book>
        </books>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Robert A. Heinlein', 'books': ['Starship Troopers', 'Stranger in a Strange Land']}


Composing Processors
--------------------
Processors can be composed to define more complex document structures.

.. sourcecode:: py

    import declxml as xml

    genre_xml = """
    <genre-authors>
        <genre>Science Fiction</genre>
        <author>
            <name>Robert A. Heinlein</name>
            <birth-year>1907</birth-year>
            <book>
                <title>Starship Troopers</title>
                <year-published>1959</year-published>
            </book>
            <book>
                <title>Stranger in a Strange Land</title>
                <year-published>1961</year-published>
            </book>
        </author>
        <author>
            <name>Isaac Asimov</name>
            <birth-year>1920</birth-year>
            <book>
                <title>I, Robot</title>
                <year-published>1950</year-published>
            </book>
            <book>
                <title>Foundation</title>
                <year-published>1951</year-published>
            </book>
        </author>
    </genre-authors>
    """

    book_processor = xml.dictionary('book', [
        xml.string('title'),
        xml.integer('year-published')
    ])

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year'),
        xml.array(book_processor, alias='books')
    ])

    genre_processor = xml.dictionary('genre-authors', [
        xml.string('genre'),
        xml.array(author_processor, alias='authors')
    ])


    xml.parse_from_string(genre_processor, genre_xml)
    { 'genre': 'Science Fiction',
      'authors': [ { 'name': 'Robert A. Heinlein',
                 'birth-year': 1907,
                 'books': [ { 'title': 'Starship Troopers',
                              'year-published': 1959},
                            { 'title': 'Stranger in a Strange Land',
                              'year-published': 1961}],
                 },
               { 'name': 'Isaac Asimov',
                 'birth-year': 1920,
                 'books': [ {'title': 'I, Robot', 'year-published': 1950},
                            {'title': 'Foundation', 'year-published': 1951}],
                 }],
    }


User-Defined Classes
--------------------
Processors can also be created for parsing and serializing XML data to and from user-defined classes.
Simply provide the class to the processor factory function.

.. sourcecode:: py

    import declxml as xml

    class Author:

        def __init__(self):
            self.name = None
            self.birth_year = None

        def __repr__(self):
            return 'Author(name={}, birth_year={})'.format(
                self.name, self.birth_year)

    
    author_processor = xml.user_object('author', Author, [
        xml.string('name'),
        xml.integer('birth-year', alias='birth_year')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # Author(name=Robert A. Heinlein, birth_year=1907)

    author = Author()
    author.name = 'Isaac Asimov'
    author.birth_year = 1920

    xml.serialize_to_string(author_processor, author, indent='    ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """

Note that the class provided to the `user_object` factory function must have a zero-argument constructor.
It is also possible to pass any other callable object that takes zero parameters and returns an object
instance to which parsed values will be read into.


Named Tuples
------------
Processors may also be created for named tuple values.

.. sourcecode:: py

    from collections import namedtuple

    import declxml as xml

    
    Author = namedtuple('Author', ['name', 'birth_year'])

    
    author_processor = xml.named_tuple('author', Author, [
        xml.string('name'),
        xml.integer('birth-year', alias='birth_year')
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # Author(name='Robert A. Heinlein', birth_year=1907)

    author = Author(name='Isaac Asimov', birth_year=1920)
    xml.serialize_to_string(author_processor, author, indent='    ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """
