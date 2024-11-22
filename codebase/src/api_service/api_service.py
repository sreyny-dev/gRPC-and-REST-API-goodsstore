from flask import Flask, jsonify, request
import grpc
import jwt
import datetime

import sys
import os

# Add the path to db_service folder
sys.path.append(os.path.abspath("../db_service"))

import goods_store_pb2
import goods_store_pb2_grpc
from local_manager import jwt_required

app = Flask(__name__)

# Connect to the gRPC DB service
channel = grpc.insecure_channel("localhost:50051")
stub = goods_store_pb2_grpc.DBServiceStub(channel)

@app.route("/api/v1")
def welcome():
    return jsonify({"message": "Welcome to the goods store API!"})

@app.route("/api/v1/products", methods=["GET"])
@jwt_required
def get_products():
    try:
        response = stub.GetProducts(goods_store_pb2.Empty())
        products = [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "price": product.price,
                "slogan": product.slogan,
                "stock": product.stock,
            }
            for product in response.products
        ]
        return jsonify(products)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error: product no found"}), 404
        return jsonify({"error: Internal server error"}), 500


@app.route("/api/v1/products/<int:product_id>", methods=["GET"])
def get_product_by_id(product_id):
    try:
        response = stub.GetProductById(goods_store_pb2.ProductId(id=product_id))
        product = {
            "id": response.id,
            "name": response.name,
            "description": response.description,
            "category": response.category,
            "price": response.price,
            "stock": response.stock,
        }
        return jsonify(product)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/v1/users/create", methods=["POST"])
def create_user():
    try:
        data = request.get_json()

        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required field'}), 400

        grpc_request = goods_store_pb2.CreateUserRequest(
            sid=data.get('sid', ''),  # Use sid if provided, or leave empty
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        grpc_response = stub.CreateUser(grpc_request)

        if grpc_response.sid:
            return jsonify({
                'sid': grpc_response.sid,
                'username': grpc_response.username,
                'email': grpc_response.email
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500

    except grpc.RpcError as e:
        return jsonify({'error': e.details()}), e.code().value[0]
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/v1/users/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        required_fields = ['username', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required field'}), 400

        grpc_request = goods_store_pb2.LoginRequest(
            username=data['username'],
            password=data['password']
        )
        grpc_response = stub.Login(grpc_request)

        if grpc_response.token:
            return jsonify({
                'token': grpc_response.token
            }), 201
        else:
            return jsonify({'error': grpc_response.error}), 401

    except grpc.RpcError as e:
        return jsonify({'error': e.details()}), e.code().value[0]
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/v1/users/update/<string:sid>", methods=["PUT"])
@jwt_required
def update_user(sid):
    data = request.json
    username = data.get('username', '')

    if not username:
        return jsonify({'error': 'No field provided to update'}), 400

    # Construct the gRPC request with the 'sid'
    update_request = goods_store_pb2.UpdateUserRequest(
        sid=sid,  # Include sid in the request
        username=username
    )
    try:
        update_user = stub.UpdateUser(update_request)

        return jsonify({
            'sid': update_user.sid,
            'username': update_user.username,
            'email': update_user.email
        }), 200
    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]



@app.route("/api/v1/users", methods=["GET"])
@jwt_required
def get_users():
    try:
        # Call the gRPC method
        response = stub.GetAllUsers(goods_store_pb2.Empty())

        # Correctly reference the userList field
        users = [
            {
                "id": user.sid,
                "name": user.username,
                "email": user.email,  # Corrected key
            }
            for user in response.userList  # Corrected field access
        ]
        return jsonify(users), 200
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "Users not found"}), 404
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/users/<string:sid>", methods=["GET"])
def get_user_by_sid(sid):
    try:
        response = stub.GetUserBySid(goods_store_pb2.UserSid(sid=sid))
        user = {
            "sid": response.sid,
            "username": response.username,
            "email": response.email,
        }
        return jsonify(user)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/users/id/<int:id>", methods=["GET"])
def get_user_by_id(id):
    try:
        response = stub.GetUserById(goods_store_pb2.UserId(id=id))
        user = {
            "sid": response.sid,
            "username": response.username,
            "email": response.email,
        }
        return jsonify(user)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/users/deactivate/<string:sid>", methods=["PUT"])
def deactivate_user(sid):
    try:
        deactivate_request = goods_store_pb2.deactivateRequest(sid=sid)

        stub.DeactivateUser(deactivate_request)
        return jsonify({'message': f'user with sid{sid} has been deactivated'}), 200
    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]

if __name__ == "__main__":
    app.run(port=8080)
