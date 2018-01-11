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
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/Streaming',methods=['POST'])
def get_alltag():
    data = request.data
    print data
    res = {'status':'ok'}
    res = jsonify(res) 
    res.headers['Content-Type'] = 'application/json; charset=utf-8'
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'  
    return res


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
