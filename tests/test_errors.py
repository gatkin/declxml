"""Tests for error messages"""
import pytest

import declxml as xml


_PROCESSOR = xml.dictionary('genre-authors', [
    xml.string('genre'),
    xml.array(xml.dictionary('author', [
        xml.string('name'),
        xml.integer('birth-year'),
        xml.array(xml.dictionary('book', [
            xml.string('title'),
            xml.integer('year-published')
        ]), alias='books')
    ]), alias='authors')
])


def test_parse_error_message():
    """Tests receiving parse error messages"""
    xml_string = """
    <genre-authors>
        <genre>Science Fiction</genre>
        <author>
            <name>Robert A. Heinlein</name>
            <birth-year>1907</birth-year>
            <book>
                <title>Starship Troopers</title>
                <year-published>1959</year-published>
            </book>
            <book>
                <title>Stranger in a Strange Land</title>
                <year-published>1961</year-published>
            </book>
        </author>
        <author>
            <name>Isaac Asimov</name>
            <birth-year>1920</birth-year>
            <book>
                <title>I, Robot</title>
            </book>
            <book>
                <title>Foundation</title>
                <year-published>1951</year-published>
            </book>
        </author>
    </genre-authors>
    """

    expected_message = 'genre-authors>authors>author[1]>books>book[0]>year-published'

    with pytest.raises(xml.MissingValue) as exception_info:
        xml.parse_from_string(_PROCESSOR, xml_string)

    actual_message = exception_info.value.message
    assert actual_message.endswith(expected_message)


def test_serialize_error_message():
    """Tests receiving serialize error messages"""
    author_data = {
        'genre': 'Science Fiction',
        'authors': [
            {
                'name': 'Robert A. Heinlein',
                'birth-year': 1907,
                'books': [
                    {
                        'title': 'Starship Troopers',
                        'year-published': 1959
                    },
                    {
                        'year-published': 1961
                    }
                ],
            },
            {
                'name': 'Isaac Asimov',
                'birth-year': 1920,
                'books': [
                    {
                        'title': 'I, Robot',
                        'year-published': 1950
                    },
                    {
                        'title': 'Foundation',
                        'year-published': 1951
                    }],
            }],
        }

    expected_message = 'authors>author[0]>books>book[1]>title'

    with pytest.raises(xml.MissingValue) as exception_info:
        xml.serialize_to_string(_PROCESSOR, author_data)

    actual_message = exception_info.value.message
    assert actual_message.endswith(expected_message)
