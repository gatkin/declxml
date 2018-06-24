Advanced Guide
==============
This guide presents some of the more advanced features supported by declxml
that can be useful when they are needed.

XPath Syntax
------------
declxml supports a very small subset of XPath syntax that enables greater
expressiveness when defining processors.

The Dot (.) Selector
""""""""""""""""""""
The dot (.) selector can be used in a processor to refer to the parent
processor's element. For instance, the dot operator can be used to refer to
attributes on a childless element.

.. sourcecode:: py

    >>> import declxml as xml
    >>> from pprint import pprint

    >>> books_xml = """
    ... <books>
    ...     <book title="I, Robot" author="Isaac Asimov" />
    ...     <book title="Foundation" author="Isaac Asimov" />
    ...     <book title="Nemesis" author="Isaac Asimov" />
    ... </books>
    ... """

    >>> books_processor = xml.array(xml.dictionary('book', [
    ...     xml.string('.', attribute='title'),  # Select the attribute "title" on the element "book"
    ...     xml.string('.', attribute='author'),
    ... ]), nested='books')


    >>> pprint(xml.parse_from_string(books_processor, books_xml))
    [{'author': 'Isaac Asimov', 'title': 'I, Robot'},
     {'author': 'Isaac Asimov', 'title': 'Foundation'},
     {'author': 'Isaac Asimov', 'title': 'Nemesis'}]



The dot operator can also be used to group an element's attribute values with
the values of the element's children.

.. sourcecode:: py

    >>> import declxml as xml
    >>> from pprint import pprint

    >>> author_xml = """
    ... <author name="Liu Cixin">
    ...     <book>The Three Body Problem</book>
    ...     <book>The Dark Forest</book>
    ...     <book>Deaths End</book>
    ... </author>
    ... """

    >>> author_processor = xml.dictionary('author', [
    ...     xml.string('.', attribute='name'),
    ...     xml.array(xml.string('book'), alias='books')
    ... ])

    >>> pprint(xml.parse_from_string(author_processor, author_xml))
    {'books': ['The Three Body Problem', 'The Dark Forest', 'Deaths End'],
     'name': 'Liu Cixin'}

The Path (/) Selector
"""""""""""""""""""""
The path selector (/) can be used to select descendant elements which can be
useful for flattening out deeply nested XML data.

.. sourcecode:: py

    >>> import declxml as xml
    >>> from pprint import pprint

    >>> hugo_xml = """
    ... <awards>
    ...     <hugo>
    ...         <winners>
    ...             <winner>
    ...                 <year>2017</year>
    ...                 <book>
    ...                     <title>The Obelisk Gate</title>
    ...                     <author>N. K. Jemisin</author>
    ...                 </book>
    ...             </winner>
    ...             <winner>
    ...                 <year>2016</year>
    ...                 <book>
    ...                     <title>The Fifth Season</title>
    ...                     <author> N.K. Jemisin</author>
    ...                 </book>
    ...             </winner>
    ...             <winner>
    ...                 <year>2015</year>
    ...                 <book>
    ...                     <title>The Three Body Problem</title>
    ...                     <author>Liu Cixin</author>
    ...                 </book>
    ...             </winner>
    ...         </winners>
    ...     </hugo>
    ... </awards>
    ... """

    >>> hugo_processor = xml.array(xml.dictionary('winner', [
    ...     xml.integer('year'),
    ...     xml.string('book/title', alias='title'),
    ...     xml.string('book/author', alias='author'),
    ... ]), nested='awards/hugo/winners')

    >>> pprint(xml.parse_from_string(hugo_processor, hugo_xml))
    [{'author': 'N. K. Jemisin', 'title': 'The Obelisk Gate', 'year': 2017},
     {'author': 'N.K. Jemisin', 'title': 'The Fifth Season', 'year': 2016},
     {'author': 'Liu Cixin', 'title': 'The Three Body Problem', 'year': 2015}]

The data will be serialized back into the deeply nested XML structure if the
processor is used to perform serialization.

It is *highly* recommended to provide aliases when using XPath syntax to ensure
that when a value is parsed and assigned a name (e.g. a field of a dictionary,
object, or namedtuple), the name of the value is a valid Python identifier
without any '.' or '/' characters.

Value Transforms
----------------
Value transforms are an advanced feature that enable a very high degree of
control over how values are parsed and serialized. Value transforms are
callbacks invoked during the parsing and serialization process. As normal
Python functions (or any callable object), these callbacks can perform any
arbitrary work when invoked. Usually, they are used for transforming values
from shapes that are easy to parse from XML into shapes that are more
convenient for the application to use and vice versa.

As a basic example, if we want to make sure all strings read from an XML
document are uppercase when used in our application and lowercase when written
to XML, we could use a value transform

.. sourcecode:: py

    >>> import declxml as xml

    >>> xml_string = """
    ... <data>
    ...    <message>hello</message>
    ... </data>
    ... """

    >>> hooks = xml.Hooks(after_parse=lambda _, x: x.upper(), before_serialize=lambda _, x: x.lower())
    >>> processor = xml.dictionary('data', [
    ...     xml.string('message', hooks=hooks),
    ... ])

    >>> xml.parse_from_string(processor, xml_string)
    {'message': 'HELLO'}

    >>> data = {'message': 'GOODBYE'}
    >>> print(xml.serialize_to_string(processor, data, indent='    '))
    <?xml version="1.0" encoding="utf-8"?>
    <data>
        <message>goodbye</message>
    </data>
