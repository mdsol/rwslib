# -*- coding: utf-8 -*-
__author__ = 'isparks'

import enum


class DataType(enum.Enum):
    """ODM Data Types"""
    Text = 'text'
    Integer = 'integer'
    Float = 'float'
    Date = 'date'
    DateTime = 'datetime'
    Time = 'time'
    String = 'string'  # Used only by codelists


class QueryStatusType(enum.Enum):
    """MdsolQuery action type"""
    Open = "Open"
    Cancelled = "Cancelled"
    Answered = "Answered"
    Forwarded = "Forwarded"
    Closed = "Closed"


class StepType(enum.Enum):
    """Edit/Derivation step types"""
    CustomFunction = "CustomFunction"
    IsEmpty = "IsEmpty"
    IsNotEmpty = "IsNotEmpty"
    Contains = "Contains"
    StartsWith = "StartsWith"
    IsLessThan = "IsLessThan"
    IsLessThanOrEqualTo = "IsLessThanOrEqualTo"
    IsGreaterThan = "IsGreaterThan"
    IsGreaterThanOrEqualTo = "IsGreaterThanOrEqualTo"
    IsEqualTo = "IsEqualTo"
    IsNonConformant = "IsNonConformant"
    IsNotEqualTo = "IsNotEqualTo"
    InLocalLabRange = "InLocalLabRange"
    LengthIsLessThan = "LengthIsLessThan"
    LengthIsLessThanOrEqualTo = "LengthIsLessThanOrEqualTo"
    LengthIsGreaterThan = "LengthIsGreaterThan"
    LengthIsGreaterThanOrEqualTo = "LengthIsGreaterThanOrEqualTo"
    LengthIsEqualTo = "LengthIsEqualTo"
    Or = "Or"
    And = "And"
    Not = "Not"
    Now = "Now"
    IsPresent = "IsPresent"
    IsActive = "IsActive"
    Add = "Add"
    Subtract = "Subtract"
    Multiply = "Multiply"
    Divide = "Divide"
    AddDay = "AddDay"
    AddMonth = "AddMonth"
    AddYear = "AddYear"
    AddSec = "AddSec"
    AddMin = "AddMin"
    AddHour = "AddHour"
    DaySpan = "DaySpan"
    TimeSpan = "TimeSpan"
    Age = "Age"
    StringAdd = "StringAdd"
    Space = "Space"


ALL_STEPS = [StepType.CustomFunction,
             StepType.IsEmpty,
             StepType.IsNotEmpty,
             StepType.Contains,
             StepType.StartsWith,
             StepType.IsLessThan,
             StepType.IsLessThanOrEqualTo,
             StepType.IsGreaterThan,
             StepType.IsGreaterThanOrEqualTo,
             StepType.IsEqualTo,
             StepType.IsNonConformant,
             StepType.IsNotEqualTo,
             StepType.InLocalLabRange,
             StepType.LengthIsLessThan,
             StepType.LengthIsLessThanOrEqualTo,
             StepType.LengthIsGreaterThan,
             StepType.LengthIsGreaterThanOrEqualTo,
             StepType.LengthIsEqualTo,
             StepType.Or,
             StepType.And,
             StepType.Not,
             StepType.Now,
             StepType.IsPresent,
             StepType.IsActive,
             StepType.Add,
             StepType.Subtract,
             StepType.Multiply,
             StepType.Divide,
             StepType.AddDay,
             StepType.AddMonth,
             StepType.AddYear,
             StepType.AddSec,
             StepType.AddMin,
             StepType.AddHour,
             StepType.DaySpan,
             StepType.TimeSpan,
             StepType.Age,
             StepType.StringAdd]

# Note: Missing 2015 additions to edit check step functions.


VALID_DERIVATION_STEPS = [
    StepType.Age,
    StepType.Subtract,
    StepType.Multiply,
    StepType.Divide,
    StepType.AddDay,
    StepType.AddMonth,
    StepType.AddYear,
    StepType.AddSec,
    StepType.AddMin,
    StepType.AddHour,
    StepType.DaySpan,
    StepType.TimeSpan,
    StepType.Now,
    StepType.StringAdd,
    StepType.CustomFunction,
    StepType.Space,
    StepType.Add
]


class ActionType(enum.Enum):
    OpenQuery = "OpenQuery"
    RequireReview = "RequireReview"
    RequireVerification = "RequireVerification"
    AddComment = "AddComment"
    AddDeviation = "AddDeviation"
    CustomFunction = "CustomFunction"
    PlaceSticky = "PlaceSticky"
    AddForm = "AddForm"
    AddMatrix = "AddMatrix"
    MrgMatrix = "MrgMatrix"
    OldMrgMatrix = "OldMrgMatrix"
    SetNonconformant = "SetNonconformant"
    SendMessage = "SendMessage"
    SetDataPoint = "SetDataPoint"
    SetTimeZero = "SetTimeZero"
    SetTimeForward = "SetTimeForward"
    SetSubjectStatus = "SetSubjectStatus"
    SetSubjectName = "SetSubjectName"
    UpdateFormName = "UpdateFormName"
    UpdateFolderName = "UpdateFolderName"
    SetRecordDate = "SetRecordDate"
    SetDataPageDate = "SetDataPageDate"
    SetInstanceDate = "SetInstanceDate"
    SetSubjectDate = "SetSubjectDate"
    SetDataPointVisible = "SetDataPointVisible"
    SetSecondarySubjectName = "SetSecondarySubjectName"
    SetFormRequiresSignature = "SetFormRequiresSignature"
    SetFolderRequiresSignature = "SetFolderRequiresSignature"
    SetSubjectRequiresSignature = "SetSubjectRequiresSignature"
    SetDynamicSearchList = "SetDynamicSearchList"


ALL_ACTIONS = [
    ActionType.OpenQuery,
    ActionType.RequireReview,
    ActionType.RequireVerification,
    ActionType.AddComment,
    ActionType.AddDeviation,
    ActionType.CustomFunction,
    ActionType.PlaceSticky,
    ActionType.AddForm,
    ActionType.AddMatrix,
    ActionType.MrgMatrix,
    ActionType.OldMrgMatrix,
    ActionType.SetNonconformant,
    ActionType.SendMessage,
    ActionType.SetDataPoint,
    ActionType.SetTimeZero,
    ActionType.SetTimeForward,
    ActionType.SetSubjectStatus,
    ActionType.SetSubjectName,
    ActionType.UpdateFormName,
    ActionType.UpdateFolderName,
    ActionType.SetRecordDate,
    ActionType.SetDataPageDate,
    ActionType.SetInstanceDate,
    ActionType.SetSubjectDate,
    ActionType.SetDataPointVisible,
    ActionType.SetSecondarySubjectName,
    ActionType.SetFormRequiresSignature,
    ActionType.SetFolderRequiresSignature,
    ActionType.SetSubjectRequiresSignature,
    ActionType.SetDynamicSearchList
]


class RangeCheckComparatorType(enum.Enum):
    LessThanEqualTo = 'LE'
    GreaterThanEqualTo = 'GE'


class RangeCheckType(enum.Enum):
    Soft = 'Soft'
    Hard = 'Hard'


class ControlType(enum.Enum):
    CheckBox = 'CheckBox'
    Text = 'Text'
    DateTime = 'DateTime'
    DropDownList = 'DropDownList'
    SearchList = 'SearchList'
    RadioButton = 'RadioButton'
    RadioButtonVertical = 'RadioButton (Vertical)'
    FileUpload = 'File Upload'
    LongText = 'LongText'
    SignaturePage = 'Signature page'
    SignatureFolder = 'Signature folder'
    SignatureSubject = 'Signature subject'
