API
====================================

Processors
---------------
The declxml library uses processors to define the structure of XML documents. Processors can be divided into two categories:
*primitve processors* and *aggregate processors*

Primitive Processors
----------------------
Primitive processors are used to parse and serialize simple, primitve values. The following module functions are used to construct
primitive processors:

.. autofunction:: declxml.boolean
.. autofunction:: declxml.floating_point
.. autofunction:: declxml.integer
.. autofunction:: declxml.string

Aggregate Processors
---------------------
Aggregate processors are composed of other processors. These processors are used for values such as dictionaries, arrays, and
user objects.

.. autofunction:: declxml.array
.. autofunction:: declxml.dictionary
.. autofunction:: declxml.user_object