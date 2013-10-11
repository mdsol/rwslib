.. _post_clinical_data:

Posting Clinical Data
*********************

Creating or updating subject data in Rave is managed via the post_data method to RWS.


.. _post_data:
.. index:: PostDataRequest

PostDataRequest(odm_data)
-------------------------

Authorization is required for this method.

Returns a :class:`rwsobjects.RWSPostResponse` object which has attributes that report on the changes made and new counts of subjects
in the study. On failure, raises an exception with a RWSPostErrorResponse attached in the error attribute that reports
on the full source of the error as reported by RWS.

Calls::

    https://{{ host }}/RaveWebServices/webservice.aspx?PostODMClinicalData

Options:

+------------------------------------------+--------------------------------------------------------------------------+
| Option                                   | Description                                                              |
+==========================================+==========================================================================+
| headers={'Content-type': "text/xml"}     | Set custom headers. May need to provide a Content-type if your RWS       |
|                                          | version is set to accept different standard content-type than default.   |
+------------------------------------------+--------------------------------------------------------------------------+

Note that the content-type header that RWS will accept can be varied by configuration. The standard, default setting
is text/xml. You should not need to specify content_type in the normal case.

Example::

    >>> from rwslib import RWSConnection
    >>> from rwslib.rws_requests import PostDataRequest
    >>> r = RWSConnection('https://innovate.mdsol.com', 'username', 'password')  #Authorization required
    >>> data = """<?xml version="1.0" encoding="utf-8" ?>
    ... <ODM CreationDateTime="2013-06-17T17:03:29"
    ...      FileOID="3b9fea8b-e825-4e5f-bdc8-1464bdd7a664" FileType="Transactional"
    ...      ODMVersion="1.3" Originator="test system"
    ...      xmlns="http://www.cdisc.org/ns/odm/v1.3"
    ...      xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
    ...   <ClinicalData MetaDataVersionOID="1" StudyOID="Mediflex (DEV)">
    ...     <SubjectData SubjectKey="New Subject" TransactionType="Insert">
    ...       <SiteRef LocationOID="MDSOL" />
    ...       <StudyEventData StudyEventOID="SUBJECT">
    ...         <FormData FormOID="EN" FormRepeatKey="1" TransactionType="Update">
    ...           <ItemGroupData ItemGroupOID="EN" mdsol:Submission="SpecifiedItemsOnly">
    ...             <ItemData ItemOID="SUBJID" Value="1" />
    ...             <ItemData ItemOID="SUBJINIT" Value="AAA" />
    ...           </ItemGroupData>
    ...         </FormData>
    ...       </StudyEventData>
    ...     </SubjectData>
    ...   </ClinicalData>
    ... </ODM>"""
    >>> resp = r.send_request(PostDataRequest(data))
    >>> resp.istransactionsuccessful
    True
    >>> resp.fields_touched
    2
    >>> str(resp)
    <Response ReferenceNumber="ebb3dfc7-fca6-4872-84b4-f0942cd66ce7"
              InboundODMFileOID="3b9fea8b-e825-4e5f-bdc8-1464bdd7a664" IsTransactionSuccessful="1"
              SuccessStatistics="Rave objects touched: Subjects=1; Folders=0; Forms=0; Fields=2; LogLines=0"
              NewRecords=""
              SubjectNumberInStudy="1103"
              SubjectNumberInStudySite="55"/>

Using Builders
--------------

Creating ODM strings can be error prone, especially when dealing with XML entities such as &gt; &lt; &amp; etc. rwslib
provides the :mod:`builders` module to help build ODM documents using python syntax.

The ODM from the example above could be generated using the builder vocabulary::

    >>> from rwslib.builders import *
    >>> odm = ODM("test system")(
    ...   ClinicalData("Mediflex","DEV")(
    ...      SubjectData("MDSOL","New Subject", "Insert")(
    ...         StudyEventData("Subject")(
    ...            FormData("EN", transaction_type="Update")(
    ...               ItemGroupData()(
    ...                  ItemData("SUBJINIT","AAA"),
    ...                  ItemData("SUBJID",001)
    ...               )
    ...            )
    ...         )
    ...      )
    ...   )
    ... )
    >>> str(odm) #Returns the string representation of the odm object and all it's children.

See :ref:`using_builders` for examples of using rwslib builder objects to create ODM messages.

