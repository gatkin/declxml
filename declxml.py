"""Enables XML to be processed using declarative syntax"""
import warnings
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET

class XmlParseError(Exception):
    """Represents errors encountered when parsing XML data"""


class InvalidPrimitiveValue(XmlParseError):
    """Represents errors due to invalid primitive values"""


class InvalidRootProcessor(XmlParseError):
    """Represents errors due to an invalid root processor"""


class MissingValue(XmlParseError):
    """Represents errors due to a missing required element"""


def parse_xml_file(xml_file_path, root_proccesor):
    """Parses the XML file using the processor as the root of the document"""
    with open(xml_file_path) as xml_file:
        xml_string = xml_file.read()
        parsed = parse_xml_string(xml_string, root_proccesor)

    return parsed


def parse_xml_string(xml_string, root_processor):
    """Parses the XML string using the processor as the root of the document"""
    if not _is_valid_root_processor(root_processor):
        raise InvalidRootProcessor('Invalid root processor')

    root = ET.fromstring(xml_string)
    return root_processor.parse_at_root(root)


def serialize_xml_string(value, root_processor, indent=None):
    """
    Serializes the value to an XML string using the root processor.

    :param indent: If specified, then the XML will be pretty formatted with the indentation.

    :return: The serialized XML string. If the omit_empty option was specified for the root
        processer, and the value is a Falsey value, then an empty string will be returned.
    """
    if not _is_valid_root_processor(root_processor):
        raise InvalidRootProcessor('Invalid root processor')

    root = root_processor.serialize(value)
    if root is None:
        return ''

    serialized = ET.tostring(root)

    # Why does element tree not support pretty printing XML?
    if indent:
        serialized = minidom.parseString(serialized).toprettyxml(indent=indent)

    return serialized


def array(item_processor, alias=None, nested=None, omit_empty=False):
    """
    Creates an array processor that can be used to parse and serialize array
    data.

    XML arrays may be nested or they may be embedded within their parent.
    A nested array would look like:
        <root-element>
            <some-element>ABC</some-element>
            <nested-array>
                <array-item>0</array-item>
                <array-item>1</array-item>
            </nested-array>
        </root-element>

    The corresponding embedded array would look like:
		<root-element>
            <some-element>ABC</some-element>
            <array-item>0</array-item>
            <array-item>1</array-item>
        </root-element>

    :param item_processor: A declxml processor object for the items of the array.
    :param alias: If specified, the name given to the array when read from XML.
        If not specified, then the name of the items is used instead.
    :param nested: If the array is a nested array, then this should be the name of
        the element under which all array items are located. If not specified, then
        the array is treated as an embedded array.
    :param omit_empty: If True, then empty lists will be omitted when serializing
        array values to XML.

    :return: A declxml processor object.
    """
    return _Array(item_processor, alias, nested, omit_empty)


def boolean(element_name, attribute=None, required=True, alias=None, default=False, omit_empty=False):
    """
    Creates a processor for boolean values.

    :param element_name: Name of the XML element containing the value
    :param attribute: If specified, then the value is searched for under the
        attribute within the element specified by element_name. If not specified,
        then the value is searched for as the contents of the element specified by
        element_name.
    :param required: Indicates whether the value is required when parsing and serializing.
    :param alias: If specified, then this is used as the name of the value when read from
        XML. If not specified, then the element_name is used as the name of the value.
    :param default: Default value to use if the element is not present. This option is only
        valid if required is specified as False.
    :param omit_empty: If True, then Falsey values will be ommitted when serializing to XML.

    :return: A declxml processor object.
    """
    return _PrimitiveValue(element_name, _parse_boolean, attribute, required, alias, default, omit_empty)


def dictionary(element_name, children, required=True, alias=None, omit_empty=False):
    """
    Creates a processor for dictionary values.

    :param element_name: Name of the XML element containing the dictionary value.
    :param children: List of declxml processor objects for processing the children
        contained within the dictionary.
    :param required: Indicates whether the value is required when parsing and serializing.
    :param alias: If specified, then this is used as the name of the value when read from
        XML. If not specified, then the element_name is used as the name of the value.
    :param omit_empty: If True, the empty dictionary values will be omitted when serializing
        to XML.

    :return: A declxml processor object.
    """
    return _Dictionary(element_name, children, required, alias, omit_empty)


def floating_point(element_name, attribute=None, required=True, alias=None, default=0.0, omit_empty=False):
    """
    Creates a processor for floating point values.

    .. seealso:: boolean()
    """
    return _PrimitiveValue(element_name, _parse_float, attribute, required, alias, default, omit_empty)


def integer(element_name, attribute=None, required=True, alias=None, default=0, omit_empty=False):
    """
    Creates a processor for integer values.

    .. seealso:: boolean()
    """
    return _PrimitiveValue(element_name, _parse_int, attribute, required, alias, default, omit_empty)


def string(element_name, attribute=None, required=True, alias=None, default='', strip_whitespace=True, omit_empty=False):
    """
    Creates a processor for integer values.

    :param strip_whitespace: Indicates whether leading and trailing whitespace should be stripped
        from parsed string values.

    .. seealso:: boolean()
    """
    parser = _parse_string(strip_whitespace)
    return _PrimitiveValue(element_name, parser, attribute, required, alias, default, omit_empty)


class _Array(object):
    """An XML processor object for Array values"""

    def __init__(self, item_processor, alias=None, nested=None, omit_empty=False):
        self._item_processor = item_processor
        self._nested = nested
        self.omit_empty = omit_empty
        self.required = item_processor.required
        if alias:
            self.alias = alias
        elif nested:
            self.alias = nested
        else:
            self.alias = item_processor.alias

    def parse_at_element(self, element):
        """Parses the provided element as an array"""
        return self._parse(element)

    def parse_at_root(self, root):
        """Parses the root XML element as an array"""
        if not self._nested:
            raise InvalidRootProcessor('Non-nested array "{}" cannot be root element'.format(
                self.alias))

        parsed_array = []
        if root.tag == self._nested:
            parsed_array = self._parse(root)
        elif self.required:
            raise MissingValue('Missing required array: "{}"'.format(self.alias))

        return parsed_array

    def parse_from_parent(self, parent):
        """Parses the array data from the provided parent XML element"""
        if self._nested:
            item_iter = parent.find(self._nested)
        else:
            # The array's items are emebedded within the parent
            item_iter = parent.findall(self._item_processor.element_name)

        return self._parse(item_iter)

    def serialize(self, value):
        """
        Serializes the value into a new Element object and returns it. If the
        value is an empty list, and the processor has been configured with the
        omit_empty option specified, then this will return None.
        """
        if self._nested is None:
            raise InvalidRootProcessor('Cannot directly serialize a non-nested array: {}'.format(
                self.alias))

        if not value and self.required:
            raise MissingValue('Missing required array: "{}"'.format(
                self.alias))

        if not value and self.omit_empty:
            return None

        element = ET.Element(self._nested)
        self._serialize(element, value)

        return element

    def serialize_on_parent(self, parent, value):
        """Serializes value and appends it to the parent element"""
        if not value and self.required:
            raise MissingValue('Missing required array: "{}"'.format(
                self.alias))

        if not value and self.omit_empty:
            return  # Do Nothing

        if self._nested is not None:
            array_parent = _element_get_or_add_from_parent(parent, self._nested)
        else:
            # Embedded array has all items serialized directly on the parent.
            array_parent = parent

        self._serialize(array_parent, value)

    def _parse(self, item_iter):
        """
        Parses the array data by using the provided iterator of XML elements to iterate over
        the item elements.
        """
        parsed_array = []

        if item_iter is not None:
            parsed_array = [self._item_processor.parse_at_element(item) for item in item_iter]

        if not parsed_array and self.required:
            raise MissingValue('Missing required array: "{}"'.format(self.alias))

        return parsed_array

    def _serialize(self, array_parent, value):
        """Serializes the array value adding it to the array parent element"""
        if not value:
            # Nothing to do. Avoid attempting to iterate over a possibly
            # None value.
            return

        for item_value in value:
            item_element = self._item_processor.serialize(item_value)
            if item_element is not None:
                array_parent.append(item_element)


class _Dictionary(object):
    """An XML processor object for dictionary values"""

    def __init__(self, element_name, child_processors, required=True, alias=None, omit_empty=False):
        self.element_name = element_name
        self._child_processors = child_processors
        self.required = required
        self.omit_empty = omit_empty
        if alias:
            self.alias = alias
        else:
            self.alias = element_name

    def parse_at_element(self, element):
        """Parses the provided element as a dictionary"""
        parsed_dict = {}

        if element is not None:
            for child in self._child_processors:
                parsed_dict[child.alias] = child.parse_from_parent(element)
        elif self.required:
            raise MissingValue('Missing required dictionary: "{}"'.format(self.element_name))

        return parsed_dict

    def parse_at_root(self, root):
        """Parses the root XML element as a dictionary"""
        parsed_dict = {}

        if root.tag == self.element_name:
            parsed_dict = self.parse_at_element(root)
        elif self.required:
            raise MissingValue('Missing required dictionary: "{}"'.format(self.element_name))

        return parsed_dict

    def parse_from_parent(self, parent):
        """Parses the dictionary data from the provided parent XML element"""
        element = parent.find(self.element_name)
        return self.parse_at_element(element)

    def serialize(self, value):
        """
        Serializes the value to a new element and returns the element. If omit_empty
        was specified and the value is an empty dictionary, then this will return
        None.
        """
        if not value and self.required:
            raise MissingValue('Missing required dictionary: "{}"'.format(self.element_name))

        if not value and self.omit_empty:
            return None

        element = ET.Element(self.element_name)
        self._serialize(element, value)
        return element

    def serialize_on_parent(self, parent, value):
        """Serializes the value and adds it to the parent"""
        if not value and self.required:
            raise MissingValue('Missing required dictionary: "{}"'.format(
                self.element_name))

        if not value and self.omit_empty:
            return  # Do Nothing

        element = _element_get_or_add_from_parent(parent, self.element_name)
        self._serialize(element, value)

    def _serialize(self, element, value):
        """Serializes the dictionary appending all serialized children to the element"""
        if value is None:
            value = {}

        for child in self._child_processors:
            child_value = value.get(child.alias)
            child.serialize_on_parent(element, child_value)


class _PrimitiveValue(object):
    """An XML processor object for processing primitive values"""

    def __init__(self, element_name, parser_func, attribute=None, required=True, alias=None, default=None, omit_empty=False):
        """
        :param element_name: Name of the XML element containing the value.
        :param parser_func: Function to parse the raw XML value. Should take a string and return
            the value parsed from the raw string.
        :param required: Indicates whether the value is required.
        :param alias: Alternative name to give to the value. If not specified, element_name is used.
        :param default: Default value. Only valid if required is False.
        :param omit_empty: Omit the value when serializing if it is a falsey value. Only valid if required is
            False.
        """
        self.element_name = element_name
        self._parser_func = parser_func
        self._attribute = attribute
        self.required = required
        self._default = default

        if alias:
            self.alias = alias
        elif attribute:
            self.alias = attribute
        else:
            self.alias = element_name

        # If a value is required, then it will never be ommitted when serialized. This
        # is to ensure that data that is serialized by a processor can also be parsed
        # by a processor. Omitting required values would lead to an error when attempting
        # to parse the XML data. This only needs to be enforced for primitive values where
        # a value must be None to be considered missing, but is considered empty if it is
        # falsey.
        if required:
            self.omit_empty = False
            if omit_empty:
                warnings.warn('omit_empty ignored on primitive values when required is specified')
        else:
            self.omit_empty = omit_empty


    def parse_at_element(self, element):
        """Parses the primitive value at the given XML element"""
        parsed_value = self._default

        if element is not None:
            if self._attribute:
                parsed_value = self._parse_attribute(element)
            else:
                parsed_value = self._parser_func(element.text)
        elif self.required:
            raise MissingValue('Missing required element: "{}"'.format(self.element_name))

        return parsed_value

    def parse_from_parent(self, parent):
        """Parses the primitive value under the provided parent XML element"""
        element = parent.find(self.element_name)
        return self.parse_at_element(element)

    def serialize(self, value):
        """
        Serializes the value into a new element object and returns the element. If the omit_empty
        option was specified and the value is falsey, then this will return None.
        """
        # Note that falsey values are not treated as missing, but they may be omitted.
        if value is None and self.required:
            raise MissingValue('Missing required value: "{}"'.format(self.element_name))

        if not value and self.omit_empty:
            return None

        element = ET.Element(self.element_name)
        self._serialize(element, value)
        return element

    def serialize_on_parent(self, parent, value):
        """Serializes the value adding it to the parent element"""
        if value is None and self.required:
            raise MissingValue('Missing required value: "{}"'.format(self.element_name))

        if not value and self.omit_empty:
            return  # Do Nothing

        element = _element_get_or_add_from_parent(parent, self.element_name)
        self._serialize(element, value)

    def _parse_attribute(self, element):
        """Parses the primiteve value within the XML element's attribute"""
        parsed_value = self._default
        attribute_value = element.get(self._attribute, None)
        if attribute_value:
            parsed_value = self._parser_func(attribute_value)
        elif self.required:
            raise MissingValue('Missing required attribute "{}" on element "{}"'.format(
                self._attribute, self.element_name))

        return parsed_value

    def _serialize(self, element, value):
        """Serializes the value to the element"""
        # A value is only considered missing, and hence elegible to be replaced by its
        # default only if it is None. Falsey values are not considered missing and are
        # not replaced by the default.
        if value is None:
            serialized_value = str(self._default)
        else:
            serialized_value = str(value)

        if self._attribute:
            element.set(self._attribute, serialized_value)
        else:
            element.text = serialized_value


def _element_get_or_add_from_parent(parent, element_name):
    """
    If an element with the give name has already been added to the parent element,
    then this returns the existing element. Otherwise, this will create a new element
    with the given name, append it to the parent, and return the newly created element.
    This allows for multiple values to be serialized to the same element which can occur
    if an element has any attributes.
    """
    element = parent.find(element_name)
    if element is None:
        element = ET.Element(element_name)
        parent.append(element)

    return element


def _is_valid_root_processor(processor):
    """Returns True if the given XML processor can be used as a root processor"""
    return hasattr(processor, 'parse_at_root')


def _parse_boolean(element_text):
    """Parses the raw XML string as a boolean value"""
    lowered_text = element_text.lower()
    if lowered_text == 'true':
        value = True
    elif lowered_text == 'false':
        value = False
    else:
        raise InvalidPrimitiveValue('Invalid boolean value: {}'.format(element_text))

    return value


def _parse_float(element_text):
    """Parses the raw XML string as a floating point value"""
    try:
        value = float(element_text)
    except ValueError:
        raise InvalidPrimitiveValue('Invalid float value: {}'.format(element_text))

    return value


def _parse_int(element_text):
    """Parses the raw XML string as an integer value"""
    try:
        value = int(element_text)
    except ValueError:
        raise InvalidPrimitiveValue('Invalid integer value: {}'.format(element_text))

    return value

def _parse_string(strip_whitespace):
    """Returns a parser function for parsing string values"""
    def _parse_string_value(element_text):
        if strip_whitespace:
            value = element_text.strip()
        else:
            value = element_text

        return value

    return _parse_string_value
