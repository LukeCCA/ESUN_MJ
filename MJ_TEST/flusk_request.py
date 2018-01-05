#-*- coding:utf-8 -*-
import os
import sys
import operator
from flask import Flask,g
import time
from flask import jsonify
import json
import requests
from flask import request
import pybreaker

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


timebreaker = pybreaker.CircuitBreaker(fail_max = 2, reset_timeout=3)

@timebreaker
def _get_time(value):
    response = requests.get('http://localhost:6104/Sleep', timeout = 3.0)
    return response.json().get('datetime')


@app.route('/Hope',methods=['GET'])
def hope():
    try:
        a = _get_time(1)
        return a
    except requests.exceptions.ReadTimeout:
        return 'TimeOut'
    except pybreaker.CircuitBreakerError:
        return 'Break'
    

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6105)