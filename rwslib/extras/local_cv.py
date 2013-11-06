__author__ = 'isparks'

#-----------------------------------------------------------------------------------------------------------------------
# Overview
#
# local_cv is a small framework utilizing rwslib that pulls clinical view data from Rave and into a local
# (to your own machine) database where it can be queried, reported on by SQL tools etc.
#
# The library provides a simple SQLLite proof of concept but other SQL engines could be supported by creating
# new subclasses of BaseDBAdapter to handle the DDL, DML and database population.

from rwslib import RWSConnection
from rwslib.rws_requests.biostats_gateway import ProjectMetaDataRequest, FormDataRequest

import os
from csv import DictReader
from itertools import groupby
import sqlite3
from cStringIO import StringIO
import logging




#-----------------------------------------------------------------------------------------------------------------------
# Classes

class BaseDBAdapter(object):
    """
    A DBAdapter provides functionality to convert a set of dataset definitions into DDL statements suitable for
    storage of data in that format. It also provides capability to insert data into that database once provided.

    Key responsibilities:

    1. Convert set of dataset definitions to DDL
    2. Populate / create tables with DDL
    3. Convert set of data rows to INSERT statements
    4. Execute Insert statements against database to build DB

    """
    def __init__(self):
        """Override in descendant classes to receive information about the DB to be populated"""
        self.datasets = {}

    @staticmethod
    def getCSVReader(data):
        """Take a Rave CSV output ending with a line with just EOF on it and return a DictReader"""
        f = StringIO(data[:-4]) #Remove \nEOF
        return DictReader(f)

    def processMetaData(self, metadata):
        """Takes a string representing a View metadata CSV extract from RWS, sets dataset dictionary
           where each dataset key has a list of dictionaries representing fields in dataset
        """
        self._setDatasets(metadata)
        self._processDDL()

    def _setDatasets(self, metadata):
        """Extract dataset definitions from CSV metadata"""
        #Pull the lot into a list
        cols = list(self.getCSVReader(metadata))

        #sort the cols by view name and ordinal (they come sorted, but lets be sure)
        def sort_func(r1, r2):
            val1 = r1["viewname"], int(r1["ordinal"])
            val2 = r2["viewname"], int(r2["ordinal"])
            return cmp(val1,val2)
        cols.sort(sort_func)

        #Now group them by their viewname
        for key, grp in groupby(cols, key=lambda x: x["viewname"]):
            self.datasets[key] = list(grp)

    def _processDDL(self):
        """Generate table SQL, override for each database variant"""
        raise NotImplementedError("Override makeTableSQL in descendant classes")

    def processFormData(self, data, dataset_name):
        """Take a string of form data as CSV and convert to insert statements, return template and data values"""

        #Get the cols for this dataset
        cols = self.datasets[dataset_name]
        reader =  self.getCSVReader(data)
        fieldnames = reader.fieldnames

        #Check columns
        for col in cols:
            varname = col["varname"]
            if varname not in fieldnames:
                raise ValueError("Column %s not found in data for dataset %s" % (varname, dataset_name,) )

        #Now call overrideen methods of base classes to process this data
        self._processDML(dataset_name, cols, reader)

    def _processDML(self, dataset_name, cols, reader):
        """Create and populate table with values from dataset"""
        raise NotImplementedError("Override _createDML in descendant classes")

class SQLLiteDBAdapter(BaseDBAdapter):
    """Variant that makes SQLLite SQL"""

    def __init__(self, db):
        """Receives a SQLLiteDB to populate"""
        BaseDBAdapter.__init__(self)
        self.conn = db

    def _processDDL(self):
        """Generate and process table SQL, SQLLite version"""
        sql_statements = self._generateDDL()

        logging.info('Generating sqllite tables')
        for stmt in sql_statements:
            c = self.conn.cursor()
            c.execute(stmt)
            self.conn.commit()

    def _generateDDL(self):
        """Generate DDL statements for SQLLite"""
        sql = []
        #Next convert each set of columns into a table structure
        for dataset_name in self.datasets.keys():

            #SQL to drop the table if it already exists
            sql.append('''drop table if exists %s;''' % dataset_name)

            #Generate the SQL for the cols
            cols = self.datasets[dataset_name]
            col_defs = []
            for col in cols:
                sql_datatype = self.getSQLDataType(col["vartype"],col["varlength"],col["varformat"])
                col_defs.append("%s %s" % (col["varname"],sql_datatype,))

            l = ["CREATE TABLE %s " % dataset_name]
            l.append("(")
            l.append(','.join(col_defs))
            l.append(")")

            stmt = ''.join(l)
            sql.append(stmt)

        return sql

    @staticmethod
    def getSQLDataType(dtype, dlength, dformat):
        """Return SQLLite data type for a Rave view data type"""
        return dict(num = "NUMERIC", char = "TEXT")[dtype]

    def _processDML(self, dataset_name, cols, reader):
        """Overridden version of create DML for SQLLite"""
        sql_template, rows = self._generateDML(dataset_name, cols, reader)

        #Now insert in batch
        c = self.conn.cursor()
        c.executemany(sql_template, rows)
        self.conn.commit()

    def _generateDML(self, dataset_name, cols, reader):
        """Generates a sql INSERT template and marshals row data into form that meets INSERT statements expectations"""
        col_names = [col["varname"] for col in cols]

        #Generate question mark placeholders
        qm = []
        for _ in col_names:
            qm.append('?')
        qms = ','.join(qm)

        sql_template = 'INSERT INTO %s (%s) values (%s)' % (dataset_name, ','.join(col_names), qms)

        rows = []
        for row in reader:
            rows.append(tuple([row[name] for name in col_names]))

        return sql_template, rows

class LocalCVBuilder(object):
    """
    Does the work of pulling data from Rave via RWS. All database activities are delegated to the db_adapter.
    """
    def __init__(self, rws_connection, project_name, environment, db_adapter):
        self.rws_connection = rws_connection
        self.project_name = project_name
        self.environment = environment
        self.db_adapter = db_adapter

    @staticmethod
    def name_type_from_viewname(viewname):
        """Have format V_<studyname>_<view>[_RAW], return name and view type REGULAR or RAW"""
        vars = viewname.split('_')
        name = vars[2]
        if len(vars) == 4:
            _type = vars[3]
        else:
            _type = 'REGULAR'
        return name, _type

    def execute(self):
        """Generate local DB, pulling metadata and data from RWSConnection"""

        logging.info('Requesting view metadata for project %s' % self.project_name)
        project_csv_meta = self.rws_connection.send_request(ProjectMetaDataRequest(self.project_name))

        #Process it into a set of tables
        self.db_adapter.processMetaData(project_csv_meta)

        #Get the data for the study
        for dataset_name in self.db_adapter.datasets.keys():
            logging.info('Requesting data from dataset %s' % dataset_name)
            form_name, _type = self.name_type_from_viewname(dataset_name)
            form_data = self.rws_connection.send_request(FormDataRequest(self.project_name,self.environment,_type,form_name))

            #Now process the form_data into the db of choice
            logging.info('Populating dataset %s' % dataset_name)
            self.db_adapter.processFormData(form_data, dataset_name)

        logging.info('Process complete')


if __name__ == '__main__':

    #An example
    logging.basicConfig(level=logging.INFO)

    from rwslib._settings import accounts

    #Accounts is a dict of dicts like
    # accounts = {'innovate' : {'username': 'username',
    #                          'password':'password'},
    #             'otherurl' : {'username': 'username',
    #                          'password':'password'},
    #            }

    acc = accounts['innovate']
    rv = RWSConnection('innovate', acc['username'], acc['password'])

    path, _ = os.path.split(os.path.realpath(__file__))
    db_path = os.path.join(path, 'local_cvs.db')

    #Make sqllite connection
    logging.info('Opening/overwriting sqllite db %s' % db_path)
    conn = sqlite3.connect(db_path)

    #DBAdaptor takes care of all the database specific parts of the process
    db_adaptor = SQLLiteDBAdapter(conn)

    lcv = LocalCVBuilder(rv, 'SIMPLESTUDY', 'TEST', db_adaptor)
    lcv.execute()

    #Once complete you can do further work with the conn object, run SQL statements etc.
