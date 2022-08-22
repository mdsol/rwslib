Class Reference for Builders
****************************
Builders provide a way to construct an ODM XML document from  Python object.

.. note:: Any Class with the Prefix **Mdsol** represents a Medidata Rave specific extension

Metadata Builders
=================
Metadata Builders provide an API for creating ODM metadata elements

.. automodule:: rwslib.builders.metadata
    :members:
    :exclude-members: build

Clinical Data Builders
======================
Clinical Data Builders provide an API for creating ODM data elements

.. automodule:: rwslib.builders.clinicaldata
    :members:
    :exclude-members: build


Medidata Extensions to ODM (MODM) Builders
==========================================
MODM Builders provide an API for creating ODM data elements meeting the Medidata Rave specific extensions to the MODM specification

.. automodule:: rwslib.builders.clinicaldata
    :members:
    :exclude-members: build


Administrative Data Builders
============================
Admin Data Builders provide an API for creating ODM AdminData elements

.. automodule:: rwslib.builders.admindata
    :members:
    :exclude-members: build

