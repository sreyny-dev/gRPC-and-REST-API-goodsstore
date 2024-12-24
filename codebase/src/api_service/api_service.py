import time
from flask import Flask, jsonify, request
import grpc
import logging

# Ensure Flask writes all logs to stdout
import sys
import os

# Add the path to db_service folder
# sys.path.append(os.path.abspath("../db_service"))
# sys.path.append(os.path.abspath("../logging_service"))
import goods_store_pb2
import goods_store_pb2_grpc
from local_manager import jwt_required
import logging_service_pb2
import logging_service_pb2_grpc

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG
app.logger.addHandler(logging.StreamHandler(sys.stdout))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Connect to the gRPC DB service
channel = grpc.insecure_channel("db-service:50051")
# channel = grpc.insecure_channel("localhost:50051")
stub = goods_store_pb2_grpc.DBServiceStub(channel)

logging_chanel = grpc.insecure_channel("logging-service:50052")
# logging_chanel = grpc.insecure_channel("localhost:50052")
logging_stub = logging_service_pb2_grpc.LoggingServiceStub(logging_chanel)


def send_log(message):
    try:
        log_message = logging_service_pb2.LogMessage(
            log=message,
            service="API Service",
            timestamp=int(time.time())  # Convert timestamp to Unix epoch seconds
        )
        # Send a stream of log messages to the Logging Service
        logging_stub.StreamLogs(iter([log_message]))  # Use `iter([log_message])` to send a list of one message at a time
        app.logger.debug("Sent log message to logging service!")
    except Exception as e:
        app.logger.error(f"Failed to send log to logging service: {str(e)}")


@app.route("/api/v1")
def welcome():
    """Handle welcome route"""
    message = "Accessed the welcome endpoint"
    send_log(message)  # Send log to logging service
    app.logger.debug(message)  # Also log locally
    return jsonify({"message": "Welcome to the goods store API!"})

@app.route("/api/v1/products", methods=["GET"])
@jwt_required
def get_products():
    try:
        username = request.user.get("username")
        send_log(f"User '{username}' is fetching all products")

        response = stub.GetProducts(goods_store_pb2.Empty())
        products = [
            {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "price": round(product.price, 2),
                "slogan": product.slogan,
                "stock": product.stock,
            }
            for product in response.products
        ]
        return jsonify(products)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            send_log(f"User '{username}' fetched all products, but not found")
            return jsonify({"error: product no found"}), 404
        send_log("Internal Server Error")
        return jsonify({"error: Internal server error"}), 500


@app.route("/api/v1/products/<int:product_id>", methods=["GET"])
@jwt_required
def get_product_by_id(product_id):
    try:

        username = request.user.get("username")
        send_log(f"User '{username}' is fetching product by product id")

        response = stub.GetProductById(goods_store_pb2.ProductId(id=product_id))
        product = {
            "id": response.id,
            "name": response.name,
            "description": response.description,
            "category": response.category,
            "price": round(response.price, 2),
            "stock": response.stock,
        }
        return jsonify(product)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            send_log(f"User '{username}' is fetching product by product id, product not found")
            return jsonify({"error": "Product not found"}), 404
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/users/create", methods=["POST"])
def create_user():
    try:

        send_log("Create User endpoint is being called")
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
            send_log(f"User '{data['username']}' is created")
            return jsonify({
                'sid': grpc_response.sid,
                'username': grpc_response.username,
                'email': grpc_response.email
            }), 201
        else:
            send_log(f"Fail to create user '{data['username']}'")
            return jsonify({'error': 'Failed to create user'}), 500
    except grpc.RpcError as e:
        error_message = e.details()
        grpc_status_code = e.code().name
        send_log(f"error: {grpc_status_code} - {error_message}")
        return jsonify({'error': e.details()}), e.code().value[0]
    except Exception as e:
        send_log(f"Internal server error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/api/v1/users/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        # Check for required fields
        required_fields = ['username', 'password']
        if not all(field in data for field in required_fields):
            send_log("Missing required fields in login request")
            return jsonify({'error': 'Missing required field'}), 400

        # Send login request to gRPC server
        grpc_request = goods_store_pb2.LoginRequest(
            username=data['username'],
            password=data['password']
        )
        grpc_response = stub.Login(grpc_request)

        if grpc_response.token:
            send_log(f"User {data['username']} successfully logged in")
            return jsonify({
                'token': grpc_response.token
            }), 201
        else:
            send_log(f"Failed login attempt for user {data['username']}")
            return jsonify({'error': grpc_response.error}), 401

    except grpc.RpcError as e:
        # Handle specific gRPC errors
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            send_log(f"Unauthenticated login attempt for user {data.get('username')}")
            return jsonify({'error': 'Invalid username or password'}), 401
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            send_log(f"Invalid login request for user {data.get('username')}")
            return jsonify({'error': 'Invalid login request'}), 400
        else:
            # Generic fallback for unexpected gRPC errors
            send_log("Unexpected gRPC error during login")
            return jsonify({'error': 'Internal server error'}), 500

    except Exception as e:
        send_log("Internal server error during login")
        return jsonify({'error': 'Internal server error'}), 500



@app.route("/api/v1/users/update/<string:sid>", methods=["PUT"])
@jwt_required
def update_user(sid):

    data = request.json
    username = data.get('username', '')
    send_log(f"'{username}' access update user endpoint")


    if not username:
        return jsonify({'error': 'No field provided to update'}), 400

    # Construct the gRPC request with the 'sid'
    update_request = goods_store_pb2.UpdateUserRequest(
        sid=sid,  # Include sid in the request
        username=username
    )
    try:
        update_user = stub.UpdateUser(update_request)
        send_log(f"update user '{update_user.sid}' to username '{update_user.username}' successfully")
        return jsonify({
            'sid': update_user.sid,
            'username': update_user.username,
            'email': update_user.email
        }), 200
    except grpc.RpcError as e:
        error_message = e.details()
        grpc_status_code = e.code().name
        send_log(f"error: {grpc_status_code} - {error_message}")
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]

@app.route("/api/v1/users", methods=["GET"])
@jwt_required
def get_users():
    try:
        username = request.user.get("username")
        send_log(f"User '{username}' fetching all users")
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
@jwt_required
def get_user_by_sid(sid):
    try:
        username = request.user.get("username")

        send_log(f"User '{username}' accessed get user by sid endpoint")

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
@jwt_required
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
@jwt_required
def deactivate_user(sid):
    try:
        username = request.user.get("username")
        send_log(f"User '{username}' access deactivate user endpoint")

        deactivate_request = goods_store_pb2.deactivateRequest(sid=sid)
        stub.DeactivateUser(deactivate_request)
        return jsonify({'message': f'user with sid{sid} has been deactivated'}), 200
    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]

@app.route("/api/v1/products/create", methods=["POST"])
@jwt_required
def create_product():
    try:
        username = request.user.get("username")
        send_log(f"User '{username}' access create product endpoint")

        data = request.get_json()

        required_fields = ['name', 'description', 'category','price', 'slogan', 'stock']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required field'}), 400

        grpc_request = goods_store_pb2.CreateProductRequest(
            name=data.get('name', ''),  # Use sid if provided, or leave empty
            description=data['description'],
            category=data['category'],
            price=data['price'],
            slogan=data['slogan'],
            stock=data['stock']
        )
        grpc_response = stub.CreateProduct(grpc_request)

        if grpc_response.id:
            return jsonify({
                'name': grpc_response.name,
                'description': grpc_response.description,
                'category': grpc_response.category,
                'price': round(grpc_response.price, 2),
                'slogan': grpc_response.slogan,
                'stock': grpc_response.stock
            }), 201
        else:
            return jsonify({'error': 'Failed to create product'}), 500

    except grpc.RpcError as e:
        return jsonify({'error': e.details()}), e.code().value[0]
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/v1/products/update/<int:product_id>", methods=["PUT"])
@jwt_required
def update_product(product_id):
    username = request.user.get("username")
    send_log(f"User '{username}' access update product endpoint")
    data = request.json

    # Initialize the fields to update
    update_fields = {}

    # Collect fields from the request
    if 'name' in data:
        update_fields['name'] = data['name']
    if 'description' in data:
        update_fields['description'] = data['description']
    if 'category' in data:
        update_fields['category'] = data['category']
    if 'price' in data:
        update_fields['price'] = data['price']
    if 'slogan' in data:
        update_fields['slogan'] = data['slogan']
    if 'stock' in data:
        update_fields['stock'] = data['stock']

    # Check if there are no fields to update
    if not update_fields:
        return jsonify({'error': 'No fields provided to update'}), 400

    # Construct the gRPC request with the product ID
    update_request = goods_store_pb2.UpdateProductRequest(
        id=product_id,
        **update_fields  # Unpack dictionary to pass as keyword arguments
    )

    try:
        # Call the gRPC UpdateProduct method
        updated_product = stub.UpdateProduct(update_request)

        return jsonify({
            'id': updated_product.id,
            'name': updated_product.name,
            'description': updated_product.description,
            'category': updated_product.category,
            'price': round(updated_product.price, 2),
            'slogan': updated_product.slogan,
            'stock': updated_product.stock
        }), 200
    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]


@app.route("/api/v1/orders/place", methods=["POST"])
@jwt_required
def place_order():
    username = request.user.get("username")
    send_log(f"User '{username}' access place order endpoint")

    data = request.json

    # Validate input
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not user_id or not product_id or not quantity:
        return jsonify({'error': 'Missing required fields: user_id, product_id, quantity'}), 400

    # Construct the gRPC request
    order_request = goods_store_pb2.OrderRequest(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity
    )

    try:
        # Call the gRPC PlaceOrder method
        order_response = stub.PlaceOrder(order_request)

        return jsonify({
            'order_id': order_response.order_id,
            'user_id': order_response.user_id,
            'product_id': order_response.product_id,
            'quantity': order_response.quantity,
            'total_price': order_response.total_price
        }), 201

    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]


@app.route("/api/v1/orders", methods=["GET"])
@jwt_required
def get_all_orders():
    username = request.user.get("username")
    send_log(f"User '{username}' access get all order endpoint")

    # Construct the gRPC request
    empty_request = goods_store_pb2.Empty()

    try:
        # Call the gRPC GetAllOrder method
        order_response_list = stub.GetAllOrder(empty_request)

        # Convert the order response to a JSON format
        orders = [{
            'order_id': order.order_id,
            'user_id': order.user_id,
            'product_id': order.product_id,
            'quantity': order.quantity,
            'total_price': order.total_price
        } for order in order_response_list.order_list]

        return jsonify(orders), 200

    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]


@app.route("/api/v1/orders/id/<int:id>", methods=["GET"])
@jwt_required
def get_order_by_id(id):
    username = request.user.get("username")
    send_log(f"User '{username}' access get order by id endpoint")

    try:
        order_id_request = goods_store_pb2.OrderId(id=id)
        response = stub.GetOrderById(order_id_request)
        order = {
            "order_id": response.order_id,
            "user_id": response.user_id,
            "product_id": response.product_id,
            "quantity": response.quantity,
            "total_price": response.total_price
        }
        return jsonify(order), 200
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "Order not found"}), 404
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/v1/orders/user_id/<int:user_id>", methods = ["GET"])
@jwt_required
def get_order_by_user_id(user_id):
    try:

        username = request.user.get("username")
        send_log(f"User '{username}' access get orders by user endpoint")


        user_request = goods_store_pb2.UserId(id=user_id)
        order_response_list = stub.GetOrderByUser(user_request)

        orders = [{
            'order_id': order.order_id,
            'user_id': order.user_id,
            'product_id': order.product_id,
            'quantity': order.quantity,
            'total_price': order.total_price
        } for order in order_response_list.order_list]

        return jsonify(orders), 200

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            return jsonify({"error": "Order not found"}), 404
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/v1/orders/cancel/<int:id>", methods=["PUT"])
@jwt_required
def cancel_order(id):
    try:
        username = request.user.get("username")
        send_log(f"User '{username}' access cancel order endpoint")

        cancel_request = goods_store_pb2.OrderId(id=id)
        stub.CancelOrderById(cancel_request)
        return jsonify({'message': f'order with id={id} has been canceled'}), 200
    except grpc.RpcError as e:
        return jsonify({'error': f"gRPC error: {e.details()}"}), e.code().value[0]





if __name__ == "__main__":
    # app.run(port=8080)
    app.run(debug=True, host='0.0.0.0', port=8081)

