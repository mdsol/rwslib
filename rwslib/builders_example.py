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

    item1 = ItemData("SUBJINIT","AAA")
    item2 = ItemData("SUBJID",'001')

    igd << item1
    igd << item2


    odm = ODM("test system")(
       ClinicalData("Mediflex","DEV")(
          SubjectData("MDSOL","New Subject", "Insert")(
             StudyEventData("Subject")(
                FormData("EN", transaction_type="Update")(
                   ItemGroupData()(
                      ItemData("SUBJINIT","AAA"),
                      ItemData("SUBJID",'001')
                   )
                )
             )
          )
       )
    )
    return odm

def example_metadata():
    """Example of building a metadata doc"""
    odm = ODM("SYSTEM_NAME")

    study = Study("TESTSTUDY", project_type="Project") #Could also be a global library

    # Push study element into odm
    odm << study

    # Create global variables and set them into study.
    study << GlobalVariables("TESTSTUDY") #Expected that protocol name will match the Study OID.

    # Create some basic definitions
    bd = BasicDefinitions()

    # Add some measurement units to the basic definitions. This time using the call () syntax:
    bd(
        MeasurementUnit("KG","Kilograms")(
            Symbol()(TranslatedText("en","Kilograms"))
        ),
        MeasurementUnit("CM","Centimeters")(
            Symbol()(TranslatedText("en","Centimeters"))
        )
    )

    # Add basic definitions to study
    study << bd


    # Now metadata which will contain all our form and field defs eventually
    meta = MetaDataVersion('META1','Draft1') #Note that Draft1 becomes our draft name in Rave.
    study << meta

    # Protocol contains StudyEventRefs
    protocol = Protocol()
    # Add some StudyEventRefs
    protocol << StudyEventRef("Folder1",1,True)  # Order 1, Mandatory
    protocol << StudyEventRef("Folder1",2,False) # Order 2, Not Mandatory

    meta << protocol

    # Next we'd start adding forms, etc. Patience !

    return odm




if __name__ == '__main__':
    #print str(example_clinical_data())
    print str(example_metadata())
