.. declxml documentation master file, created by
   sphinx-quickstart on Sat Sep  2 08:22:41 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

declxml - Declarative XML Processing
====================================

The declxml library provides a simple, declarative API for parsing and serializing XML documents.
For the most common and straightforward processing tasks, declxml aims to replace the need for writing
and maintaining dozens or hundreds of lines of imperitive serialization and parsing logic required when
using lower-level APIs such as ElementTree directly. The declxml library was inspired by the simplicity
and declaritive nature of Golang's XML processing library.

declxml works with *processors* which declaritively define the structure of the XML document.
Processors are used to both serialize and parse XML data as well as to perform a basic level of
validation.


.. toctree::
   :maxdepth: 2

   quickstart
   api
