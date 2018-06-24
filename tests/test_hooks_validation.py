"""Tests using hooks for validation"""
from collections import namedtuple

import pytest

import declxml as xml
from .helpers import strip_xml


_UserTuple = namedtuple('_UserTuple', [
    'name',
    'age',
])


class _UserClass(object):

    def __init__(self, name=None, age=None):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return isinstance(other, _UserClass) and\
                other.name == self.name and\
                other.age == self.age

    def __repr__(self):
        return '_UserClass(name=\'{}\', age={})'.format(
            self.name, self.age
        )


class _ValidationError(Exception):
    """Custom validation error class"""


class TestValidateArray(object):
    """Use hooks to validate array values."""

    def test_invalid(self):
        """Invalid array value."""
        xml_string = strip_xml("""
        <data>
            <value>1</value>
            <value>3</value>
            <value>3</value>
        </data>
        """)

        value = [1, 3, 3]

        _assert_invalid(self._processor, value, xml_string)

    def test_valid(self):
        """Valid array value."""
        xml_string = strip_xml("""
        <data>
            <value>1</value>
            <value>2</value>
            <value>3</value>
        </data>
        """)

        value = [1, 2, 3]

        _assert_valid(self._processor, value, xml_string)

    @property
    def _processor(self):
        def validate(state, value):
            if len(value) != len(set(value)):
                state.raise_error(_ValidationError)
            return value

        hooks = xml.Hooks(
            after_parse=validate,
            before_serialize=validate,
        )

        processor = xml.array(xml.integer('value'), hooks=hooks, nested='data')

        return processor


class TestValidateDictionary(object):
    """Use hooks to validate dictionary values."""

    def test_invalid(self):
        """Invalid dictionary value."""
        xml_string = strip_xml("""
        <data>
            <a>5</a>
            <b>6</b>
        </data>
        """)

        value = {
            'a': 5,
            'b': 6,
        }

        _assert_invalid(self._processor, value, xml_string)

    def test_valid(self):
        """Valid dictionary value."""
        xml_string = strip_xml("""
        <data>
            <a>32</a>
            <b>67</b>
        </data>
        """)

        value = {
            'a': 32,
            'b': 67,
        }

        _assert_valid(self._processor, value, xml_string)

    @property
    def _processor(self):
        def validate(state, value):
            if value['a'] == 5 and value['b'] == 6:
                state.raise_error(_ValidationError)
            return value

        hooks = xml.Hooks(
            after_parse=validate,
            before_serialize=validate,
        )

        processor = xml.dictionary('data', [
            xml.integer('a'),
            xml.integer('b'),
        ], hooks=hooks)

        return processor


class TestValidateNamedTuple(object):
    """Use hooks for validating namedtuple values."""

    def test_invalid(self):
        """Invalid namedtuple value"""
        xml_string = strip_xml("""
        <user>
            <name>Bob</name>
            <age>24</age>
        </user>
        """)

        value = _UserTuple(name='Bob', age=24)

        _assert_invalid(self._processor, value, xml_string)

    def test_valid(self):
        """Valid namedtuple value"""
        xml_string = strip_xml("""
        <user>
            <name>Jill</name>
            <age>28</age>
        </user>
        """)

        value = _UserTuple(name='Jill', age=28)

        _assert_valid(self._processor, value, xml_string)

    @property
    def _processor(self):
        def validate(state, value):
            if value.name == 'Bob' and value.age == 24:
                state.raise_error(_ValidationError)
            return value

        hooks = xml.Hooks(
            after_parse=validate,
            before_serialize=validate,
        )

        processor = xml.named_tuple('user', _UserTuple, [
            xml.string('name'),
            xml.integer('age')
        ], hooks=hooks)

        return processor


class TestValidatePrimitive(object):
    """Use hooks for validating primitive values."""

    def test_invalid(self):
        """Invalid primitive value"""
        xml_string = strip_xml("""
        <data>
            <value>-91</value>
        </data>
        """)

        value = {'value': -91}

        _assert_invalid(self._processor, value, xml_string)

    def test_valid(self):
        """Valid primitive value"""
        xml_string = strip_xml("""
        <data>
            <value>32</value>
        </data>
        """)

        value = {'value': 32}

        _assert_valid(self._processor, value, xml_string)

    @property
    def _processor(self):
        def validate(state, value):
            if value < 0:
                state.raise_error(_ValidationError)

            return value

        hooks = xml.Hooks(
            after_parse=validate,
            before_serialize=validate
        )

        processor = xml.dictionary('data', [
            xml.integer('value', hooks=hooks)
        ])

        return processor


class TestValidateUserObject(object):
    """Use hooks for validating user object values."""

    def test_invalid(self):
        """Invalid namedtuple value"""
        xml_string = strip_xml("""
        <user>
            <name>Bob</name>
            <age>24</age>
        </user>
        """)

        value = _UserClass(name='Bob', age=24)

        _assert_invalid(self._processor, value, xml_string)

    def test_valid(self):
        """Valid namedtuple value"""
        xml_string = strip_xml("""
        <user>
            <name>Jill</name>
            <age>28</age>
        </user>
        """)

        value = _UserClass(name='Jill', age=28)

        _assert_valid(self._processor, value, xml_string)

    @property
    def _processor(self):
        def validate(state, value):
            if value.name == 'Bob' and value.age == 24:
                state.raise_error(_ValidationError)
            return value

        hooks = xml.Hooks(
            after_parse=validate,
            before_serialize=validate,
        )

        processor = xml.user_object('user', _UserClass, [
            xml.string('name'),
            xml.integer('age')
        ], hooks=hooks)

        return processor


def _assert_invalid(processor, value, xml_string):
    """Assert the processor rejects the XML and value as invalid."""
    with pytest.raises(_ValidationError):
        xml.parse_from_string(processor, xml_string)

    with pytest.raises(_ValidationError):
        xml.serialize_to_string(processor, value)


def _assert_valid(processor, value, xml_string):
    """Assert the processor accepts the XML and value as valid."""
    actual_value = xml.parse_from_string(processor, xml_string)
    assert value == actual_value

    actual_xml_string = xml.serialize_to_string(processor, value)
    assert xml_string == actual_xml_string
