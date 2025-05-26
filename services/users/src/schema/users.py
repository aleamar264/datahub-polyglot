from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
	status: str


class FilterParameters(BaseModel):
	"""
	Represents filter parameters for querying resources.
	"""

	limit: int = 10
	cursor: str | None = Field(None, description="Cursor for pagination")
	sort: str = Field(
		"asc",
		description="Sort order, either 'asc' or 'desc', this sort is applied to the 'created_at' field",
	)

	model_config = {"json_schema_extra": {"example": {"limit": 10, "cursor": "abc123"}}}
