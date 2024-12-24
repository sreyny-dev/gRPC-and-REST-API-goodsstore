import grpc
from concurrent import futures
import logging
from datetime import datetime
from confluent_kafka import Producer
import logging_service_pb2
import logging_service_pb2_grpc

# Kafka configuration
producer = Producer({'bootstrap.servers': 'kafka:9092'})
topic = 'log-channel'

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

class LoggingService(logging_service_pb2_grpc.LoggingServiceServicer):
    def StreamLogs(self, request_iterator, context):
        """Process incoming log messages and send them to Kafka"""
        try:
            for log_message in request_iterator:
                # Serialize and send each message
                serialized_message = log_message.SerializeToString()
                producer.produce(topic, value=serialized_message)
                logger.info(f"Sent log message to Kafka: {log_message}")
            producer.flush()
            return logging_service_pb2.LogResponse(status="SUCCESS")
        except Exception as e:
            logger.error(f"Failed to send logs: {e}")
            return logging_service_pb2.LogResponse(status="FAILURE")


def serve():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging_service_pb2_grpc.add_LoggingServiceServicer_to_server(LoggingService(), server)
    server.add_insecure_port('[::]:50052')  # Change port if necessary
    logger.info("Logging service is running on port 50052...")
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Logging service shutting down...")

if __name__ == "__main__":
    serve()