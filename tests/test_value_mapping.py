"""Tests for performing arbitrary transformations of XML values during processing"""
from collections import OrderedDict

import pytest

import declxml as xml
from .helpers import strip_xml


class TestArrayValueMapping(object):

    _mapped_value = OrderedDict([
        ('a', 17),
        ('b', 42),
        ('c', 37),
    ])

    _array_item_processor = xml.dictionary('value', [
                xml.string('.', attribute='key'),
                xml.integer('.', alias='value')
            ])

    @staticmethod
    def _from_xml(xml_array):
        dict_value = OrderedDict()
        for item in xml_array:
            dict_value[item['key']] = item['value']

        return dict_value

    @staticmethod
    def _to_xml(dict_value):
        return [{'key': k, 'value': v} for k, v in dict_value.items()]

    def test_array_of_arrays(self):
        """Map array values for a nested array"""
        xml_string = strip_xml("""
            <data>
                <name>Dataset 1</name>
                <values>
                    <value key="a">17</value>
                    <value key="b">42</value>
                    <value key="c">37</value>
                </values>
                <values>
                    <value key="x">34</value>
                    <value key="y">4</value>
                    <value key="z">58</value>
                </values>
            </data>
        """)

        value = {
            'name': 'Dataset 1',
            'values': [
                self._mapped_value,
                OrderedDict([
                    ('x', 34),
                    ('y', 4),
                    ('z', 58),
                ])
            ],
        }

        processor = xml.dictionary('data', [
            xml.string('name'),
            xml.array(
                xml.array(self._item_processor, nested='values', mapping=self._mapping),
            )
        ])

        _mapping_test_case_run(processor, value, xml_string)

    def test_non_root_array(self):
        """Map array values for non-root arrays"""
        xml_string = strip_xml("""
            <data>
                <name>Dataset 1</name>
                <value key="a">17</value>
                <value key="b">42</value>
                <value key="c">37</value>
            </data>
        """)

        value = {
            'name': 'Dataset 1',
            'values': self._mapped_value,
        }

        processor = xml.dictionary('data', [
            xml.string('name'),
            xml.array(self._item_processor, alias='values', mapping=self._mapping)
        ])

        _mapping_test_case_run(processor, value, xml_string)

    def test_root_array(self):
        """Map array values for root arrays"""
        xml_string = strip_xml("""
            <data>
                <value key="a">17</value>
                <value key="b">42</value>
                <value key="c">37</value>
            </data>
        """)

        value = self._mapped_value

        processor = xml.array(self._item_processor, nested='data', mapping=self._mapping)

        _mapping_test_case_run(processor, value, xml_string)

    @property
    def _item_processor(self):
        return TestArrayValueMapping._array_item_processor

    @property
    def _mapping(self):
        return xml.ValueMapping(
            from_xml=TestArrayValueMapping._from_xml,
            to_xml=TestArrayValueMapping._to_xml
        )


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

    mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.boolean('value', mapping=mapping)
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

    mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.floating_point('value', mapping=mapping)
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

    mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.integer('value', mapping=mapping)
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

    mapping = xml.ValueMapping(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.string('value', mapping=mapping)
    ])

    _mapping_test_case_run(processor, value, xml_string)


def _mapping_test_case_run(processor, value, xml_string):
    """Runs the given value mapping test case"""
    actual_value = xml.parse_from_string(processor, xml_string)
    assert value == actual_value

    actual_xml_string = xml.serialize_to_string(processor, value)
    assert xml_string == actual_xml_string
