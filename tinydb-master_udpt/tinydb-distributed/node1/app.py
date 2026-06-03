from flask import Flask, request
from tinydb import TinyDB
import requests

app = Flask(__name__)

db = TinyDB('db1.json')

OTHER_NODE = "http://127.0.0.1:5001/replicate"


@app.route('/insert', methods=['POST'])
def insert_data():

    data = request.json

    db.insert(data)

    try:
        requests.post(OTHER_NODE, json=data)

    except:
        print("Node2 is offline")

    return {
        "message": "inserted"
    }


@app.route('/replicate', methods=['POST'])
def replicate():

    data = request.json

    db.insert(data)

    return {
        "message": "replicated"
    }


# THÊM ĐOẠN NÀY
@app.route('/data', methods=['GET'])
def get_data():

    return {
        "data": db.all()
    }


app.run(port=5000)