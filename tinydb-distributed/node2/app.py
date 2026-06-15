
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pyrefly: ignore [missing-import]
from flask import Flask, request
from tinydb import TinyDB, Query
import requests
from utils.timestamp_manager import generate_timestamp

app = Flask(__name__)

db = TinyDB('db2.json')

OTHER_NODE = "http://127.0.0.1:5000/replicate"

NODE_ID = 2

User = Query()


# API insert dữ liệu vào node2
@app.route('/insert', methods=['POST'])
def insert_data():

    data = request.json

    # Sinh timestamp và gắn node_id
    data["timestamp"] = generate_timestamp()
    data["node_id"] = NODE_ID

    old_data = db.search(User.id == data["id"])

    if not old_data:

        db.insert(data)

    else:

        old_timestamp = old_data[0]["timestamp"]
        old_node_id = old_data[0].get("node_id", 2)

        # Conflict Resolution
        if data["timestamp"] > old_timestamp:

            db.update(data, User.id == data["id"])

        elif data["timestamp"] == old_timestamp:

            if data["node_id"] < old_node_id:

                db.update(data, User.id == data["id"])

    # Replication sang node1
    try:

        requests.post(OTHER_NODE, json=data)

    except:

        print("Node1 is offline")

    return {
        "message": "Data inserted into node2 and replicated"
    }


# API nhận replication từ node1
@app.route('/replicate', methods=['POST'])
def replicate():

    data = request.json

    old_data = db.search(User.id == data["id"])

    if not old_data:

        db.insert(data)

    else:

        old_timestamp = old_data[0]["timestamp"]
        old_node_id = old_data[0].get("node_id", 2)

        # Conflict Resolution
        if data["timestamp"] > old_timestamp:

            db.update(data, User.id == data["id"])

        elif data["timestamp"] == old_timestamp:

            if data["node_id"] < old_node_id:

                db.update(data, User.id == data["id"])

    return {
        "message": "Replication success on node2"
    }


# API xem toàn bộ dữ liệu
@app.route('/data', methods=['GET'])
def get_data():

    return {
        "data": db.all()
    }


# API xóa dữ liệu trên node2
# và replicate thao tác xóa sang node1
@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_data(user_id):

    db.remove(User.id == user_id)

    try:

        requests.delete(
            f"http://127.0.0.1:5000/delete_replica/{user_id}"
        )

    except:

        print("Node1 is offline")

    return {
        "message": f"Deleted id={user_id} and replicated"
    }


# API nhận yêu cầu xóa từ node1
@app.route('/delete_replica/<int:user_id>', methods=['DELETE'])
def delete_replica(user_id):

    db.remove(User.id == user_id)

    return {
        "message": f"Replica delete success for id={user_id}"
    }


app.run(port=5001)

