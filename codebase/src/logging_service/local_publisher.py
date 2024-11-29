import time
from datetime import datetime
from confluent_kafka import Producer
import grpc
from concurrent import futures
import logging_service_pb2
import logging_service_pb2_grpc

# Kafka configuration
producer = Producer({'bootstrap.servers': 'kafka:9092'})
topic = 'log-channel'


class LoggingService(logging_service_pb2_grpc.LoggingServiceServicer):
  def StreamLogs(self, request_iterator, context):
    """Receive log messages via gRPC and produce them to Kafka"""
    for log_message in request_iterator:
      try:
        # Construct the log message
        msg = f"{log_message.timestamp} - {log_message.service}: {log_message.log}"

        # Produce the message to Kafka
        producer.produce(topic, msg.encode('utf-8'))
        producer.flush()

        print(f"Produced message to Kafka: {msg}")
      except Exception as e:
        print(f"Error producing message to Kafka: {e}")
        return logging_service_pb2.LogResponse(status="FAILURE")

    # Respond to the gRPC client after processing
    return logging_service_pb2.LogResponse(status="SUCCESS")


def serve():
  """Start the gRPC server"""
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  logging_service_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
  server.add_insecure_port('[::]:50052')  # Change port if necessary
  print("Logging service is running on port 50052...")
  server.start()
  try:
    server.wait_for_termination()
  except KeyboardInterrupt:
    print("\nLogging service shutting down...")


if __name__ == "__main__":
  serve()