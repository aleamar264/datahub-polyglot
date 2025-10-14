import icecream
import logfire
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from logfire import instrument_fastapi, instrument_system_metrics

from common.broker import kafka_router
from exception.handler_exception import CreateHandlerExceptions
from routes import kafka_user
from routes.auth import router as auth_router
from routes.profile import profile_router
from routes.users import router
from schema.users import HealthCheck
from utils.fastapi.observability.logfire_settings import _env
from utils.fastapi.observability.otel import server_request_hook

origin = ["*"]

app = FastAPI(
	docs_url="/docs",
	redoc_url="/redoc",
	version="0.0.1",
	root_path="/users".lower(),
	title="User Service API",
	description="This is the User Service API, which provides endpoints for user management.",
)


app.add_middleware(
	CORSMiddleware,
	allow_origins=origin,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(router)
app.include_router(profile_router)
app.include_router(auth_router)
app.include_router(kafka_router)


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
	return HealthCheck(status="OK")


CreateHandlerExceptions(app)

logfire.configure(
	service_name="user_services", token=_env.token, environment=_env.environment,
	send_to_logfire="if-token-present"
)

instrument_fastapi(
	app=app, capture_headers=True, server_request_hook=server_request_hook
)
instrument_system_metrics()
