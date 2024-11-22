# import psycopg2
# from psycopg2 import pool   # this line is oddly necessary
# from pprint import pprint
#
"""
Connection pooling: https://www.psycopg.org/docs/pool.html
Connection: https://www.psycopg.org/docs/connection.html
Cursor: https://www.psycopg.org/docs/cursor.html
"""
import datetime

#
# # Create a SimpleConnectionPool for a single-threaded application
# simple_pool = psycopg2.pool.SimpleConnectionPool(
#   minconn=1,
#   maxconn=10,
#   user="dncc",
#   # maybe password need to be read from environment variable for security issue
#   password="dncc",
#   host="localhost",
#   port="5432",
#   database="goodsstore"
# )
#
# # Single-threaded usage of connections
# try:
#   # Get a connection from the pool
#   conn = simple_pool.getconn()
#
#   # Perform a database operation
#   with conn.cursor() as cursor:
#     cursor.execute("SELECT * FROM products;")
#     results = cursor.fetchall()
#     pprint(results)
#     # Commit only for INSERT/UPDATE/DELETE operations.
#     # cursor.execute("INSERT INTO products (name, stock, price) VALUES (%s, %s, %s) RETURNING id", ("SUSTech Pixel Map", 300, 3.99))
#     # results = cursor.fetchone()
#     # pprint(results)
#     # conn.commit()
#     # Rollback when sth is wrong.
#     # conn.rollback()
# finally:
#   # Return the connection to the pool
#   simple_pool.putconn(conn)
#
# # Closing all connections in the pool
# simple_pool.closeall()


import grpc
from concurrent import futures

from flask import request, jsonify
from psycopg2 import pool
import goods_store_pb2
import goods_store_pb2_grpc
import bcrypt
import jwt
import datetime
from functools import wraps
from werkzeug.exceptions import Unauthorized

# Connection pool configuration
DB_CONFIG = {
    "dbname": "goodsstore",
    "user": "dncc",
    "password": "dncc",
    "host": "localhost",
    "port": "1111",
}

# Initialize a connection pool
connection_pool = pool.SimpleConnectionPool(
    minconn=1,  # Minimum number of connections in the pool
    maxconn=10,  # Maximum number of connections in the pool
    **DB_CONFIG
)

# JWT Configuration
SECRET_KEY = "crazy-grpc"  # Use a secure key in production
ALGORITHM = "HS256"
JWT_EXP_DELTA_SECONDS = 3600


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # Check if the token is passed in the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]  # Extract token part
        if not token:
            raise Unauthorized("Token is missing!")

        try:
            # Decode and verify the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # You can add the user details in the request context if needed
            request.user = payload
        except jwt.ExpiredSignatureError:
            raise Unauthorized("Token has expired!")
        except jwt.InvalidTokenError:
            raise Unauthorized("Invalid token!")

        return f(*args, **kwargs)

    return decorated_function


class DBService(goods_store_pb2_grpc.DBServiceServicer):
    def GetProducts(self, request, context):
        conn = None
        try:
            # Get a connection from the pool
            conn = connection_pool.getconn()
            cursor = conn.cursor()

            # Query to fetch all products
            cursor.execute("SELECT id, name, description, category, price, slogan, stock FROM products;")
            products = [
                goods_store_pb2.ProductResponse(
                    id=row[0], name=row[1], description=row[2], category=row[3], price=row[4], slogan=row[5], stock=row[6]
                )
                for row in cursor.fetchall()
            ]

            # Close the cursor
            cursor.close()

            # Return the list of products
            return goods_store_pb2.ProductListResponse(products=products)

        except Exception as e:
            # Handle and log the exception
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return goods_store_pb2.ProductListResponse()
        finally:
            if conn:
                # Return the connection back to the pool
                connection_pool.putconn(conn)

    def GetProductById(self, request, context):
        conn = None
        try:
            # Get a connection from the pool
            conn = connection_pool.getconn()
            cursor = conn.cursor()

            # Query to fetch a product by ID
            cursor.execute(
                "SELECT id, name, description, category, price, slogan, stock FROM products WHERE id = %s;",
                (request.id,),
            )
            row = cursor.fetchone()

            # Close the cursor
            cursor.close()

            if row:
                # If the product is found, return it
                return goods_store_pb2.ProductResponse(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    category=row[3],
                    price=row[4],
                    slogan=row[5],
                    stock=row[6]
                )
            else:
                # If no product is found, return NOT_FOUND
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Product not found")
                return goods_store_pb2.ProductResponse()

        except Exception as e:
            # Handle and log the exception
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return goods_store_pb2.ProductResponse()
        finally:
            if conn:
                # Return the connection back to the pool
                connection_pool.putconn(conn)

    import uuid

    def CreateUser(self, request, context):
        conn = None
        try:
            conn = connection_pool.getconn()
            cursor = conn.cursor()

            insert_query = """
            INSERT INTO users (sid, username, email, password_hash)
            VALUES (%s, %s, %s, %s)
            RETURNING sid, username, email
            """
            password_hash = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()

            cursor.execute(
                insert_query,
                (request.sid, request.username, request.email, password_hash)
            )

            user_row = cursor.fetchone()
            conn.commit()
            cursor.close()

            if user_row:
                return goods_store_pb2.UserInfo(
                    sid=user_row[0],
                    username=user_row[1],
                    email=user_row[2]
                )
            else:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create user")
                return goods_store_pb2.UserInfo()

        except Exception as e:
            if conn:
                connection_pool.putconn(conn)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return goods_store_pb2.UserInfo()

    def Login(self, request, context):
        conn = None
        try:
            # Get a connection from the pool
            conn = connection_pool.getconn()
            cursor = conn.cursor()

            # Query to fetch user by username
            cursor.execute(
                "SELECT sid, username, email, password_hash FROM users WHERE username = %s;",
                (request.username,)
            )
            user_row = cursor.fetchone()

            # Close the cursor
            cursor.close()

            if user_row:
                # Check if the provided password matches the hashed password in the database
                if bcrypt.checkpw(request.password.encode(), user_row[3].encode()):
                    # Create JWT token
                    payload = {
                        "sid": user_row[0],
                        "username": user_row[1],
                        "email": user_row[2],
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
                    }
                    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

                    return goods_store_pb2.LoginResponse(token=token)

                else:
                    context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                    context.set_details("Invalid credentials")
                    return goods_store_pb2.LoginResponse(error="Invalid credentials")
            else:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("User not found")
                return goods_store_pb2.LoginResponse(error="User not found")

        except Exception as e:
            if conn:
                connection_pool.putconn(conn)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return goods_store_pb2.LoginResponse(error="Internal server error")
        finally:
            if conn:
                # Return the connection back to the pool
                connection_pool.putconn(conn)


# Start the gRPC server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    goods_store_pb2_grpc.add_DBServiceServicer_to_server(DBService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("DB Service running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        serve()
    finally:
        # Close all connections in the pool when the server is stopped
        connection_pool.closeall()
