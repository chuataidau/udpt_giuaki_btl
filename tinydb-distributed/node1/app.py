
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pyrefly: ignore [missing-import]
from flask import Flask, request
from tinydb import TinyDB, Query
import requests
import time
from utils.timestamp_manager import generate_timestamp

app = Flask(__name__)

db = TinyDB('db1.json')

OTHER_NODE = "http://127.0.0.1:5001/replicate"

NODE_ID = 1

User = Query()


@app.route('/insert', methods=['POST'])
def insert_data():

    data = request.json

    data["timestamp"] = generate_timestamp()
    data["node_id"] = NODE_ID

    old_data = db.search(User.id == data["id"])

    if not old_data:

        db.insert(data)

    else:

        old_timestamp = old_data[0]["timestamp"]
        old_node_id = old_data[0].get("node_id", 1)

        if data["timestamp"] > old_timestamp:

            db.update(data, User.id == data["id"])

        elif data["timestamp"] == old_timestamp:

            if data["node_id"] < old_node_id:

                db.update(data, User.id == data["id"])

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

    old_data = db.search(User.id == data["id"])

    if not old_data:

        db.insert(data)

    else:

        old_timestamp = old_data[0]["timestamp"]
        old_node_id = old_data[0].get("node_id", 1)

        if data["timestamp"] > old_timestamp:

            db.update(data, User.id == data["id"])

        elif data["timestamp"] == old_timestamp:

            if data["node_id"] < old_node_id:

                db.update(data, User.id == data["id"])

    return {
        "message": "replicated"
    }


@app.route('/data', methods=['GET'])
def get_data():

    return {
        "data": db.all()
    }


app.run(port=5000)

"""
Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/insert" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"id":2,"name":"Tran Thi B","age":21}'
"""

