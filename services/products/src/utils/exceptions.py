from collections.abc import Callable

from fastapi.requests import Request
from fastapi.responses import JSONResponse

from healthnexus.common.links import BASE_LINK
from healthnexus.schemas.error import ErrorMessage, Links, ReportExportTask


class ApiError(Exception):
	"""base exception class"""

	def __init__(
		self,
		message: str = "Service is unavailable",
	) -> None:
		self.message = message
		super().__init__(self.message)


def create_exception_handler(
	status_code: int,
	initial_detail: str,
) -> Callable[[Request, ApiError], JSONResponse]:
	detail = {"message": initial_detail}

	async def exception_handler(request: Request, exc: ApiError) -> JSONResponse:
		detail["message"] = exc.message
		# logger.error(exc)
		return JSONResponse(
			status_code=status_code,
			content=ReportExportTask(
				_embedded=ErrorMessage(**detail),
				_links=Links(self=f"{BASE_LINK}{request.url.path}"),
			).model_dump(by_alias=True),
		)

	return exception_handler  # type: ignore


class ServiceError(ApiError):
	"""failures in external services or APIs, like a database or a third-party service"""

	pass


class EntityDoesNotExistError(ApiError):
	"""database returns nothing"""

	pass


class EntityAlreadyExistsError(ApiError):
	"""conflict detected, like trying to create a resource that already exists"""

	pass


class AuthenticationFailed(ApiError):
	"""invalid authentication credentials"""

	pass


class InvalidTokenError(ApiError):
	"""invalid token"""

	pass


class GeneralError(ApiError):
	"""General Errors"""

	pass


class TooManyRequest(ApiError):
	"""Too many request"""

	pass


class InvalidParameter(ApiError):
	"""Invalid parameter"""

	pass
