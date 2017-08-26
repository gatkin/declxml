"""Contains unit tests for parsing logic"""
import pytest

from .. import declxml as xml


def test_parse_attribute():
    """Parses an attribute value"""
    xml_string = """
        <root>
            <element value="hello">27</element>
        </root>
    """

    processor = xml.dictionary('root', [
        xml.string('element', attribute='value'),
    ])

    expected = {
        'value': 'hello',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_attribute_aliased():
    """Parses an attribute value with an alias"""
    xml_string = """
        <root>
            <element value="hello">27</element>
        </root>
    """

    processor = xml.dictionary('root', [
        xml.string('element', attribute='value', alias='value_alias'),
    ])

    expected = {
        'value_alias': 'hello',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual



def test_parse_attribute_default():
    """Parses an attribute with a default value specified"""
    xml_string = """
    <root>
        <element>27</element>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.string('element', attribute='value', required=False, default='Goodbye'),
    ])

    expected = {
        'value': 'Goodbye',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_attribute_default_present():
    """Parses an attribute with a default value specified"""
    xml_string = """
    <root>
        <element value="Hello">27</element>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.string('element', attribute='value', required=False, default='Goodbye'),
    ])

    expected = {
        'value': 'Hello',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_attribute_missing():
    """Parses a missing attribute value"""
    xml_string = """
    <root>
        <element wrong-value="27">Hello</element>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.integer('element', attribute='value')
    ])

    with pytest.raises(xml.MissingValue):
        xml.parse_xml_string(xml_string, processor)


def test_parse_attribute_missing_element():
    """Parses an attribute value with a missing element"""
    xml_string = """
    <root>
        <wrong-element value="27">Hello</wrong-element>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.integer('element', attribute='value')
    ])

    with pytest.raises(xml.MissingValue):
        xml.parse_xml_string(xml_string, processor)


def test_parse_attribute_only():
    """Parses an attribute value that is the only value in an element"""
    xml_string = """
        <root>
            <element value="hello" />
        </root>
    """

    processor = xml.dictionary('root', [
        xml.string('element', attribute='value'),
    ])

    expected = {
        'value': 'hello',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_boolean_invalid():
    """Parse an invalid boolean value"""
    xml_string = """
    <root>
        <value>hello</value>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.boolean('value'),
    ])

    with pytest.raises(xml.InvalidPrimitiveValue):
        xml.parse_xml_string(xml_string, processor)


def test_parse_float_invalid():
    """Parse an invalid float value"""
    xml_string = """
    <root>
        <value>hello</value>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.floating_point('value'),
    ])

    with pytest.raises(xml.InvalidPrimitiveValue):
        xml.parse_xml_string(xml_string, processor)


def test_parse_int_invalid():
    """Parse an invalid int value"""
    xml_string = """
    <root>
        <value>hello</value>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.integer('value'),
    ])

    with pytest.raises(xml.InvalidPrimitiveValue):
        xml.parse_xml_string(xml_string, processor)


def test_parse_primitive():
    """Parse primitve XML values"""
    xml_string = """
    <root>
        <boolean>true</boolean>
        <float>3.14</float>
        <int>1</int>
        <string>Hello, World</string>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.boolean('boolean'),
        xml.floating_point('float'),
        xml.integer('int'),
        xml.string('string'),
    ])

    expected = {
        'boolean': True,
        'float': 3.14,
        'int': 1,
        'string': 'Hello, World',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_primitive_aliased():
    """Parses primitive values with aliases"""
    xml_string = """
    <root>
        <boolean>true</boolean>
        <float>3.14</float>
        <int>1</int>
        <string>Hello, World</string>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.boolean('boolean', alias='b'),
        xml.floating_point('float', alias='f'),
        xml.integer('int', alias='i'),
        xml.string('string', alias='s'),
    ])

    expected = {
        'b': True,
        'f': 3.14,
        'i': 1,
        's': 'Hello, World',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_primitive_default():
    """Parses primitive values with defaults specified"""
    xml_string = """
    <root>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.boolean('boolean', required=False, default=False),
        xml.floating_point('float', required=False, default=0.0),
        xml.integer('int', required=False, default=0),
        xml.string('string', required=False, default=''),
    ])

    expected = {
        'boolean': False,
        'float': 0.0,
        'int': 0,
        'string': '',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_primitive_default_preset():
    """Parses primitive values with defaults specified"""
    xml_string = """
    <root>
        <boolean>true</boolean>
        <float>3.14</float>
        <int>1</int>
        <string>Hello, World</string>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.boolean('boolean', required=False, default=False),
        xml.floating_point('float', required=False, default=0.0),
        xml.integer('int', required=False, default=0),
        xml.string('string', required=False, default=''),
    ])

    expected = {
        'boolean': True,
        'float': 3.14,
        'int': 1,
        'string': 'Hello, World',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_primitive_missing():
    """Parses a missing primitive value"""
    xml_string = """
    <root>
        <wrong-value>15</wrong-value>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.integer('value')
    ])

    with pytest.raises(xml.MissingValue):
        xml.parse_xml_string(xml_string, processor)


def test_parse_string_leave_whitespace():
    """Parses a string value without stripping whitespace"""
    xml_string = """
    <root>
        <value>    Hello, World! </value>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.string('value', strip_whitespace=False)
    ])

    expected = {
        'value': '    Hello, World! ',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual


def test_parse_string_strip_whitespace():
    """Parses a string value stripping whitespace"""
    xml_string = """
    <root>
        <value>    Hello, World! </value>
    </root>
    """

    processor = xml.dictionary('root', [
        xml.string('value')
    ])

    expected = {
        'value': 'Hello, World!',
    }

    actual = xml.parse_xml_string(xml_string, processor)

    assert expected == actual
