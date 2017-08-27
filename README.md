# declxml - Declarative XML Processing [![Build Status](https://travis-ci.org/gatkin/declxml.svg?branch=master)](https://travis-ci.org/gatkin/declxml)
The declxml library makes defining how data is transformed between XML and Python objects simple. Wrather than writing dozens or hundreds of lines of imperitive logic for serializing and parsing XML documents by hand with the ElementTree or minidom libraries, declxml enables you to simply define the data in your XML document using a declaritive syntax. This makes it easy to quickly implement XML parsers and serializers and allows XML document definitions to be easily extended.

For example, suppose we had some XML data on race results that we want to process
```xml
<running-season>
    <year>2017</year>
    <runner>
        <name>John Doe</name>
        <age>27</age>
        <gender>Male</gender>
    </runner>
    <race>
        <name>St Patrick's 10k</name>
        <distance units="kilometers">10</distance>
        <date>3/17/2017</date>
        <location>
            <city>Dublin</city>
            <country>Ireland</country>
        </location>
        <result>
            <place>51</place>
            <time units="seconds">2413</time>
        </result>
    </race>
    <race>
        <name>Boston Marathon</name>
        <distance units="miles">26.2</distance>
        <date>4/17/2017</date>
        <location>
            <city>Boston</city>
            <state>MA</state>
            <country>USA</country>
        </location>
        <result>
            <place>171</place>
            <time units="seconds">7200</time>
        </result>
    </race>
</running-season>
``` 

Defining an XML processer and using it to parse such documents is simple with declxml. The following example defines an XML processor that transforms race data to and from Python dictionaries.
```python
import declxml as xml

# Can specify aggregates in the XML by specifying the primitive values that
# make up the fields of the aggregate
runner_xml = xml.dictionary('runner', [
    xml.string('name'),  # decl XML fields are typed
    xml.integer('age'),
    xml.string('gender'),
])

location_xml = xml.dictionary('location', [
    xml.string('city'),
    xml.string('state', required=False),
    xml.string('country'),
])

result_xml = xml.dictionary('result', [
    xml.integer('place'),
    xml.integer('time'),
    xml.string('time', attribute='units', alias='time_units'),
])

# Processors can be composed with other processors to define the hierarchical
# structure of the XML document
race_xml = xml.dictionary('race', [
    xml.string('name'),
    xml.floating_point('distance'),
    xml.string('distance', attribute='units', alias='distance_units'),
    xml.string('date'),
    location_xml,
    result_xml
])

running_season_xml = xml.dictionary('running-season', [
    xml.integer('year'),
    runner_xml,
    xml.array(race_xml, alias='races')
])

races = xml.parse_xml_file('races.xml', running_season_xml)
print(races)
```

Parsing the above XML file would result in
```python
{   'year': 2017,
    'runner': {'age': 27, 'gender': 'Male', 'name': 'John Doe'},
    'races': [   {   'date': '3/17/2017',
                     'distance': 10.0,
                     'distance_units': 'kilometers',
                     'location': {   'city': 'Dublin',
                                     'country': 'Ireland',
                                     'state': ''},
                     'name': "St Patrick's 10k",
                     'result': {   'place': 51,
                                   'time': 2413,
                                   'time_units': 'seconds'}},
                 {   'date': '4/17/2017',
                     'distance': 26.2,
                     'distance_units': 'miles',
                     'location': {   'city': 'Boston',
                                     'country': 'USA',
                                     'state': 'MA'},
                     'name': 'Boston Marathon',
                     'result': {   'place': 171,
                                   'time': 7200,
                                   'time_units': 'seconds'}}],
}
```

The same processor can be used for serializing Python data structures as well
```python
races = xml.parse_xml_file('races.xml', running_season_xml)
races['year'] = 2018
xml.serialize_xml_file(running_season_xml, races, 'races_2018.xml')
```