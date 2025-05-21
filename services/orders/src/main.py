import grpc
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from protos import health_pb2, health_pb2_grpc
from routes.orders import router
from schema.orders import HealthCheck

origin = ["*"]
app = FastAPI(
	docs_url="/docs",
	redoc_url="/redoc",
	version="0.0.1",
	root_path="/orders".lower(),
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=origin,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(router)


@app.get(
	"/health",
	tags=["healthcheck"],
	summary="Perform a Health Check",
	response_description="Return HTTP Status Code 200 (OK)",
	status_code=status.HTTP_200_OK,
	response_model=HealthCheck,
)
def get_health() -> HealthCheck:
	"""
	## Perform a Health Check
	Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
	to ensure a robust container orchestration and management is in place. Other
	services which rely on proper functioning of the API service will not deploy if this
	endpoint returns any other HTTP status code except 200 (OK).
	Returns:
	    HealthCheck: Returns a JSON response with the health status
	"""
	with grpc.insecure_channel("localhost:50051") as channel:
		stub = health_pb2_grpc.GetHealtStub(channel)
		request = health_pb2.SendHealth(health="Ok")
		response = stub.Health(request)
		return HealthCheck(status=response.health)
