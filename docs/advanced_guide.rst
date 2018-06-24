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

Hooks
-----
Hooks are an advanced feature that allow arbitrary code to be executed during
the parsing and serialization process. A `Hooks` object is associated with a
processor and contains two functions: `after_parse` and `before_serialize`.

Both of these functions (which can be any callable object) are provided two
parameters and should return a single value. The first parameter provided to
both functions is a `ProcessorStateView` object which contains information
about the current state of the processor when the function is invoked.

The `after_parse` function is invoked after a processor has parsed a value
from the XML data. The second parameter provided to the `after_parse` function
is the value parsed by the processor from the XML data. The `after_parse`
function must return a single value which will be used by the processor as its
parse result. The value returned by `after_parse` replaces the value parsed
from the XML data as the processor's parse result.

The `before_serialize` function is invoked before a processor serializes a
value to XML. The second parameter provided to the `before_serialize` function
is the value to be serialized by the processor to XML. The `before_serialize`
function must return a single value which the processor will serialize to XML.
The value returned by `before_serialize` replaces the value provided to the
processor to serialize to XML.

There are three intended use cases for hooks (though since hooks can be any
arbitrary callable objects, there should be flexibility for other use cases):

- Value transformations
- Validation
- Debugging

Value Transformations
"""""""""""""""""""""
Sometimes it is useful to be able to transform values read from XML during
parsing into a shape more convenient for the application to use and transform
values during serialization back into shapes that better fit the XML structure.

Hooks can be used to achieve this by simply returning the transformed value
from the `after_parse` and `before_serialize` functions. This works because
whatever value a processor was going to use for parsing or serialization is
replaced by the value returned by `after_parse` or `before_serialize`.

As a basic example, if we want to make sure all strings read from an XML
document are uppercase when used in our application and lowercase when written
to XML, we could use hooks to perform value transformations.

.. sourcecode:: py

    >>> import declxml as xml

    >>> hooks = xml.Hooks(
    ...     after_parse=lambda _, x: x.upper(),
    ...     before_serialize=lambda _, x: x.lower()
    ... )

    >>> processor = xml.dictionary('data', [
    ...     xml.string('message', hooks=hooks),
    ... ])

    >>> xml_string = """
    ... <data>
    ...    <message>hello</message>
    ... </data>
    ... """

    >>> xml.parse_from_string(processor, xml_string)
    {'message': 'HELLO'}

    >>> data = {'message': 'GOODBYE'}
    >>> print(xml.serialize_to_string(processor, data, indent='    '))
    <?xml version="1.0" encoding="utf-8"?>
    <data>
        <message>goodbye</message>
    </data>

When using hooks to perform value transformations, it is a good idea to ensure
that the transformations performed by `after_parse` and `before_serialize` are
inverse operations of each other so that parsing and serialization work
correctly when using transformed values. This is particular important when
values are transformed into different types.

Validation
""""""""""
By default, declxml only performs a very basic level of validation by ensuring
that required values are present and that they are of the correct type. Hooks
provide the ability to perform additional, application-specific validation.

When performing validation, we can use the `ProcessorStateView` object provided
as the first parameter to the `after_parse` and `before_serialize` functions.
The `ProcessorStateView` object provides a useful method, `raise_error`, for
reporting errors. This method will raise an application-provided exception
with a custom error message and will include information about the current
state of the processor in the error message.

For example, if we wanted to ensure that integer values were in a specific
range, we could use hooks to perform the validation.

.. sourcecode:: py

    >>> import declxml as xml

    >>> def validate(state, value):
    ...     if value not in range(1, 4):
    ...         state.raise_error(
    ...             RuntimeError,
    ...             'Invalid value {}'.format(value)
    ...         )
    ...
    ...     # Important! Don't forget to return the value
    ...     return value

    >>> hooks = xml.Hooks(
    ...     after_parse=validate,
    ...     before_serialize=validate
    ... )

    >>> processor = xml.dictionary('data', [
    ...     xml.integer('value', hooks=hooks),
    ... ])

    >>> xml_string = """
    ... <data>
    ...     <value>567</value>
    ... </data>
    ... """

    >>> xml.parse_from_string(processor, xml_string)
    Traceback (most recent call last):
    ...
    RuntimeError: Invalid value 567 at data/value

    >>> data = {'value': -90}
    >>> xml.serialize_to_string(processor, data)
    Traceback (most recent call last):
    ...
    RuntimeError: Invalid value -90 at data/value

When using hooks for validation, it is important to remember to return the
value from the `before_parse` and `after_serialize` functions since the
processor will used the value returned by those functions as its parsing result
and the value to serialize to XML, respectively.

Debugging
"""""""""
Hooks can also be used to debug processors. We can use the
`ProcessorStateView` object provided to the `before_parse` and
`after_serialize` functions to include information about which values are
received in which locations in the XML document.

.. sourcecode:: py

    >>> import declxml as xml

    >>> def trace(state, value):
    ...     print('Got {} at {}'.format(value, state))
    ...
    ...     # Important! Don't forget to return the value
    ...     return value

    >>> hooks = xml.Hooks(
    ...     after_parse=trace,
    ...     before_serialize=trace
    ... )

    >>> processor = xml.dictionary('data', [
    ...     xml.integer('value', hooks=hooks),
    ... ])

    >>> xml_string = """
    ... <data>
    ...     <value>42</value>
    ... </data>
    ... """

    >>> xml.parse_from_string(processor, xml_string)
    Got 42 at data/value
    {'value': 42}

    >>> data = {'value': 17}
    >>> print(xml.serialize_to_string(processor, data, indent='    '))
    Got 17 at data/value
    <?xml version="1.0" encoding="utf-8"?>
    <data>
        <value>17</value>
    </data>
