
import sys
import os

# Thêm đường dẫn thư mục cha vào Python path
# để import được thư mục utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Flask dùng để xây dựng REST API
# pyrefly: ignore [missing-import]
from flask import Flask, request

# TinyDB là database dạng document
# Query dùng để tìm kiếm dữ liệu theo điều kiện
from tinydb import TinyDB, Query

# requests dùng để gửi dữ liệu replication sang node khác
import requests

# time được import để hỗ trợ xử lý timestamp
import time

# Hàm sinh timestamp từ thư mục utils
from utils.timestamp_manager import generate_timestamp

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Khởi tạo database cho node1
db = TinyDB('db1.json')

# Địa chỉ API replicate của node2
OTHER_NODE = "http://127.0.0.1:5001/replicate"

# ID của node hiện tại
# Dùng để tie-break khi timestamp bằng nhau
NODE_ID = 1

# Tạo đối tượng Query để truy vấn TinyDB
User = Query()


# API insert dữ liệu vào node1
@app.route('/insert', methods=['POST'])
def insert_data():

    # Lấy dữ liệu JSON từ request
    data = request.json

    # Sinh timestamp hiện tại
    data["timestamp"] = generate_timestamp()

    # Gắn ID của node tạo dữ liệu
    data["node_id"] = NODE_ID

    # Tìm dữ liệu cũ có cùng id
    old_data = db.search(User.id == data["id"])

    # Nếu chưa tồn tại thì insert mới
    if not old_data:

        db.insert(data)

    else:

        # Lấy timestamp cũ
        old_timestamp = old_data[0]["timestamp"]

        # Lấy node_id cũ
        old_node_id = old_data[0].get("node_id", 1)

        # Conflict Resolution:
        # Timestamp lớn hơn sẽ thắng
        if data["timestamp"] > old_timestamp:

            db.update(data, User.id == data["id"])

        # Nếu timestamp bằng nhau
        elif data["timestamp"] == old_timestamp:

            # Node có node_id nhỏ hơn sẽ thắng
            if data["node_id"] < old_node_id:

                db.update(data, User.id == data["id"])

    # Replication dữ liệu sang node2
    try:

        requests.post(OTHER_NODE, json=data)

    except:

        # Nếu node2 đang offline
        print("Node2 is offline")

    return {
        "message": "inserted"
    }


# API nhận dữ liệu replicate từ node2
@app.route('/replicate', methods=['POST'])
def replicate():

    # Nhận dữ liệu từ node2
    data = request.json

    # Tìm dữ liệu cũ có cùng id
    old_data = db.search(User.id == data["id"])

    # Nếu chưa có dữ liệu thì insert
    if not old_data:

        db.insert(data)

    else:

        # Lấy timestamp cũ
        old_timestamp = old_data[0]["timestamp"]

        # Lấy node_id cũ
        old_node_id = old_data[0].get("node_id", 1)

        # Conflict Resolution:
        # Timestamp mới hơn sẽ thắng
        if data["timestamp"] > old_timestamp:

            db.update(data, User.id == data["id"])

        # Nếu timestamp bằng nhau
        elif data["timestamp"] == old_timestamp:

            # Node có node_id nhỏ hơn sẽ thắng
            if data["node_id"] < old_node_id:

                db.update(data, User.id == data["id"])

    return {
        "message": "replicated"
    }


# API lấy toàn bộ dữ liệu trong database
@app.route('/data', methods=['GET'])
def get_data():

    return {
        "data": db.all()
    }


# Khởi động node1 trên cổng 5000
app.run(port=5000)

"""
Ví dụ gọi API insert:

Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/insert" `
    -Method POST `
    -ContentType "application/json" `
    -Body '{"id":2,"name":"Tran Thi B","age":21}'
"""

