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
from flask import request

'''
redis_ip = 'lukeredis'
get_tag_host = 80
'''
redis_ip = 'localhost'
get_tag_host = 6004

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
conn = redis.Redis(host=redis_ip,port=6379,db=0)

@app.route('/GetAllTag',methods=['GET'])
def get_alltag():
    vid = request.args.get('vid')
    tag_info = conn.get(vid)
    tag_info = json.loads(tag_info)
    res = json.dumps(tag_info, ensure_ascii = False)
    res = jsonify(tag_info)
    res.headers['Content-Type'] = 'application/json; charset=utf-8'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'  
    return res


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=get_tag_host)
