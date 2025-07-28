from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from .general import UserLinks, UserResponse


class HealthCheck(BaseModel):
	status: str


class FilterParameters(BaseModel):
	"""
	Represents filter parameters for querying resources.
	"""

	limit: int = 10
	offset: int = 0
	sort: str = Field(
		"asc",
		description="Sort order, either 'asc' or 'desc', this sort is applied to the 'created_at' field",
	)

	model_config = {
		"json_schema_extra": {"example": {"limit": 10, "sort": "asc", "offset": 0}}
	}


class Response(BaseModel):
	result: UserResponse | list[UserResponse]
	links: UserLinks = Field(..., alias="_links")


class PaginationResponse(Response):
	max_items: int = Field(..., description="Max items in the database")


class KafkaEvents(BaseModel):
	event_type: str
	event_version: float
	timestampt: datetime
	data: Any
	source: str
