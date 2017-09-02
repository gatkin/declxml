"""Contains helper functions forunit tests"""
import re


def strip_xml(xml_string):
    """Prepares the XML string so it can be compared to the actual serialized output"""
    # Strip internal whitespace between tags
    stripped = re.sub(r'>\s+<', '><', xml_string)

    # Strip external whitespace
    return stripped.strip().encode('utf8')
