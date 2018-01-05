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
import redis


#如果使用讀取資料的形式
file_path = inspect.getfile(inspect.currentframe())
file_direction = os.path.dirname(os.path.abspath(file_path))
tagging = os.path.join( file_direction , 'MJ_TAG.xlsx' )
taggingvalue = os.path.join( file_direction , 'MJ_TAGVALUE.xlsx' )
df1 = pd.read_excel(tagging)
df2 = pd.read_excel(taggingvalue)

'''
df1 = pd.read_excel(sys.argv[1])
df2 = pd.read_excel(sys.argv[2])
'''
df = pd.concat([df1,df2]).reset_index(drop = True)
'''
HOST_POSTGRES = os.environ['POSTGRES_IP']
USER = os.environ['POSTGRES_USER']
PASSWORD = os.environ['POSTGRES_PASSWORD']
HOST_REDIS = os.environ['REDIS_IP']
'''
DB = 'postgres'
HOST_POSTGRES = 'lukepostgres'
USER = 'postgres'
PASSWORD = 'lukechen0419'
HOST_REDIS = 'lukeredis'
'''
DB = 'MJ_PROTOTYPE'
'''
# 貼標庫格式
def Tag_query(tag, sql_db):
    SQL = "SELECT tag_info FROM tag_db WHERE tag_info->>'TAG_ID' = '{}';".format(tag)
    sql_db.execute(SQL)
    records = sql_db.fetchall()[0][0]
    data = {}
    data['TAG_ID'] = records['TAG_ID']
    data['scenario'] = records['scenario']
    data['dataSource'] = records['dataSource']
    data['securityFilter'] = records['securityFilter']
    data['tagTime'] = time.time()
    data['expireTime'] = time.time() + records['expireAfter']
    data['isValid'] = records['isActive']
    return data

# Database設定
redis_conn = redis.Redis(host= HOST_REDIS ,port=6379,db=0)
sql_conn = psycopg2.connect(database = DB,
                        host = HOST_POSTGRES,
                        user = USER,
                        password = PASSWORD)
cur = sql_conn.cursor()

# 組裝Tagging_Db，並塞入DB
def TaggingDB_ETL(data, TagDB=cur, TaggingDB=redis_conn):
    print 'Start Tagging DB ETL'
    vids = data.ID.unique()
    times = 1
    for i in vids:
        Tagging = {}
        Tagging['VID'] = i
        Tagging['batchTag'] = []
        Tagging['realtimeTag'] = []
        tag = data[data.ID==i][['UTID','TAG_VALUE']]
        for j in range(len(tag)):
            Tag = Tag_query(tag.UTID.values[j], TagDB)
            Tag['TAG_VALUE'] = tag.TAG_VALUE.values[j]
            Tagging['batchTag'].append(Tag)

        TaggingDB.set(i, json.dumps(Tagging,ensure_ascii=False))
        print 'Finish ' + str(times) + 'th data'
        times += 1
TaggingDB_ETL(df)

print 'Tagging DB ETL Done!'
