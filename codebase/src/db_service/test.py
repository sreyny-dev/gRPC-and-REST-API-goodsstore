import goods_store_pb2
update_user_request = goods_store_pb2.UpdateUserRequest(
    sid="12113053",
    username="sreyny"
)

encoded_data = update_user_request.SerializeToString()

hex_representation = encoded_data.hex()
print("Encoded binary data (hexadecimal):", hex_representation)

decoded_update_user_request = goods_store_pb2.UpdateUserRequest()
decoded_update_user_request.ParseFromString(encoded_data)

# Print the decoded message
print("\nDecoded UpdateUserRequest message:")
print(f"SID: {decoded_update_user_request.sid}")
print(f"Username: {decoded_update_user_request.username}")
