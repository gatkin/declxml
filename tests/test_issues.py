"""
Contains unit tests that reproduce previous issues. Whenever a new issue is
discovered, a failing test should be added to this file first before the issue
is fixed.
"""
from collections import namedtuple

import declxml as xml
from .helpers import strip_xml


def test_serialize_none_namedtuple_issue_7():
    """Tests attempting to serialize a named tuple value that is None"""
    Athlete = namedtuple('Athlete', [
        'name',
        'age',
    ])
    
    processor = xml.dictionary('race-result', [
        xml.floating_point('time'),
        xml.named_tuple('athlete', Athlete, [
            xml.string('name'),
            xml.integer('age'),
        ], required=False)
    ])

    value = {
        'time': 87.5,
        'athlete': None, 
    }

    expected_xml = strip_xml("""
    <race-result>
        <time>87.5</time>
    </race-result>
    """)

    actual_xml = xml.serialize_to_string(processor, value)

    assert expected_xml == actual_xml


def test_serialize_none_object_issue_7():
    """Attempts to serialize an object value that is None"""
    class Athlete(object):

        def __init__(self):
            self.name = ''
            self.age = 0 


    processor = xml.dictionary('race-result', [
        xml.floating_point('time'),
        xml.user_object('athete', Athlete, [
            xml.string('name'),
            xml.integer('age'),
        ], required=False)
    ])

    value = {
        'time': 87.5,
        'athlete': None,
    }

    expected_xml = strip_xml("""
    <race-result>
        <time>87.5</time>
    </race-result>
    """)

    actual_xml = xml.serialize_to_string(processor, value)

    assert expected_xml == actual_xml
