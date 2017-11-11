"""Contains unit tests for handling XPath syntax in processors"""
import declxml as xml
from .helpers import strip_xml


class TestDot(object):
    """Parse/serialize with dot specifier"""

    _xml_string = strip_xml("""
    <files>
        <file name="a.txt" size="236" />
        <file name="b.txt" size="7654" />
    </files>
    """)

    _value = [
        {
            'name': 'a.txt',
            'size': 236,
        },
        {
            'name': 'b.txt',
            'size': 7654,
        }
    ]

    _processor = xml.array(xml.dictionary('file', [
        xml.string('.', attribute='name'),
        xml.integer('.', attribute='size')
    ]), nested='files')

    def test_parse_dot(self):
        """Parse with dot specifier"""
        actual_value = xml.parse_from_string(TestDot._processor, TestDot._xml_string)

        assert TestDot._value == actual_value

    def test_serialize_dot(self):
        """Serialize with dot specifier"""
        actual_xml_string = xml.serialize_to_string(TestDot._processor, TestDot._value)

        assert TestDot._xml_string == actual_xml_string


class TestMixed(object):
    """Process with a mix of specifiers"""

    _xml_string = strip_xml("""
    <location name="Kansas City">
        <coordinates>
            <lat>39.0997</lat>
            <lon>94.5786</lon>
        </coordinates>
    </location>
    """)

    _value = {
        'name': 'Kansas City',
        'lat': 39.0997,
        'lon': 94.5786,
    }

    _processor = xml.dictionary('location', [
        xml.string('.', attribute='name'),
        xml.floating_point('coordinates/lat', alias='lat'),
        xml.floating_point('coordinates/lon', alias='lon')
    ])

    def test_parse_mixed(self):
        """Parse mix of specifiers"""
        actual_value = xml.parse_from_string(TestMixed._processor, TestMixed._xml_string)

        assert TestMixed._value == actual_value

    def test_serialize_mixed(self):
        """Serialize mix of specifiers"""
        actual_xml_string = xml.serialize_to_string(TestMixed._processor, TestMixed._value)

        assert TestMixed._xml_string == actual_xml_string


class TestNestedSlash(object):
    """Process with nested slash specifiers"""

    _xml_string = strip_xml("""
    <root>
        <place>
            <city>
                <name>Kansas City</name>
                <location>
                    <coordinates>
                        <lat>39.0997</lat>
                        <lon>94.5786</lon>
                    </coordinates>
                </location>
            </city>
        </place>
    </root>
    """)

    _value = {
        'name': 'Kansas City',
        'lat': 39.0997,
        'lon': 94.5786,
    }

    _processor = xml.dictionary('root', [
        xml.string('place/city/name', alias='name'),
        xml.floating_point('place/city/location/coordinates/lat', alias='lat'),
        xml.floating_point('place/city/location/coordinates/lon', alias='lon')
    ])

    def test_parse_nested_slash(self):
        """Parse with nested slashes"""
        actual_value = xml.parse_from_string(TestNestedSlash._processor,
                                             TestNestedSlash._xml_string)

        assert TestNestedSlash._value == actual_value

    def test_serialize_nested_slash(self):
        """Serialize with nested slashes"""
        actual_xml_string = xml.serialize_to_string(TestNestedSlash._processor,
                                                    TestNestedSlash._value)

        assert TestNestedSlash._xml_string == actual_xml_string


class TestSlash(object):
    """Process with slash specifier"""

    _xml_string = strip_xml("""
    <city>
        <name>Kansas City</name>
        <coordinates>
            <lat>39.0997</lat>
            <lon>94.5786</lon>
        </coordinates>
    </city>
    """)

    _value = {
        'name': 'Kansas City',
        'lat': 39.0997,
        'lon': 94.5786,
    }

    _processor = xml.dictionary('city', [
        xml.string('name'),
        xml.floating_point('coordinates/lat', alias='lat'),
        xml.floating_point('coordinates/lon', alias='lon')
    ])

    def test_parse_slash(self):
        """Parse with slash specifier"""
        actual_value = xml.parse_from_string(TestSlash._processor, TestSlash._xml_string)

        assert TestSlash._value == actual_value

    def test_serialize_slash(self):
        """Serialize with slash specifier"""
        actual_xml_string = xml.serialize_to_string(TestSlash._processor, TestSlash._value)

        assert TestSlash._xml_string == actual_xml_string


class TestSlashFromRoot(object):
    """Process with a slash starting from the root element"""

    _xml_string = strip_xml("""
    <locations>
        <cities>
            <city name="Kansas City" state="MO" />
            <city name="Lincoln" state="NE" />
            <city name="Salt Lake City" state="UT" />
        </cities>
    </locations>
    """)

    _value = [
        {
            'name': 'Kansas City',
            'state': 'MO'
        },
        {
            'name': 'Lincoln',
            'state': 'NE'
        },
        {
            'name': 'Salt Lake City',
            'state': 'UT'
        }
    ]

    _processor = xml.array(xml.dictionary('city', [
        xml.string('.', attribute='name'),
        xml.string('.', attribute='state'),
    ]), nested='locations/cities', alias='cities')

    def test_parse_slash_from_root(self):
        """Parse with slash from root"""
        actual_value = xml.parse_from_string(TestSlashFromRoot._processor,
                                             TestSlashFromRoot._xml_string)

        assert TestSlashFromRoot._value == actual_value

    def test_serialize_slash_from_root(self):
        """Serialize with slash from root"""
        actual_xml_string = xml.serialize_to_string(TestSlashFromRoot._processor,
                                                    TestSlashFromRoot._value)

        assert TestSlashFromRoot._xml_string == actual_xml_string
