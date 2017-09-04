# -*- coding: utf-8 -*-

from rwslib.builders.common import ODMElement, dt_to_iso8601
from rwslib.builders.clinicaldata import LocationRef
from rwslib.builders.constants import LocationType, UserType
from rwslib.builders.modm import LastUpdateMixin


class AdminData(ODMElement):
    """
    Administrative information about users, locations, and electronic signatures.
    """
    def __init__(self, study_oid=None):
        """
        :param str study_oid: OID pointing to the StudyDef
        """
        super(AdminData, self).__init__()
        self.study_oid = study_oid
        self.users = []
        self.locations = []
        # SignatureDef

    def build(self, builder):
        """Build XML by appending to builder"""
        params = {}
        if self.study_oid:
            params.update(dict(StudyOID=self.study_oid))
        builder.start("AdminData", params)
        for user in self.users:
            user.build(builder)
        for location in self.locations:
            location.build(builder)

        builder.end("AdminData")

    def __lshift__(self, other):
        """Override << operator"""

        if not isinstance(other, (User, Location,)):
            raise ValueError('{0} cannot accept a {1} as a child element'.format(self.__class__.__name__,
                                                                                 other.__class__.__name__))

        self.set_list_attribute(other, User, 'users')
        self.set_list_attribute(other, Location, 'locations')

        return other


class MetaDataVersionRef(ODMElement):
    """
    A reference to a MetaDataVersion used at the containing Location. 
      The EffectiveDate expresses the fact that the metadata used at a location can vary over time.
    """
    def __init__(self, study_oid, metadata_version_oid, effective_date):
        """
        :param str study_oid: References the :class:`Study` that uses this metadata version.
        :param str metadata_version_oid: References the :class:`rwslib.builders.MetaDataVersion` (within the above Study).
        :param datetime.datetime effective_date: Effective Date for this version and Site
        """
        super(MetaDataVersionRef, self).__init__()
        self.study_oid = study_oid
        self.metadata_version_oid = metadata_version_oid
        self.effective_date = effective_date

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(StudyOID=self.study_oid,
                      MetaDataVersionOID=self.metadata_version_oid,
                      EffectiveDate=dt_to_iso8601(self.effective_date))
        builder.start("MetaDataVersionRef", params)
        builder.end("MetaDataVersionRef")


class Location(ODMElement, LastUpdateMixin):
    """
    A physical location -- typically a clinical research site or a sponsor's office.
    """
    def __init__(self, oid, name,
                 location_type=None,
                 metadata_versions=None):
        """
        :param str oid: OID for the Location, referenced in :class:`LocationRef`
        :param str name: Name for the Location
        :param rwslib.builder_constants.LocationType location_type: Type for this Location
        :param list(MetaDataVersionRef) metadata_versions: The :class:`MetaDataVersionRef` for this Location
        """
        super(Location, self).__init__()
        self.oid = oid
        self.name = name
        self._location_type = None
        if location_type:
            self.location_type = location_type
        self.metadata_versions = []
        if metadata_versions:
            if isinstance(metadata_versions, (tuple, list)):
                for mdv in metadata_versions:
                    self << mdv
            elif isinstance(metadata_versions, (MetaDataVersionRef,)):
                self << metadata_versions

    @property
    def location_type(self):
        return self._location_type

    @location_type.setter
    def location_type(self, value):
        if not isinstance(value, (LocationType,)):
            raise ValueError("{} is not a LocationType".format(type(value)))
        self._location_type = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid,
                      Name=self.name)
        if self.location_type:
            params.update(dict(LocationType=self.location_type.value))
        # mixins
        self.mixin()
        self.mixin_params(params)
        builder.start("Location", params)
        for mdv in self.metadata_versions:
            mdv.build(builder)
        builder.end("Location")

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (MetaDataVersionRef,)):
            raise ValueError('{0} cannot accept a {1} as a child element'.format(self.__class__.__name__,
                                                                                 other.__class__.__name__))

        self.set_list_attribute(other, MetaDataVersionRef, 'metadata_versions')

        return other


class Address(ODMElement):
    """
    The user's postal address.
    """
    def __init__(self, street_names=None, city=None, state_prov=None, country=None, postal_code=None, other_text=None):
        """
        :param list(Address) street_names: User street names 
        :param City city: User City
        :param StateProv state_prov: User State or Provence
        :param Country country: User City
        :param PostalCode postal_code: User City
        :param OtherText other_text: User Other Text
        """
        super(Address, self).__init__()
        self.street_names = street_names or []
        self.city = city
        self.state_prov = state_prov
        self.country = country
        self.postal_code = postal_code
        self.other_text = other_text

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict()
        builder.start(self.__class__.__name__, params)
        for street in self.street_names:
            street.build(builder)
        # build the children
        for child in ('city', 'country', 'state_prov', 'postal_code', 'other_text'):
            if getattr(self, child) is not None:
                getattr(self, child).build(builder)
        builder.end(self.__class__.__name__)

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (StreetName, City, StateProv, Country, PostalCode, OtherText,)):
            raise ValueError('{0} cannot accept a {1} as a child element'.format(self.__class__.__name__,
                                                                                 other.__class__.__name__))
        self.set_list_attribute(other, StreetName, 'street_names')
        self.set_single_attribute(other, Country, 'country')
        self.set_single_attribute(other, City, 'city')
        self.set_single_attribute(other, StateProv, 'state_prov')
        self.set_single_attribute(other, PostalCode, 'postal_code')
        self.set_single_attribute(other, OtherText, 'other_text')
        return other


class User(ODMElement):
    """
    Information about a specific user of a clinical data collection system. This may be an investigator, a CRA, or 
      data management staff. Study subjects are not users in this sense.
    """

    def __init__(self, oid, user_type=None, login_name=None, display_name=None, full_name=None,
                 first_name=None, last_name=None,
                 organisation=None, addresses=[], emails=[], phones=[], locations=[]):
        """
        :param str oid: 
        :param rwslib.builder_constants.UserType user_type: User Type
        :param LoginName login_name: User Login Name - see :class:`LoginName`
        :param DisplayName display_name: User Display Name - see :class:`DisplayName`
        :param FullName full_name: User Full Name - see :class:`FullName` 
        :param FirstName first_name: User First Name - see :class:`FirstName`
        :param LastName last_name: User Last Name - see :class:`LastName`
        :param Organisation organisation: User Organisation - see :class:`Organisation`
        :param list(Address) addresses: User Address - see :class:`Address`
        :param list(Email) emails: User Email - see :class:`Email`
        :param list(Phone) phones: User Phone - see :class:`Phone`
        :param list(LocationRef) locations: Locations for User - see :class:`LocationRef`
        """
        super(User, self).__init__()
        self.login_name = login_name
        self.display_name = display_name
        self.full_name = full_name
        self.first_name = first_name
        self.last_name = last_name
        self.organisation = organisation
        self.addresses = addresses
        self.emails = emails
        self.phones = phones
        self.locations = locations
        self._user_type = None
        if user_type:
            self.user_type = user_type
        self.oid = oid

    @property
    def user_type(self):
        """
        User Type
        :return: 
        """
        return self._user_type

    @user_type.setter
    def user_type(self, value):
        if not isinstance(value, (UserType,)):
            raise ValueError("{} is not a UserType".format(type(value)))
        self._user_type = value

    def build(self, builder):
        """Build XML by appending to builder"""
        params = dict(OID=self.oid)
        if self.user_type:
            params.update(dict(UserType=self.user_type.value))
        builder.start(self.__class__.__name__, params)
        # build the children
        for child in ('login_name', 'display_name', 'full_name', 'first_name', 'last_name',
                      'organisation'):
            if getattr(self, child) is not None:
                getattr(self, child).build(builder)
        for address in self.addresses:
            address.build(builder)
        for email in self.emails:
            email.build(builder)
        for phone in self.phones:
            phone.build(builder)
        for location in self.locations:
            location.build(builder)
        builder.end(self.__class__.__name__)

    def __lshift__(self, other):
        """Override << operator"""
        if not isinstance(other, (LoginName, DisplayName, FullName, FirstName, LastName, Organization,
                                  Address, Email, Phone, LocationRef)):
            raise ValueError('{0} cannot accept a {1} as a child element'.format(self.__class__.__name__,
                                                                                 other.__class__.__name__))
        self.set_list_attribute(other, Email, 'emails')
        self.set_list_attribute(other, Address, 'addresses')
        self.set_list_attribute(other, LocationRef, 'locations')
        self.set_list_attribute(other, Phone, 'phones')
        self.set_single_attribute(other, LoginName, 'login_name')
        self.set_single_attribute(other, DisplayName, 'display_name')
        self.set_single_attribute(other, FullName, 'full_name')
        self.set_single_attribute(other, FirstName, 'first_name')
        self.set_single_attribute(other, LastName, 'last_name')
        self.set_single_attribute(other, Organization, 'organisation')
        return other


class SimpleChildElement(ODMElement):
    """
    Generic Element, for elements we're not ready to flesh out in the builders
    """
    def __init__(self, text):
        self.text = text

    def build(self, builder):
        """
        Build the element
        :param builder: 
        :return: 
        """
        builder.start(self.__class__.__name__)
        builder.data(self.text)
        builder.end(self.__class__.__name__)


class LoginName(SimpleChildElement):
    """
    The user's login identification.
    """


class DisplayName(SimpleChildElement):
    """
    A short displayable name for the user.
    """


class FullName(SimpleChildElement):
    """
    The user's full formal name.
    """


class FirstName(SimpleChildElement):
    """
    The user's initial given name or all given names.
    """


class LastName(SimpleChildElement):
    """
    The user's surname (family name).
    """


class Organization(SimpleChildElement):
    """
    The user's organization.
    """


class Email(SimpleChildElement):
    """
    The user's email address.
    """


class Phone(SimpleChildElement):
    """
    The user's voice phone number.
    """


class StreetName(SimpleChildElement):
    """
    The street address part of a user's postal address.
    """


class City(SimpleChildElement):
    """
    The city name part of a user's postal address.
    """


class StateProv(SimpleChildElement):
    """
    The state or province name part of a user's postal address.
    """


class Country(ODMElement):
    """
    The country name part of a user's postal address. This must be represented by an ISO 3166 two-letter country code.
    """
    def __init__(self, country_code):
        super(Country, self).__init__()
        # TODO: Validate this
        self.country_code = country_code

    def build(self, builder):
        """
        Build this element
        :param builder: 
        :return: 
        """
        builder.start(self.__class__.__name__)
        builder.data(self.country_code)
        builder.end(self.__class__.__name__)


class PostalCode(SimpleChildElement):
    """
    The postal code part of a user's postal address.
    """


class OtherText(SimpleChildElement):
    """
    Any other text needed as part of a user's postal address.
    """

