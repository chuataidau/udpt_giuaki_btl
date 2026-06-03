from flask import Flask, request
from tinydb import TinyDB
import requests

# Khởi tạo Flask app
app = Flask(__name__)

# Database của node2
db = TinyDB('db2.json')

# Địa chỉ node1 để replication
OTHER_NODE = "http://127.0.0.1:5000/replicate"


# API insert dữ liệu vào node2
@app.route('/insert', methods=['POST'])
def insert_data():

    # Lấy dữ liệu JSON từ request
    data = request.json

    # Insert vào TinyDB của node2
    db.insert(data)

    # Gửi dữ liệu sang node1 để replicate
    try:
        requests.post(OTHER_NODE, json=data)

    except:
        print("Node1 is offline")

    return {
        "message": "Data inserted into node2 and replicated"
    }


# API nhận dữ liệu replication từ node1
@app.route('/replicate', methods=['POST'])
def replicate():

    # Nhận dữ liệu
    data = request.json

    # Lưu vào database node2
    db.insert(data)

    return {
        "message": "Replication success on node2"
    }


# API xem toàn bộ dữ liệu
@app.route('/data', methods=['GET'])
def get_data():

    return {
        "data": db.all()
    }


# Chạy node2 ở port 5001
app.run(port=5001)