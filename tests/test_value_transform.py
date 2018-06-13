"""Tests for performing arbitrary transformations of XML values during processing"""
from collections import OrderedDict, namedtuple

import pytest

import declxml as xml
from .helpers import strip_xml


class TestArrayValueTransform(object):
    """Transform array values"""

    _array_item_processor = xml.dictionary('value', [
                xml.string('.', attribute='key'),
                xml.integer('.', alias='value')
            ])

    @staticmethod
    def _from_xml(array_value):
        dict_value = OrderedDict()
        for item in array_value:
            dict_value[item['key']] = item['value']

        return dict_value

    @staticmethod
    def _to_xml(dict_value):
        return [{'key': k, 'value': v} for k, v in dict_value.items()]

    def test_array_of_arrays(self):
        """Transform array values for a nested array"""
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
                OrderedDict([
                    ('a', 17),
                    ('b', 42),
                    ('c', 37),
                ]),
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
                xml.array(self._item_processor, nested='values', transform=self._transform),
            )
        ])

        _transform_test_case_run(processor, value, xml_string)

    def test_non_root_array(self):
        """Transform array values for non-root arrays"""
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
            'values': OrderedDict([
                ('a', 17),
                ('b', 42),
                ('c', 37),
            ]),
        }

        processor = xml.dictionary('data', [
            xml.string('name'),
            xml.array(self._item_processor, alias='values', transform=self._transform)
        ])

        _transform_test_case_run(processor, value, xml_string)

    def test_root_array(self):
        """Transform array values for root arrays"""
        xml_string = strip_xml("""
            <data>
                <value key="a">17</value>
                <value key="b">42</value>
                <value key="c">37</value>
            </data>
        """)

        value = OrderedDict([
            ('a', 17),
            ('b', 42),
            ('c', 37),
        ])

        processor = xml.array(self._item_processor, nested='data', transform=self._transform)

        _transform_test_case_run(processor, value, xml_string)

    @property
    def _item_processor(self):
        return TestArrayValueTransform._array_item_processor

    @property
    def _transform(self):
        return xml.ValueTransform(
            from_xml=TestArrayValueTransform._from_xml,
            to_xml=TestArrayValueTransform._to_xml
        )


class TestDictionaryValueTransform(object):
    """Transform dictionary values"""

    @staticmethod
    def _from_xml(dict_value):
        list_value = []
        for key, value in dict_value.items():
            list_value.append((key, value))

        return sorted(list_value)

    @staticmethod
    def _to_xml(list_value):
        dict_value = {}
        for key, value in list_value:
            dict_value[key] = value

        return dict_value

    def test_array_element_dictionary(self):
        """Apply a transform to a dictionary in an array"""
        xml_string = strip_xml("""
            <results>
                <data>
                    <a>17</a>
                    <b>42</b>
                    <c>23</c>
                </data>
                <data>
                    <a>32</a>
                    <b>2</b>
                    <c>15</c>
                </data>
            </results>
        """)

        value = [
            [
                ('a', 17),
                ('b', 42),
                ('c', 23),
            ],
            [
                ('a', 32),
                ('b', 2),
                ('c', 15),
            ],
        ]

        processor = xml.array(self._dict_processor, nested='results')

        _transform_test_case_run(processor, value, xml_string)

    def test_non_root_dictionary(self):
        """Apply a transform to a non-root dictionary"""
        xml_string = strip_xml("""
            <results>
                <name>Dataset 1</name>
                <data>
                    <a>17</a>
                    <b>42</b>
                    <c>23</c>
                </data>
            </results>
        """)

        value = {
            'name': 'Dataset 1',
            'data': [
                ('a', 17),
                ('b', 42),
                ('c', 23),
            ],
        }

        processor = xml.dictionary('results', [
            xml.string('name'),
            self._dict_processor,
        ])

        _transform_test_case_run(processor, value, xml_string)

    def test_root_dictionary(self):
        """Apply a transform to a root dictionary"""
        xml_string = strip_xml("""
            <data>
                <a>17</a>
                <b>42</b>
                <c>23</c>
            </data>
        """)

        value = [
            ('a', 17),
            ('b', 42),
            ('c', 23),
        ]

        processor = self._dict_processor

        _transform_test_case_run(processor, value, xml_string)

    @property
    def _dict_processor(self):
        transform = xml.ValueTransform(
            from_xml=self._from_xml,
            to_xml=self._to_xml
        )

        return xml.dictionary('data', [
            xml.integer('a'),
            xml.integer('b'),
            xml.integer('c'),
        ], transform=transform)


class TestUserObjectValueTransform(object):
    """Transform user object values"""

    class _Person(object):

        def __init__(self):
            self.name = None
            self.age = None

        def __eq__(self, other):
            return other.name == self.name and other.age == self.age

    @staticmethod
    def _from_xml(object_value):
        return (object_value.name, object_value.age)

    @staticmethod
    def _to_xml(tuple_value):
        object_value = TestUserObjectValueTransform._Person()
        object_value.name = tuple_value[0]
        object_value.age = tuple_value[1]
        return object_value

    def test_array_element_user_object(self):
        """Apply a transform to a user object in an array"""
        xml_string = strip_xml("""
        <people>
            <person>
                <name>John</name>
                <age>24</age>
            </person>
            <person>
                <name>Jane</name>
                <age>27</age>
            </person>
        </people>
        """)

        value = [
            ('John', 24),
            ('Jane', 27),
        ]

        processor = xml.array(self._user_object_processor, nested='people')

        _transform_test_case_run(processor, value, xml_string)

    def test_non_root_user_object(self):
        """Apply a transform to a root user object"""
        xml_string = strip_xml("""
        <data>
            <person>
                <name>John</name>
                <age>24</age>
            </person>
        </data>
        """)

        value = {
            'person': ('John', 24)
        }

        processor = xml.dictionary('data', [
            self._user_object_processor,
        ])

        _transform_test_case_run(processor, value, xml_string)

    def test_root_user_object(self):
        """Apply a transform to a root user object"""
        xml_string = strip_xml("""
        <person>
            <name>John</name>
            <age>24</age>
        </person>
        """)

        value = ('John', 24)

        processor = self._user_object_processor

        _transform_test_case_run(processor, value, xml_string)

    @property
    def _user_object_processor(self):
        transform = xml.ValueTransform(
            from_xml=self._from_xml,
            to_xml=self._to_xml,
        )

        return xml.user_object('person', self._Person, [
            xml.string('name'),
            xml.integer('age'),
        ], transform=transform)


def test_boolean_transform():
    """Transform boolean values"""
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

    transform = xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.boolean('value', transform=transform)
    ])

    _transform_test_case_run(processor, value, xml_string)


def test_floating_point_transform():
    """Transform floating point values"""
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

    transform = xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.floating_point('value', transform=transform)
    ])

    _transform_test_case_run(processor, value, xml_string)


def test_integer_transform():
    """Transform integer values"""
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

    transform = xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.integer('value', transform=transform)
    ])

    _transform_test_case_run(processor, value, xml_string)


def test_missing_from_xml_transform():
    """Parse with a missing from XML transform"""
    xml_string = strip_xml("""
        <data>
            <value>3</value>
        </data>
    """)

    processor = xml.dictionary('data', [
        xml.integer('value', transform=xml.ValueTransform())
    ])

    with pytest.raises(xml.XmlError):
        xml.parse_from_string(processor, xml_string)


def test_missing_to_xml_transform():
    """Serialize with a missing to XML transform"""
    value = {
        'value': 6,
    }

    processor = xml.dictionary('data', [
        xml.integer('value', transform=xml.ValueTransform())
    ])

    with pytest.raises(xml.XmlError):
        xml.serialize_to_string(processor, value)


def test_named_tuple_transform():
    """Transform a named tuple value"""
    Person = namedtuple('Person', ['name', 'age'])

    xml_string = strip_xml("""
    <person>
        <name>John</name>
        <age>24</age>
    </person>
    """)

    value = {
        'name': 'John',
        'age': 24,
    }

    def _from_xml(tuple_value):
        return {
            'name': tuple_value.name,
            'age': tuple_value.age,
        }

    def _to_xml(dict_value):
        return Person(name=dict_value['name'], age=dict_value['age'])

    processor = xml.named_tuple('person', Person, [
        xml.string('name'),
        xml.integer('age'),
    ], transform=xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml))

    _transform_test_case_run(processor, value, xml_string)


def test_primitive_transform_array_element():
    """Transform a primitive value that is an array element"""
    xml_string = strip_xml("""
    <data>
        <value>3</value>
        <value>7</value>
        <value>16</value>
    </data>
    """)

    value = [
        6,
        14,
        32,
    ]

    def _from_xml(x):
        return int(x * 2)

    def _to_xml(x):
        return int(x / 2)

    processor = xml.array(
        xml.integer('value', transform=xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml)),
        nested='data')

    _transform_test_case_run(processor, value, xml_string)


def test_primitive_transform_attribute():
    """Transform a primitive value that is an attribute"""
    xml_string = strip_xml("""
    <data>
        <element value="3" />
    </data>
    """)

    value = {
        'value': 6,
    }

    def _from_xml(x):
        return int(x * 2)

    def _to_xml(x):
        return int(x / 2)

    processor = xml.dictionary('data', [
        xml.integer('element', attribute='value', transform=xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml))
    ])

    _transform_test_case_run(processor, value, xml_string)


def test_string_transform():
    """Transform string values"""
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

    transform = xml.ValueTransform(from_xml=_from_xml, to_xml=_to_xml)

    processor = xml.dictionary('data', [
        xml.string('value', transform=transform)
    ])

    _transform_test_case_run(processor, value, xml_string)


def _transform_test_case_run(processor, value, xml_string):
    """Runs the given value transform test case"""
    actual_value = xml.parse_from_string(processor, xml_string)
    assert value == actual_value

    actual_xml_string = xml.serialize_to_string(processor, value)
    assert xml_string == actual_xml_string
