#-*- coding:utf-8 -*-
import os
import sys
import json
import operator
from flask import Flask,g
import time
from flask import jsonify
import json
import redis
import Collobrative_Filtering as CF
import requests
from flask import request
import pickle

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/GetRecommandationV1',methods=['GET'])
def get_recommandation():
    
    vid = request.args.get('vid')
    url = 'http://0.0.0.0:6004/GetAllTag'
    payload = {'vid':vid}
    user_tags = requests.get(url, params=payload)
    user_tags = json.loads(user_tags.content)
    model = CF.COLLOBORATIVE_FILTERING()
    
    res = {'Offer': 
    model.predict(user_tags, True, 15, rating_table, tag, offerlabel_mapping, tag_mapping, reverse_offertag)}

    res = jsonify(res)
    res.headers['Content-Type'] = 'application/json; charset=utf-8'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'  
    print rating_table
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

    app.run(debug=True, host="0.0.0.0", port=6010)
