Quickstart
============

Parsing and Serialization
--------------------------------------
A processor defines the structure of an XML document, and it can be used to both parse and serialize data to and
from XML.

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


    author = {'name': 'Isaac Asimiov', 'birth-year': 1920}
    xml.serialize_to_string(author_processor, author)
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """

Attributes
-------------------
Processors may specify attributes to which values will be serialized to and parsed from.

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


    author = {'name': 'Isaac Asimiov', 'birth-year': 1920, 'birth-month': 'January'}
    xml.serialize_to_string(author_processor, author, indent='    ')
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year birth-month="January">1920</birth-year>
    </author>
    """

Basic Validation
-------------------
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
        <birth-year>Starship Troopers</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # InvalidPrimitiveValue: Invalid integer value: "Starship Troopers"


Optional and Default Values
-----------------------------------
Processors may specify optional and default values.

.. sourcecode:: py

    import declxml as xml 

    author_processor = xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year'),
        xml.integer('death-year', required=False, default=None)
    ])

    author_xml = """
    <author>
        <name>Robert A. Heinlein</name>
        <birth-year>1907</birth-year>
        <death-year>1988</death-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Robert A. Heinlein', 'birth-year': 1907 'death-year': 1988}


    author_xml = """
    <author>
        <name>Liu Cixin</name>
        <birth-year>1963</birth-year>
    </author>
    """

    xml.parse_from_string(author_processor, author_xml)
    # {'name': 'Liu Cixin', 'birth-year': 1963, 'death-year': None}


Arrays
--------
Processors can be defined for array values. An array processor is composed with another
processor for procssing the items of the array. An array can either be *embedded* or *nested*.

An embedded is embedded directly within its parent

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

A nested array is nested within an array element

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
-----------------------
Processors can be composed to define more complex document structures

.. sourcecode:: py

    import declxml as xml

    genre_xml = """
    <genre-authors>
        <genre>Science Fiction</genre>
        <author>
            <name>Robert A. Heinlein</name>
            <birth-year>1907</birth-year>
            <books>
                <book>
                    <title>Starship Troopers</title>
                    <year-published>1959</year-published>
                </book>
                <book>
                    <title>Stranger in a Strange Land</title>
                    <year-published>1961</year-published>
                </book>
            </books>
        </author>
        <author>
            <name>Isaac Asimov</name>
            <birth-year>1920</birth-year>
            <books>
                <book>
                    <title>I, Robot</title>
                    <year-published>1950</year-published>
                </book>
                <book>
                    <title>Foundation</title>
                    <year-published>1951</year-published>
                </book>
            </books>
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
        xml.array(book_processor, nested='books')
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
---------------------
Processors can also be created for parsing and serializing xml data to and from user-defined classes.
Simply provide the class to the processor factor function

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
    author.name = 'Isaac Asimiov'
    author.birth_year = 1920

    xml.serialize_to_string(author_processor, author)
    """
    <author>
        <name>Isaac Asimov</name>
        <birth-year>1920</birth-year>
    </author>
    """