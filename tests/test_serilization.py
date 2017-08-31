"""Contains unit tests for serialization logic"""
import re

import pytest

from .. import declxml as xml


def test_attribute_serialize():
    """serializing an attribute value"""
    value = {
        'value': 'Hello, World'
    }

    processor = xml.dictionary('root', [
        xml.string('element', attribute='value')
    ])

    expected = _strip_xml("""
    <root>
        <element value="Hello, World" />
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_aliased():
    """Serialize an aliased attribute"""
    value = {
        'pi': 3.14,
    }

    processor = xml.dictionary('root', [
        xml.floating_point('constant', attribute='value', alias='pi'),
    ])

    expected = _strip_xml("""
    <root>
        <constant value="3.14" />
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_default_missing():
    """Serializes a missing attribute value with a default specified"""
    value = {
        'data': 123,
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='units', required=False, default='feet')
    ])

    expected = _strip_xml("""
    <root>
        <data units="feet">123</data>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_default_present():
    """Serializes an attribute value with a default specified"""
    value = {
        'data': 123,
        'units': 'miles'
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='units', required=False, default='feet')
    ])

    expected = _strip_xml("""
    <root>
        <data units="miles">123</data>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_falsey():
    """Tests serializing a Falsey attribute value"""
    value = {
        'message': '',
        'data': 123,
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='message', required=False)
    ])

    expected = _strip_xml("""
    <root>
        <data message="">123</data>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_falsey_omitted():
    """Tests serializing a Falsey attribute value"""
    value = {
        'message': '',
        'data': 123,
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='message', required=False, omit_empty=True)
    ])

    expected = _strip_xml("""
    <root>
        <data>123</data>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_missing():
    """Serialize a missing attribute value"""
    value = {
        'data': 123,
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='units')
    ])

    with pytest.raises(xml.MissingValue):
        xml.serialize_xml_string(value, processor)


def test_attribute_serialize_missing_empty():
    """Tests serializing a Falsey attribute value"""
    value = {
        'data': 123,
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='message', required=False, omit_empty=True)
    ])

    expected = _strip_xml("""
    <root>
        <data>123</data>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_attribute_serialize_multiple():
    """Serializing multiple attributes to the same element"""
    value = {
        'attribute_a': 'Hello, World',
        'attribute_b': True,
        'data': 1,
        'message': 'Hello, World'
    }

    processor = xml.dictionary('root', [
        xml.integer('data'),
        xml.string('data', attribute='attribute_a'),
        xml.boolean('data', attribute='attribute_b'),
        xml.string('message')
    ])

    expected = _strip_xml("""
    <root>
        <data attribute_a="Hello, World" attribute_b="True">1</data>
        <message>Hello, World</message> 
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_dictionary_serialize_root_empty():
    """Serliazes an empty root dictionary"""
    value = {}

    processor = xml.dictionary('root', [
        xml.string('message')
    ])

    with pytest.raises(xml.MissingValue):
        xml.serialize_xml_string(value, processor)


def test_dictionary_serialize_nested():
    """Serializes nested dictionaries"""
    value = {
        'name': 'John Doe',
        'demographics': {
            'age': 27,
            'gender': 'male',
        },
        'favorites': {
            'food': 'pizza',
            'color': 'blue'
        }
    }

    processor = xml.dictionary('root', [
        xml.string('name'),
        xml.dictionary('demographics', [
            xml.integer('age'),
            xml.string('gender')
        ]),
        xml.dictionary('favorites', [
            xml.string('food'),
            xml.string('color')
        ])
    ])

    expected = _strip_xml("""
    <root>
        <name>John Doe</name>
        <demographics>
            <age>27</age>
            <gender>male</gender>
        </demographics>
        <favorites>
            <food>pizza</food>
            <color>blue</color>
        </favorites>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_dictionary_serialize_nested_aliased():
    """Serializes nested aliased dictionaries"""
    value = {
        'name': 'John Doe',
        'stats': {
            'age': 27,
            'gender': 'male',
        }
    }

    processor = xml.dictionary('root', [
        xml.string('name'),
        xml.dictionary('demographics', [
            xml.integer('age'),
            xml.string('gender')
        ], alias='stats')
    ])

    expected = _strip_xml("""
    <root>
        <name>John Doe</name>
        <demographics>
            <age>27</age>
            <gender>male</gender>
        </demographics>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_dictionary_serialize_nested_missing():
    """Serializes nested dictionaries"""
    value = {
        'name': 'John Doe',
        'demographics': {
            'age': 27,
            'gender': 'male',
        },
    }

    processor = xml.dictionary('root', [
        xml.string('name'),
        xml.dictionary('demographics', [
            xml.integer('age'),
            xml.string('gender')
        ]),
        xml.dictionary('favorites', [
            xml.string('food'),
            xml.string('color')
        ])
    ])

    with pytest.raises(xml.MissingValue):
        xml.serialize_xml_string(value, processor)


def test_dictionary_serialize_nested_missing_optional():
    """Serializes nested dictionaries"""
    value = {
        'name': 'John Doe',
        'demographics': {
            'age': 27,
            'gender': 'male',
        },
    }

    processor = xml.dictionary('root', [
        xml.string('name'),
        xml.dictionary('demographics', [
            xml.integer('age'),
            xml.string('gender')
        ]),
        xml.dictionary('favorites', [
            xml.string('food'),
            xml.string('color')
        ], required=False)
    ])

    expected = _strip_xml("""
    <root>
        <name>John Doe</name>
        <demographics>
            <age>27</age>
            <gender>male</gender>
        </demographics>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_dictionary_serialize_nested_optional_present():
    """Serializes nested dictionaries"""
    value = {
        'name': 'John Doe',
        'demographics': {
            'age': 27,
            'gender': 'male',
        },
        'favorites': {
            'movie': 'Monty Python'
        }
    }

    processor = xml.dictionary('root', [
        xml.string('name'),
        xml.dictionary('demographics', [
            xml.integer('age'),
            xml.string('gender')
        ]),
        xml.dictionary('favorites', [
            xml.string('movie'),
        ], required=False)
    ])

    expected = _strip_xml("""
    <root>
        <name>John Doe</name>
        <demographics>
            <age>27</age>
            <gender>male</gender>
        </demographics>
        <favorites>
            <movie>Monty Python</movie>
        </favorites>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_serialize_aliased():
    """Serializes an aliased primitive value"""
    value = {
        'data': 456,
    }

    processor = xml.dictionary('root', [
        xml.integer('element', alias='data'),
    ])

    expected = _strip_xml("""
    <root>
        <element>456</element>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_serialize_default_missing():
    """Serializes a missing primitive value with a default specified"""
    value = {
        'number': 898,
    }

    processor = xml.dictionary('root', [
        xml.string('message', required=False, default='Hello, World'),
    ])

    expected = _strip_xml("""
    <root>
        <message>Hello, World</message>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_serialize_default_present():
    """Serializes a missing primitive value with a defualt specified"""
    value = {
        'message': 'Hola, Mars'
    }

    processor = xml.dictionary('root', [
        xml.string('message', required=False, default='Hello, World'),
    ])

    expected = _strip_xml("""
    <root>
        <message>Hola, Mars</message>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_serialize_missing():
    """Serializes a missing primitive value"""
    value = {
        'data': 1
    }

    processor = xml.dictionary('root', [
        xml.string('message'),
        xml.integer('data')
    ])

    with pytest.raises(xml.MissingValue):
        xml.serialize_xml_string(value, processor)


def test_primitive_serialize_missing_omitted():
    """Serializes a missing primitive value"""
    value = {
        'data': 1
    }

    processor = xml.dictionary('root', [
        xml.string('message', required=False, omit_empty=True),
        xml.integer('data')
    ])

    expected = _strip_xml("""
    <root>
        <data>1</data>
    </root>  
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_values_serialize_falsey():
    """Serialize false primitive values"""
    value = {
        'boolean': False,
        'float': 0.0,
        'int': 0,
        'string': ''
    }

    processor = xml.dictionary('root', [
        xml.boolean('boolean', required=False),
        xml.floating_point('float', required=False),
        xml.integer('int', required=False),
        xml.string('string', required=False),
    ])

    expected = _strip_xml("""
    <root>  
        <boolean>False</boolean>
        <float>0.0</float>
        <int>0</int>
        <string />
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_values_serialize_falsey_omitted():
    """Serialize false primitive values"""
    value = {
        'boolean': False,
        'float': 0.0,
        'int': 0,
        'string': ''
    }

    processor = xml.dictionary('root', [
        xml.boolean('boolean', required=False, omit_empty=True),
        xml.floating_point('float', required=False, omit_empty=True),
        xml.integer('int', required=False, omit_empty=True),
        xml.string('string', required=False, omit_empty=True),
    ])

    expected = _strip_xml("""
    <root />  
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def test_primitive_values_serialize():
    """Serializes primitive values"""
    value = {
        'boolean': True,
        'float': 3.14,
        'int': 1,
        'string': 'Hello, World'
    }

    processor = xml.dictionary('root', [
        xml.boolean('boolean'),
        xml.floating_point('float'),
        xml.integer('int'),
        xml.string('string'),
    ])

    expected = _strip_xml("""
    <root>  
        <boolean>True</boolean>
        <float>3.14</float>
        <int>1</int>
        <string>Hello, World</string>
    </root>
    """)

    actual = xml.serialize_xml_string(value, processor)

    assert expected == actual


def _strip_xml(xml_string):
    """Prepares the XML string so it can be compared to the actual serialized output""" 
    # Strip internal whitespace between tags
    stripped = re.sub(r'>\s+<', '><', xml_string)

    # Strip external whitespace
    return stripped.strip().encode('utf8')
