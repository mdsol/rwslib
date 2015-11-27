
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
    >>> # Get an lxml document from the ODM object for further manipulation
    >>> root = odm.getroot()
    >>>
    >>> # Print a string representation of the ODM document
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
    >>> # Make a root ODM element with originator system
    >>> odm = ODM("test system")
    >>>
    >>> # Study and environment
    >>> clinical_data = ClinicalData("Mediflex", "DEV")
    >>>
    >>> # Subject Site, Subject Name and the transaction type
    >>> subject_data = SubjectData("MDSOL", "New Subject", "Insert")
    >>>
    >>> # The special "SUBJECT" event represents subject-level forms
    >>> event_data = StudyEventData("SUBJECT")
    >>>
    >>> # We want to update this form that will be created automatically when subject created
    >>> form_data = FormData("EN", transaction_type="Update")
    >>>
    >>> # We need an ItemGroupData element
    >>> itemgroup = ItemGroupData()
    >>>
    >>> # Push itemdata elements into the itemgroup
    >>> itemgroup << ItemData("SUBJINIT","AAA")
    >>> itemgroup << ItemData("SUBJID",001)
    >>>
    >>> # Now we put it all together
    >>> odm << clinical_data << subject_data << event_data << form_data << itemgroup
    >>>
    >>> # Get an lxml document from the ODM object for further manipulation
    >>> root = odm.getroot()
    >>>
    >>> # Print a string representation of the ODM document
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

## Metadata Builders

Builders also exist for creating Metadata ODM files::

    from rwslib.builders import *

    odm = ODM("SYSTEM_NAME", filetype=ODM.FILETYPE_SNAPSHOT)

    study_name = 'MyStudy'
    draft_name = 'Draft 1'

    study = Study(study_name, project_type=Study.PROJECT)

    # Push study element into odm
    odm << study

    # Create global variables and set them into study.
    study << GlobalVariables(study_name) # Expected that protocol name will match the Study OID.

    # Create some basic definitions
    bd = BasicDefinitions()

    # Add some measurement units to the basic definitions. This time using the call () syntax:
    bd(
        MeasurementUnit("KG", "Kilograms")(
            Symbol()(TranslatedText("Kilograms"))
        ),
        MeasurementUnit("CM", "Centimeters")(
            Symbol()(TranslatedText("Centimeters"))
        )
    )

    # Add basic definitions to study
    study << bd

    # Now metadata which will contain all our form and field defs eventually
    meta = MetaDataVersion('META1', draft_name)
    study << meta

    # Protocol contains StudyEventRefs
    protocol = Protocol()
    # Add some StudyEventRefs
    protocol << StudyEventRef("FLDR1", 1, True)    # Order 1, Mandatory
    # protocol << StudyEventRef("FLDR2", 2, False) # Order 2, Not Mandatory
    # protocol << StudyEventRef("AE", 3, True)

    meta << protocol

    # Add Study Event Defs with some child FormRefs
    fldr1 = StudyEventDef("FLDR1", "Folder 1", False, StudyEventDef.SCHEDULED)

    fldr1 << FormRef("DM", 1, True)
    fldr1 << FormRef("VS", 2, True)

    meta << fldr1

    meta << StudyEventDef("FLDR2", "Folder 2", False, StudyEventDef.UNSCHEDULED)(
        FormRef("VS", 1, True)
    )

    meta << StudyEventDef("AE", "Adverse Events", False, StudyEventDef.COMMON)(
        FormRef("AE", 1, False)
    )

    dm_form = FormDef("DM","Demography")
    dm_form << MdsolHelpText("en","Some help text for Demography form")
    dm_form << MdsolViewRestriction('Data Manager')
    dm_form << MdsolEntryRestriction('Batch Upload')
    dm_form << ItemGroupRef("DM_IG1", 1)
    dm_form << ItemGroupRef("DM_IG2", 2)

    # Add to metadata
    meta << dm_form

    # Define item group
    meta << ItemGroupDef("DM_IG1", "DM Item Group 1")(
        MdsolLabelRef("LBL1", 1),
        ItemRef("SEX", 2),
        ItemRef("RACE", 3),
        ItemRef("RACE_OTH", 4),
        ItemRef("DOB", 5),
        ItemRef("AGE", 6)
    )

    # Add the ItemDefs
    meta << ItemDef("SEX", "Gender", DATATYPE_TEXT, 1, control_type=ItemDef.CONTROLTYPE_RADIOBUTTON
       )(
        Question()(TranslatedText("Gender at Birth")),
        CodeListRef("CL_SEX")
    )
    meta << ItemDef("RACE", "Race", DATATYPE_TEXT, 2,
                    control_type=ItemDef.CONTROLTYPE_RADIOBUTTON_VERTICAL
                    )(
        Question()(TranslatedText("Race")),
        CodeListRef("CL_RACE")
    )
    meta << ItemDef("RACE_OTH", "RaceOther", DATATYPE_TEXT, 20) \
           << Question() << TranslatedText("If Race Other, please specify")

    meta << ItemDef("DOB", "DateOfBirth", DATATYPE_DATE, 10,
                    control_type=ItemDef.CONTROLTYPE_DATETIME,
                    date_time_format="dd/mm/yyyy"
                    )(
        Question()(TranslatedText("Date of Birth")),
        MdsolHelpText("en","If month unknown, enter January")
    )

    meta << ItemDef("AGE", "Age in Years", DATATYPE_INTEGER, 4, significant_digits=3, control_type=ItemDef.CONTROLTYPE_TEXT
       )(
        Question()(TranslatedText("Age in Years")),
        RangeCheck(RangeCheck.GREATER_THAN_EQUAL_TO, RangeCheck.SOFT) (
            CheckValue("18")
        ),
        RangeCheck(RangeCheck.LESS_THAN_EQUAL_TO, RangeCheck.SOFT) (
            CheckValue("65")
        )
    )

    # Add a Label
    meta.add(MdsolLabelDef("LBL1", "Label1")(TranslatedText("Please answer all questions.")))

    # As well as () and << you can use add()
    meta.add(
        CodeList("CL_SEX", "SEX", datatype=DATATYPE_TEXT)(
            CodeListItem("M").add(
                Decode().add(
                    TranslatedText("Male"))
            ),
            CodeListItem("F").add(
                Decode().add(
                    TranslatedText("Female"))
            ),
        ),
        CodeList("CL_RACE", "RACE", datatype=DATATYPE_TEXT)(
            CodeListItem("Y")(Decode()(TranslatedText("Yes"))),
            CodeListItem("N")(Decode()(TranslatedText("No"))),
        )
    )

    # Get an lxml document from the ODM object for further manipulation
    root = odm.getroot()

    # Print a string representation of the ODM document
    print(str(odm))



