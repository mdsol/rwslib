# -*- coding: utf-8 -*-
__author__ = 'isparks'

from rwslib.builders import *

def example_clinical_data(study_name, environment):
    """Test demonstrating building clinical data"""

    odm = ODM("test system")(
       ClinicalData("Mediflex", "DEV")(
          SubjectData("MDSOL", "IJS TEST3", transaction_type="Insert")(
             StudyEventData("SUBJECT")(
                FormData("EN", transaction_type="Update")(
                   ItemGroupData()(
                      ItemData("SUBJINIT", "AAA")(
                            AuditRecord(edit_point=AuditRecord.EDIT_DATA_MANAGEMENT,
                                      used_imputation_method= False,
                                      identifier='X2011',
                                      include_file_oid=False)(
                                            UserRef("isparks"),
                                            LocationRef("MDSOL"),
                                            ReasonForChange("Data Entry Error"),
                                            DateTimeStamp(datetime(2015, 9, 11, 10, 15, 22, 80))
                            )
                      ),
                      ItemData("SUBJID", '001')
                   )
                )
             )
          )
       )
    )
    return odm


def example_metadata(study_name, draft_name):
    """Example of building a metadata doc"""
    odm = ODM("SYSTEM_NAME", filetype=ODM.FILETYPE_SNAPSHOT)

    study = Study(study_name, project_type=Study.PROJECT)

    # Push study element into odm
    odm << study

    # Create global variables and set them into study.
    study << GlobalVariables(study_name) #Expected that protocol name will match the Study OID.

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
    protocol << StudyEventRef("FLDR1", 1, True)  # Order 1, Mandatory
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
    dm_form << MdsolHelpText("en","Some help text for Demography")
    dm_form << MdsolViewRestriction('Data Manager')
    dm_form << MdsolEntryRestriction('Batch Upload')
    dm_form << ItemGroupRef("DM_IG1", 1)
    dm_form << ItemGroupRef("DM_IG2", 2)

    # Add to metadata
    meta << dm_form

    # Define item group
    meta << ItemGroupDef("DM_IG1", "DM Item Group 1")(
        MdsolLabelRef("LBL1", 1),
        ItemRef("SEX", 2)(
            MdsolAttribute("Standards","CDASH","SEX"),
            MdsolAttribute("Standards","STDNUMBER","1120")
        ),
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

    return odm

if __name__ == '__main__':
    from rwslib import RWSConnection
    from rwslib.rws_requests import PostMetadataRequest, PostDataRequest
    from _settings import accounts
    account = accounts['innovate']
    r = RWSConnection('innovate', account['username'], account['password'])


    if True: # MetaData
        projectname = 'TESTSTUDY'
        odm_definition = example_metadata(projectname, "Draft1")
        request = PostMetadataRequest(projectname, str(odm_definition))
    else: #Clinical Data
        projectname = 'Mediflex'
        odm_definition = example_clinical_data(projectname,"DEV")
        request = PostDataRequest(str(odm_definition))
    print str(odm_definition)

    response = r.send_request(request)
    print(str(response))