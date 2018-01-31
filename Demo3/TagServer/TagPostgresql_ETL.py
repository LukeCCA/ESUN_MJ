#-*- coding:utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import time
import json
import psycopg2
import sys
import inspect
import os


IP = "lukepostgres"
USER = 'postgres'
PASSWORD = 'lukechen0419'
DB = 'postgres'
'''
IP = os.environ['POSTGRES_IP']
USER = os.environ['POSTGRES_USER']
PASSWORD = os.environ['POSTGRES_PASSWORD']
DB = os.environ['POSTGRES_MJDB']
'''

# connect PostgreSQL
conn = psycopg2.connect(database = DB,
                        host = IP,
                        user = USER,
                        password = PASSWORD)
cur = conn.cursor()

# Read Data

file_path = inspect.getfile(inspect.currentframe())
file_direction = os.path.dirname(os.path.abspath(file_path))
tag_data = os.path.join( file_direction , './Data/INTENT_TAG.xlsx' )
df = pd.read_excel(tag_data)

'''
df = pd.read_excel(sys.argv[1])
'''

# TagDB 轉 JSON 檔
def TagDb_ETL(data):
    Tag_DB = []
    rows = len(data)
    for row in range(rows):
        Tag = {}
        Tag['TAG_ID'] = data['TAG_ID'][row]
        Tag['scenario'] = {'DIIS1' : '',
                          'DIIS2' : '',
                          'DIIS3' : ''}
        scenario = data.scenario[row].split('|')
        for j in range(len(scenario)):
            DIIS = 'DIIS' + str(j+1)
            Tag['scenario'][DIIS] = scenario[j]
        Tag['recommedWeight'] = data['recommedWeight'][row]
        Tag['modelId'] = data['modelId'][row]
        Tag['operationType'] = data['operationType'][row]
        Tag['dataSource'] = data['dataSource'][row]
        Tag['securityFilter'] = data['securityFilter'][row]
        Tag['expireAfter'] = data['expireAfter'][row]
        Tag['createTime'] = data['create Time'][row]
        Tag['updateTime'] = data['update Time'][row]
        Tag['tagVersion'] = data['tagVersion'][row]
        Tag['isActive'] = data['isActive'][row]
        Tag['Chinese_Desc'] = data['Chinese_Desc'][row]
        Tag['referenceDocument'] = data['referenceDocument'][row]
        Tag_DB.append(Tag)
    return Tag_DB

# 標籤庫Dict
TagDB = TagDb_ETL(df)


# Check if there is tag_db in Postgresql
cur.execute("select * from information_schema.tables where table_name='tag_db';")
if bool(cur.rowcount):
    print 'tag_db is exist!'
    pass

    '''
# Insert Data into PostgreSQL
    for i in TagDB:
        SQL = "INSERT INTO tag_db(tag_info) VALUES('{}');".format(json.dumps(i))
        cur.execute(SQL)
        conn.commit()
    print 'Tag DB ETL Done!'
    '''

else:
    SQL = "CREATE TABLE tag_db(id serial PRIMARY KEY,tag_info json NOT NULL);"
    cur.execute(SQL)
    conn.commit()
    print "Create Table Done!"

# Insert Data into PostgreSQL
    print "Start Insert Data!"
    for i in TagDB:
        SQL = "INSERT INTO tag_db(tag_info) VALUES('{}');".format(json.dumps(i))
        cur.execute(SQL)
        conn.commit()
    print 'Tag DB ETL Done!'