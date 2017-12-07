# builders

This package assists in the building of CDISC ODM (with Medidata Extensions where applicable)

## Organisation
The package is broken down by the logical arrangement of the ODM document itself.

* [common.py](common.py) - common elements, functions that are reused across the module
* [core.py](core.py) -  the ODM parent element
* [metadata.py](metadata.py) - metadata elements, starting with the Study Element
* [clinicaldata.py](clinicaldata.py) - clinical data elements, starting with the ClinicalData Element
* [admindata.py](admindata.py) - Administrative Data elements, starting with the AdminData Element
* [constants.py](constants.py) - Constants such as enumerated lists of options for Type elements (as an example)