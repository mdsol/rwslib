# -*- coding: utf-8 -*-
__author__ = 'isparks'

from rwslib.builders import *

def example_clinical_data():
    """Test demonstrating building clinical data"""
    odm = ODM("test system")
    cd = ClinicalData("Mediflex", "DEV")
    subject_data = SubjectData("MDSOL", "New Subject", "Insert")


    sed = StudyEventData("SUBJECT")


    fd = FormData("EN", transaction_type="Update")

    igd = ItemGroupData()

    odm << cd << subject_data << sed << fd << igd

    item1 = ItemData("SUBJINIT", "AAA")
    item2 = ItemData("SUBJID", '001')

    igd << item1
    igd << item2


    odm = ODM("test system")(
       ClinicalData("Mediflex", "DEV")(
          SubjectData("MDSOL", "New Subject", "Insert")(
             StudyEventData("Subject")(
                FormData("EN", transaction_type="Update")(
                   ItemGroupData()(
                      ItemData("SUBJINIT", "AAA"),
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
            Symbol()(TranslatedText("en", "Kilograms"))
        ),
        MeasurementUnit("CM", "Centimeters")(
            Symbol()(TranslatedText("en", "Centimeters"))
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
    protocol << StudyEventRef("FLDR2", 2, False) # Order 2, Not Mandatory
    protocol << StudyEventRef("AE", 3, True)

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
    dm_form << ItemGroupRef("DM_ItemGroup1", 1)
    dm_form << ItemGroupRef("DM_ItemGroup2", 2)

    # Add to metadata
    meta << dm_form

    return odm

if __name__ == '__main__':
    #print str(example_clinical_data())
    #print str(example_metadata())
    projectname = 'TESTSTUDY'

    odm_definition = example_metadata(projectname, "Draft1")
    print str(odm_definition)

    #print str(odm_definition).partition("?>")[2]
    from rwslib import RWSConnection
    from rwslib.rws_requests import PostMetadataRequest
    from _settings import accounts
    account = accounts['innovate']
    r = RWSConnection('innovate', account['username'], account['password'])
    response = r.send_request(PostMetadataRequest(projectname, str(odm_definition)))
    print(str(response))