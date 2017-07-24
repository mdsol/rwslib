# -*- coding: utf-8 -*-

__author__ = 'anewbigging'

from rwslib import RWSConnection
from rwslib.rws_requests import *
from rwslib.rwsobjects import RWSException
import requests
from requests.auth import HTTPBasicAuth
from lxml import etree
from functools import partial
from rwslib.extras.rwscmd.odmutils import xml_pretty_print, E_ODM, A_ODM
from rwslib.extras.rwscmd.data_scrambler import Scramble
import click

GET_DATA_DATASET = 'rwscmd_getdata.odm'


class GetDataConfigurableDataset(ConfigurableDatasetRequest):
    VALID_DATASET_FORMATS = ("odm")

    def __init__(self, dataset, study, environment, subject, params=None):
        dataset_name, dataset_format = dataset.split('.')
        studyoid = "{}({})".format(study, environment)
        if params is None:
            params = {}
        params.update(dict(StudyOID=studyoid, SubjectKey=subject))
        super(GetDataConfigurableDataset, self).__init__(dataset_name, dataset_format, params)


@click.group()
@click.option('--username', '-u', prompt=True, default='', envvar='RWSCMD_USERNAME', help='Rave login')
@click.option('--password', '-p', prompt=True, default='', hide_input=True, envvar='RWSCMD_PASSWORD',
              help='Rave password')
@click.option('--virtual_dir', default=None, envvar='RWSCMD_VIRTUAL_DIR',
              help='RWS virtual directory, defaults to RaveWebServices')
@click.option('--raw/--list', default=False,
              help='Display raw xml response from RWS or human-readable list, defaults to list')
@click.option('--verbose/--silent', '-v/-s', default=False)
@click.option('--output', '-o', default=None, type=click.File('wb'), help='Write output to file')
@click.argument('url')
@click.pass_context
def rws(ctx, url, username, password, raw, verbose, output, virtual_dir):
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj['URL'] = url
    ctx.obj['USERNAME'] = username
    ctx.obj['PASSWORD'] = password
    ctx.obj['VIRTUAL_DIR'] = virtual_dir
    if virtual_dir:
        if username and password:
            ctx.obj['RWS'] = RWSConnection(url, username, password, virtual_dir=virtual_dir)
        else:
            # Acceptable for UnAuth Requests
            ctx.obj['RWS'] = RWSConnection(url, virtual_dir=virtual_dir)
    else:
        if username and password:
            ctx.obj['RWS'] = RWSConnection(url, username, password)
        else:
            ctx.obj['RWS'] = RWSConnection(url)
    ctx.obj['RAW'] = raw
    ctx.obj['OUTPUT'] = output
    ctx.obj['VERBOSE'] = verbose


def get_data(ctx, study, environment, subject):
    """
    Call rwscmd_getdata custom dataset to retrieve currently enterable, empty fields
    """
    cfg = GetDataConfigurableDataset(GET_DATA_DATASET,
                                     study,
                                     environment,
                                     subject,
                                     params=dict(IncludeIDs=0,
                                                 IncludeValues=0))
    # path = "datasets/{}?StudyOID={}&SubjectKey={}" \
    #        "&IncludeIDs=0&IncludeValues=0".format(GET_DATA_DATASET, studyoid, subject)
    # url = make_url(ctx.obj['RWS'].base_url, path)

    if ctx.obj['VERBOSE']:
        click.echo('Getting data list')
    # Get the client instance
    client = ctx.obj['RWS']  #: type: RWSConnection
    # Client rolls in the base_url
    resp = client.send_request(cfg)
    # resp = requests.get(url, auth=HTTPBasicAuth(ctx.obj['USERNAME'], ctx.obj['PASSWORD']))

    if client.last_result.status_code != 200:
        click.echo(client.last_result.text)

    return xml_pretty_print(resp)


def rws_call(ctx, method, default_attr=None):
    """Make request to RWS"""
    try:
        response = ctx.obj['RWS'].send_request(method)

        if ctx.obj['RAW']:  # use response from RWS
            result = ctx.obj['RWS'].last_result.text
        elif default_attr is not None:  # human-readable summary
            result = ""
            for item in response:
                result = result + item.__dict__[default_attr] + "\n"
        else:  # use response from RWS
            result = ctx.obj['RWS'].last_result.text

        if ctx.obj['OUTPUT']:  # write to file
            ctx.obj['OUTPUT'].write(result.encode('utf-8'))
        else:  # echo
            click.echo(result)

    except RWSException as e:
        click.echo(str(e))


@rws.command()
@click.pass_context
def version(ctx):
    """Display RWS version"""
    rws_call(ctx, VersionRequest())


@rws.command()
@click.argument('path', nargs=-1)
@click.pass_context
def data(ctx, path):
    """List EDC data for [STUDY] [ENV] [SUBJECT]"""
    _rws = partial(rws_call, ctx)
    if len(path) == 0:
        _rws(ClinicalStudiesRequest(), default_attr='oid')
    elif len(path) == 1:
        _rws(StudySubjectsRequest(path[0], 'Prod'), default_attr='subjectkey')
    elif len(path) == 2:
        _rws(StudySubjectsRequest(path[0], path[1]), default_attr='subjectkey')
    elif len(path) == 3:
        try:
            click.echo(get_data(ctx, path[0], path[1], path[2]))
        except RWSException as e:
            click.echo(str(e))
        except requests.exceptions.HTTPError as e:
            click.echo(str(e))
    else:
        click.echo('Too many arguments')


@rws.command()
@click.argument('odm', type=click.File('rb'))
@click.pass_context
def post(ctx, odm):
    """Post ODM clinical data"""
    try:
        ctx.obj['RWS'].send_request(PostDataRequest(odm.read()))
        if ctx.obj['RAW']:
            click.echo(ctx.obj['RWS'].last_result.text)
    except RWSException as e:
        click.echo(e.message)


@rws.command()
@click.option('--drafts/--versions', default=False, help='List CRF drafts or versions (default)')
@click.argument('path', nargs=-1)
@click.pass_context
def metadata(ctx, drafts, path):
    """List metadata for [PROJECT] [VERSION]"""
    _rws = partial(rws_call, ctx)
    if len(path) == 0:
        _rws(MetadataStudiesRequest(), default_attr='oid')
    elif len(path) == 1:
        if drafts:
            _rws(StudyDraftsRequest(path[0]), default_attr='oid')
        else:
            _rws(StudyVersionsRequest(path[0]), default_attr='oid')
    elif len(path) == 2:
        _rws(StudyVersionRequest(path[0], path[1]))
    else:
        click.echo('Too many arguments')


@rws.command()
@click.argument('path')
@click.pass_context
def direct(ctx, path):
    """Make direct call to RWS, bypassing rwslib"""
    try:
        url = make_url(ctx.obj['RWS'].base_url, path)
        resp = requests.get(url, auth=HTTPBasicAuth(ctx.obj['USERNAME'], ctx.obj['PASSWORD']))
        click.echo(resp.text)
    except RWSException as e:
        click.echo(e.message)
    except requests.exceptions.HTTPError as e:
        click.echo(e.message)


@rws.command()
@click.option('--steps', type=click.INT, default=10, help='Number of data entry iterations (default=10)')
@click.option('--metadata', default=None, type=click.File('rb'),
              help='Metadata file (optional)')
@click.option('--fixed', default=None, type=click.File('rb'),
              help='File with values to override generated data (one per line in format ItemOID,Value)')
@click.argument('study')
@click.argument('environment')
@click.argument('subject')
@click.pass_context
def autofill(ctx, steps, metadata, fixed, study, environment, subject):
    """Request enterable data for a subject, generate data values and post back to Rave.
    Requires 'rwscmd_getdata' configurable dataset to be installed on the Rave URL."""

    if metadata is not None:  # Read metadata from file, if supplied
        odm_metadata = metadata.read()
        meta_v = etree.fromstring(odm_metadata).find('.//' + E_ODM.METADATA_VERSION.value).get(A_ODM.OID.value)
    else:
        odm_metadata = None
        meta_v = None

    fixed_values = {}
    if fixed is not None:  # Read fixed values from file, if supplied
        for f in fixed:
            oid, value = f.decode().split(',')
            fixed_values[oid] = value
            if ctx.obj['VERBOSE']:
                click.echo('Fixing {} to value: {}'.format(oid, value))

    try:
        for n in range(0, steps):
            if ctx.obj['VERBOSE']:
                click.echo('Step {}'.format(str(n + 1)))

            # Get currently enterable fields for this subject
            subject_data = get_data(ctx, study, environment, subject)

            subject_data_odm = etree.fromstring(subject_data)
            if subject_data_odm.find('.//' + E_ODM.CLINICAL_DATA.value) is None:
                if ctx.obj['VERBOSE']:
                    click.echo('No data found')
                break

            # Get the metadata version for the subject
            subject_meta_v = subject_data_odm.find('.//' + E_ODM.CLINICAL_DATA.value).get(
                A_ODM.METADATA_VERSION_OID.value)
            if subject_meta_v is None:
                if ctx.obj['VERBOSE']:
                    click.echo('Subject not found')
                break

            # If no metadata supplied, or versions don't match, retrieve metadata from RWS
            if meta_v != subject_meta_v:
                if ctx.obj['VERBOSE']:
                    click.echo('Getting metadata version {}'.format(subject_meta_v))
                ctx.obj['RWS'].send_request(StudyVersionRequest(study, subject_meta_v))
                odm_metadata = ctx.obj['RWS'].last_result.text
                meta_v = subject_meta_v

            # Generate data values to fill in empty fields
            if ctx.obj['VERBOSE']:
                click.echo('Generating data')

            scr = Scramble(odm_metadata)
            odm = scr.fill_empty(fixed_values, subject_data)

            # If new data values, post to RWS
            if etree.fromstring(odm).find('.//' + E_ODM.ITEM_DATA.value) is None:
                if ctx.obj['VERBOSE']:
                    click.echo('No data to send')
                break
            ctx.obj['RWS'].send_request(PostDataRequest(odm))
            if ctx.obj['RAW']:
                click.echo(ctx.obj['RWS'].last_result.text)

    except RWSException as e:
        click.echo(e.rws_error)

    except requests.exceptions.HTTPError as e:
        click.echo(e.strerror)
