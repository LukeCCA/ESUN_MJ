#-*- coding:utf-8 -*-
import os
import sys
import json
import operator
from flask import Flask,g
import time
from flask import jsonify
import json
import Collobrative_Filtering as CF
import requests
from flask import request
import pickle
import pybreaker

reload(sys)
sys.setdefaultencoding('utf8')


timebreaker = pybreaker.CircuitBreaker(fail_max = 2, reset_timeout=10)


@timebreaker
def _get_usertags(value):
    url = "http://%s/GetAllTag"%(TAG_SERVER,)
    payload = {'vid':value}
    response = requests.get(url, params=payload, timeout = 0.1)
    try:
        user_tags = json.loads(response.content)
    except ValueError:
        user_tags = json.loads(requests.get(url, params={'vid':1}, timeout = 0.1).content)
    return user_tags



TAG_SERVER = 'tagserver'
RECO_PORT = 80
'''
TAG_SERVER = 'localhost:6004'
RECO_PORT = 6010
'''

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/GetRecommendationV1',methods=['GET'])
def get_recommandation():
    
    vid = request.args.get('vid')
    number = request.args.get('number')
    
    if number is None:
        number = 6 
    number = int(number)
    try:
        user_tags = _get_usertags(vid)   
        model = CF.COLLOBORATIVE_FILTERING()
        # 15為用來計算的offer tag數目，6為吐出offer的數目
        response = model.predict(user_tags, online=True, similar_num=10, offertag_num=15, offer_number=6, rating_table=rating_table, tag=tag, offerlabel_mapping=offerlabel_mapping, tag_mapping=tag_mapping, reverse_offertag=reverse_offertag, offer_maptb=offer_maptb, offer_sparse=offer_sparse)
        res = {'Offer': response}
    except:
        res = {'Offer':['OFF0029', 'OFF0001', 'OFF0002', 'OFF0004', 'OFF0005', 'OFF0006']}
    

    res = jsonify(res)
    res.headers['Content-Type'] = 'application/json; charset=utf-8'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'  
    return res

if __name__ == "__main__":

    # load Model and Mapping Table
    with open('offerrating_table.pickle', 'rb') as f:
        rating_table = pickle.load(f)
    with open('user_sparse.pickle', 'rb') as f1:
        tag = pickle.load(f1)
    with open('offerlabel_mapping.pickle', 'rb') as f2:
        offerlabel_mapping = pickle.load(f2)
    with open('tag_mapping.pickle', 'rb') as f3:
        tag_mapping = pickle.load(f3)
    with open('reverse_offertag.pickle', 'rb') as f4:
        reverse_offertag = pickle.load(f4) 
    with open('offer_maptb.pickle', 'rb') as f5:
        offer_maptb = pickle.load(f5)
    with open('offer_sparse.pickle', 'rb') as f6:
        offer_sparse = pickle.load(f6)

    app.run(debug=True, host="0.0.0.0", port=RECO_PORT)
