
.. index:: using_builders

.. _using_builders:

Using Builders
**************

Creating ODM messages by hand can be difficult. The builders package provides a simple API for generating these
ODM documents.

Here is an example of an ODM message to create a subject and update two values in the Enrollment default form for
this study.

.. code-block:: xml

    <?xml version="1.0" encoding="utf-8" ?>
    <ODM CreationDateTime="2013-06-17T18:49:28" FileOID="45b854a7-e170-4ff6-8ce5-f511d72688cb"
         FileType="Transactional" ODMVersion="1.3"
         Originator="test system"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
      <ClinicalData MetaDataVersionOID="1" StudyOID="Mediflex (DEV)">
        <SubjectData SubjectKey="New Subject" TransactionType="Insert">
          <SiteRef LocationOID="MDSOL" />
          <StudyEventData StudyEventOID="SUBJECT">
            <FormData FormOID="EN" TransactionType="Update">
              <ItemGroupData ItemGroupOID="EN" mdsol:Submission="SpecifiedItemsOnly">
                <ItemData ItemOID="SUBJID" Value="1" />
                <ItemData ItemOID="SUBJINIT" Value="AAA" />
              </ItemGroupData>
            </FormData>
          </StudyEventData>
        </SubjectData>
      </ClinicalData>
    </ODM>

This ODM file can be created using builders with this python code::

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
    >>> #Get an lxml document from the ODM object for further manipulation
    >>> root = odm.getroot()
    >>>
    >>> #Print a string representation of the ODM document
    >>> print(str(odm))
    <?xml version="1.0" encoding="utf-8" ?>
    <ODM CreationDateTime="2013-06-17T18:49:28" FileOID="45b854a7-e170-4ff6-8ce5-f511d72688cb"
         FileType="Transactional" ODMVersion="1.3" Originator="test system"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
      <ClinicalData MetaDataVersionOID="1" StudyOID="Mediflex (DEV)">
        <SubjectData SubjectKey="New Subject" TransactionType="Insert">
          <SiteRef LocationOID="MDSOL" />
          <StudyEventData StudyEventOID="SUBJECT">
            <FormData FormOID="EN" TransactionType="Update">
              <ItemGroupData ItemGroupOID="EN" mdsol:Submission="SpecifiedItemsOnly">
                <ItemData ItemOID="SUBJID" Value="1" />
                <ItemData ItemOID="SUBJINIT" Value="AAA" />
              </ItemGroupData>
            </FormData>
          </StudyEventData>
        </SubjectData>
      </ClinicalData>
    </ODM>

Builders also allow you to create the elements in stages and "pipeline" them together to create the document. The
following example creates the same document as above::

    >>> from rwslib.builders import *
    >>>
    >>> #Make a root ODM element with originator system
    >>> odm = ODM("test system")
    >>>
    >>> #Study and environment
    >>> clinical_data = ClinicalData("Mediflex", "DEV")
    >>>
    >>> #Subject Site, Subject Name and the transaction type
    >>> subject_data = SubjectData("MDSOL", "New Subject", "Insert")
    >>>
    >>> #The special "SUBJECT" event represents subject-level forms
    >>> event_data = StudyEventData("SUBJECT")
    >>>
    >>> #We want to update this form that will be created automatically when subject created
    >>> form_data = FormData("EN", transaction_type="Update")
    >>>
    >>> #We need an ItemGroupData element
    >>> itemgroup = ItemGroupData()
    >>>
    >>> #Push itemdata elements into the itemgroup
    >>> itemgroup << ItemData("SUBJINIT","AAA")
    >>> itemgroup << ItemData("SUBJID",001)
    >>>
    >>> #Now we put it all together
    >>> odm << clinical_data << subject_data << event_data << form_data << itemgroup
    >>>
    >>> #Get an lxml document from the ODM object for further manipulation
    >>> root = odm.getroot()
    >>>
    >>> #Print a string representation of the ODM document
    >>> print(str(odm))
    <?xml version="1.0" encoding="utf-8" ?>
    <ODM CreationDateTime="2013-06-17T18:49:28" FileOID="45b854a7-e170-4ff6-8ce5-f511d72688cb"
         FileType="Transactional" ODMVersion="1.3" Originator="test system"
         xmlns="http://www.cdisc.org/ns/odm/v1.3" xmlns:mdsol="http://www.mdsol.com/ns/odm/metadata">
      <ClinicalData MetaDataVersionOID="1" StudyOID="Mediflex (DEV)">
        <SubjectData SubjectKey="New Subject" TransactionType="Insert">
          <SiteRef LocationOID="MDSOL" />
          <StudyEventData StudyEventOID="SUBJECT">
            <FormData FormOID="EN" TransactionType="Update">
              <ItemGroupData ItemGroupOID="EN" mdsol:Submission="SpecifiedItemsOnly">
                <ItemData ItemOID="SUBJID" Value="1" />
                <ItemData ItemOID="SUBJINIT" Value="AAA" />
              </ItemGroupData>
            </FormData>
          </StudyEventData>
        </SubjectData>
      </ClinicalData>
    </ODM>

The builder creates a number of ODM properties including CreationDateTime, FileOID (a random identifier), FileType and
all namespace declarations.

