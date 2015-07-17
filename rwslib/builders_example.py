__author__ = 'isparks'

from rwslib.builders import *

from lxml.builder import E

if __name__ == '__main__':
    odm = ODM("test system")
    cd = ClinicalData("Mediflex", "DEV")
    subject_data = SubjectData("MDSOL", "New Subject", "Insert")


    sed = StudyEventData("SUBJECT")


    fd = FormData("EN", transaction_type="Update")

    igd = ItemGroupData()

    odm << cd << subject_data << sed << fd << igd

    item1 = ItemData("SUBJINIT","AAA")
    item2 = ItemData("SUBJID",001)

    igd << item1
    igd << item2


    odm = ODM("test system")(
       ClinicalData("Mediflex","DEV")(
          SubjectData("MDSOL","New Subject", "Insert")(
             StudyEventData("Subject")(
                FormData("EN", transaction_type="Update")(
                   ItemGroupData()(
                      ItemData("SUBJINIT","AAA"),
                      ItemData("SUBJID",001)
                   )
                )
             )
          )
       )
    )

    root = odm.getroot()
    print(str(odm))


