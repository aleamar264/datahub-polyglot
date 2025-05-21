from concurrent import futures

import grpc
from fastapi import Request
from grpc_interceptor import ExceptionToStatusInterceptor

from protos.health_pb2 import SendHealth
from protos.health_pb2_grpc import GetHealtServicer, add_GetHealtServicer_to_server


class HealtServicer(GetHealtServicer):
	def Health(self, request: Request, context):
		"""
		## Perform a Health Check
		Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
		to ensure a robust container orchestration and management is in place. Other
		services which rely on proper functioning of the API service will not deploy if this
		endpoint returns any other HTTP status code except 200 (OK).
		Returns:
		    HealthCheck: Returns a JSON response with the health status
		"""
		return SendHealth(health="OK")


def serve():
	interceptors = [ExceptionToStatusInterceptor()]
	server = grpc.server(
		futures.ThreadPoolExecutor(max_workers=10), interceptors=interceptors
	)
	add_GetHealtServicer_to_server(HealtServicer(), server)
	server.add_insecure_port("[::]:50051")
	server.start()
	server.wait_for_termination()


if __name__ == "__main__":
	serve()
