# -*- coding: utf-8 -*-

__author__ = 'anewbigging'

import datetime
import hashlib
from lxml import etree
from faker import Factory
from rwslib.extras.rwscmd.odmutils import E_ODM, A_ODM

fake = Factory.create()


def typeof_rave_data(value):
    """Function to duck-type values, not relying on standard Python functions because, for example,
    a string of '1' should be typed as an integer and not as a string or float
    since we're trying to replace like with like when scrambling."""

    # Test if value is a date
    for format in ['%d %b %Y', '%b %Y', '%Y', '%d %m %Y', '%m %Y', '%d/%b/%Y', '%b/%Y', '%d/%m/%Y', '%m/%Y']:
        try:
            datetime.datetime.strptime(value, format)
            if len(value) == 4 and (int(value) < 1900 or int(value) > 2030):
                break
            return ('date', format)
        except ValueError:
            pass
        except TypeError:
            pass

    # Test if value is a time
    for format in ['%H:%M:%S', '%H:%M', '%I:%M:%S', '%I:%M', '%I:%M:%S %p', '%I:%M %p']:
        try:
            datetime.datetime.strptime(value, format)
            return ('time', format)
        except ValueError:
            pass
        except TypeError:
            pass

    # Test if value is a integer
    try:
        if ((isinstance(value, str) and isinstance(int(value), int)) \
                    or isinstance(value, int)):
            return ('int', None)
    except ValueError:
        pass
    except TypeError:
        pass

    # Test if value is a float
    try:
        float(value)
        return ('float', None)
    except ValueError:
        pass
    except TypeError:
        pass

    # If no match on anything else, assume its a string
    return ('string', None)


class Scramble():
    def __init__(self, metadata=None):
        # If initialized with metadata, store relevant formats and lookup information
        if metadata:
            self.metadata = etree.fromstring(metadata)
        else:
            self.metadata = None

    def scramble_int(self, length):
        """Return random integer up to specified number of digits"""
        return str(fake.random_number(length))

    def scramble_float(self, length, sd=0):
        """Return random float in specified format"""
        if sd == 0:
            return str(fake.random_number(length))
        else:
            return str(fake.pyfloat(length - sd, sd, positive=True))

    def scramble_date(self, value, format='%d %b %Y'):
        """Return random date """
        # faker method signature changed
        if value == '':
            # handle the empty string by defaulting to 'now' and 1 year ago
            end_date = 'now'
            start_date = '-1y'
        else:
            # specified end date, and one year prior
            end_date = datetime.datetime.strptime(value, format).date()
            start_date = end_date - datetime.timedelta(days=365)
        fake_date = fake.date_time_between(start_date=start_date,
                                           end_date=end_date).strftime(format).upper()
        return fake_date

    def scramble_time(self, format='%H:%M:%S'):
        """Return random time"""
        return fake.time(pattern=format)

    def scramble_string(self, length):
        """Return random string"""
        return fake.text(length) if length > 5 else ''.join([fake.random_letter() for n in range(0, length)])

    def scramble_value(self, value):
        """Duck-type value and scramble appropriately"""
        try:
            type, format = typeof_rave_data(value)
            if type == 'float':
                i, f = value.split('.')
                return self.scramble_float(len(value) - 1, len(f))
            elif type == 'int':
                return self.scramble_int(len(value))
            elif type == 'date':
                return self.scramble_date(value, format)
            elif type == 'time':
                return self.scramble_time(format)
            elif type == 'string':
                return self.scramble_string(len(value))
            else:
                return value
        except:
            return ""

    def scramble_subjectname(self, value):
        """Scramble subject name with a consistent one-way hash"""
        # md5 will give a consistent obscured value.
        # TODO:  pattern match the subjectname and string replace?
        # TODO:  leave 'New Subject' un-encoded?
        md5 = hashlib.md5(value)
        return md5.hexdigest()

    def scramble_codelist(self, codelist):
        """Return random element from code list"""
        # TODO:  External code lists
        path = ".//{0}[@{1}='{2}']".format(E_ODM.CODELIST.value, A_ODM.OID.value, codelist)
        elem = self.metadata.find(path)
        codes = []
        for c in elem.iter(E_ODM.CODELIST_ITEM.value):
            codes.append(c.get(A_ODM.CODED_VALUE.value))
        for c in elem.iter(E_ODM.ENUMERATED_ITEM.value):
            codes.append(c.get(A_ODM.CODED_VALUE.value))

        return fake.random_element(codes)

    def scramble_itemdata(self, oid, value):
        """If metadata provided, use it to scramble the value based on data type"""
        if self.metadata is not None:
            path = ".//{0}[@{1}='{2}']".format(E_ODM.ITEM_DEF.value, A_ODM.OID.value, oid)
            elem = self.metadata.find(path)
            # for elem in self.metadata.iter(E_ODM.ITEM_DEF.value):
            datatype = elem.get(A_ODM.DATATYPE.value)

            codelist = None
            for el in elem.iter(E_ODM.CODELIST_REF.value):
                codelist = el.get(A_ODM.CODELIST_OID.value)

            length = 1 if not A_ODM.LENGTH in elem else int(elem.get(A_ODM.LENGTH.value))

            if A_ODM.SIGNIFICANT_DIGITS.value in elem.keys():
                sd = elem.get(A_ODM.SIGNIFICANT_DIGITS.value)
            else:
                sd = 0

            if A_ODM.DATETIME_FORMAT.value in elem.keys():
                dt_format = elem.get(A_ODM.DATETIME_FORMAT.value)
                for fmt in [('yyyy', '%Y'), ('MMM', '%b'), ('dd', '%d'), ('HH', '%H'), ('nn', '%M'), ('ss', '%S'),
                            ('-', '')]:
                    dt_format = dt_format.replace(fmt[0], fmt[1])

            if codelist is not None:
                return self.scramble_codelist(codelist)

            elif datatype == 'integer':
                return self.scramble_int(length)

            elif datatype == 'float':
                return self.scramble_float(length, sd)

            elif datatype in ['string', 'text']:
                return self.scramble_string(length)

            elif datatype in ['date', 'datetime']:
                return self.scramble_date(value, dt_format)

            elif datatype in ['time']:
                return self.scramble_time(dt_format)

            else:
                return self.scramble_value(value)

        else:
            return self.scramble_value(value)

    def scramble_query_value(self, value):
        """Return random text for query"""
        return self.scramble_value(value)

    def fill_empty(self, fixed_values, input):
        """Fill in random values for all empty-valued ItemData elements in an ODM document"""
        odm_elements = etree.fromstring(input)

        for v in odm_elements.iter(E_ODM.ITEM_DATA.value):
            if v.get(A_ODM.VALUE.value) == "":
                oid = v.get(A_ODM.ITEM_OID.value)

                if fixed_values is not None and oid in fixed_values:
                    d = fixed_values[oid]
                else:
                    d = self.scramble_itemdata(v.get(A_ODM.ITEM_OID.value), v.get(A_ODM.VALUE.value))

                v.set(A_ODM.VALUE.value, d)
            else:
                # Remove ItemData if it already has a value
                v.getparent().remove(v)

        # Remove empty ItemGroupData elements
        for v in odm_elements.iter(E_ODM.ITEM_GROUP_DATA.value):
            if len(v) == 0:
                v.getparent().remove(v)

        # Remove empty FormData elements
        for v in odm_elements.iter(E_ODM.FORM_DATA.value):
            if len(v) == 0:
                v.getparent().remove(v)

        # Remove empty StudyEventData elements
        for v in odm_elements.iter(E_ODM.STUDY_EVENT_DATA.value):
            if len(v) == 0:
                v.getparent().remove(v)

        return etree.tostring(odm_elements)
