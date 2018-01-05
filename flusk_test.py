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

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/Sleep',methods=['GET'])
def sleep_well():
    time.sleep(5)
    return "I'm sleeping!!!!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=6104)