"""Tests for performing arbitrary transformations of XML values during processing"""
import pytest

import declxml as xml
from .helpers import strip_xml


def test_boolean_mapping():
    """Map boolean values"""
    xml_string = strip_xml("""
        <data>
            <value>True</value>
        </data>
        """)

    value = {
        'value': 'It is true'
    }

    def _from_xml(x):
        if x:
            return 'It is true'
        else:
            return 'It is false'

    def _to_xml(x):
        if x == 'It is true':
            return True
        else:
            return False

    _mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.boolean('value', mapping=_mapping)
    ])

    _mapping_test_case_run(processor, value, xml_string)


def test_floating_point_mapping():
    """Map floating point values"""
    xml_string = strip_xml("""
        <data>
            <value>13.1</value>
        </data>
    """)

    value = {
        'value': 26.2
    }

    def _from_xml(x):
        return x * 2.0

    def _to_xml(x):
        return x / 2.0

    _mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.floating_point('value', mapping=_mapping)
    ])

    _mapping_test_case_run(processor, value, xml_string)


def test_integer_mapping():
    """Map integer values"""
    xml_string = strip_xml("""
        <data>
            <value>3</value>
        </data>
    """)

    value = {
        'value': 6
    }

    def _from_xml(x):
        return int(x * 2)

    def _to_xml(x):
        return int(x / 2)

    _mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.integer('value', mapping=_mapping)
    ])

    _mapping_test_case_run(processor, value, xml_string)


def test_missing_from_xml_mapping():
    """Parse with a missing from XML mapping"""
    xml_string = strip_xml("""
        <data>
            <value>3</value>
        </data>
    """)

    processor = xml.dictionary('data', [
        xml.integer('value', mapping=xml.ValueMapping())
    ])

    with pytest.raises(xml.XmlError):
        xml.parse_from_string(processor, xml_string)


def test_missing_to_xml_mapping():
    """Serialize with a missing to XML mapping"""
    value = {
        'value': 6,
    }

    processor = xml.dictionary('data', [
        xml.integer('value', mapping=xml.ValueMapping())
    ])

    with pytest.raises(xml.XmlError):
        xml.serialize_to_string(processor, value)


def test_string_mapping():
    """Map string values"""
    xml_string = strip_xml("""
        <data>
            <value>hello</value>
        </data>
    """)

    value = {
        'value': 'HELLO'
    }

    def _from_xml(x):
        return x.upper()

    def _to_xml(x):
        return x.lower()

    _mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.string('value', mapping=_mapping)
    ])

    _mapping_test_case_run(processor, value, xml_string)


def _mapping_test_case_run(processor, value, xml_string):
    """Runs the given value mapping test case"""
    actual_value = xml.parse_from_string(processor, xml_string)
    assert value == actual_value

    actual_xml_string = xml.serialize_to_string(processor, value)
    assert xml_string == actual_xml_string
