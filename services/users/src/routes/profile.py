from typing import Any

from fastapi import APIRouter, Request, status

from schema.general import Link
from utils.fastapi.base_url import get_base_url

profile_router = APIRouter(
	prefix="/profile",
	tags=["profile"],
	responses={404: {"description": "Not found"}},
)


@profile_router.get(
	"/",
	response_model=dict[str, Any],
	status_code=status.HTTP_200_OK,
	openapi_extra={
		"summary": "Get Profile",
		"description": "Endpoint to get the profile information of the user.",
	},
)
async def root(request: Request) -> dict[str, Any]:
	"""
	## Get Profile
	Endpoint to get the profile information of the user.
	Returns:
		dict[str, Any]: Returns a dict response with the profile information
	"""
	base_url = get_base_url(request)
	return {
		"api_name:": "User Service API",
		"api_version": "0.0.1",
		"links": {
			"self": Link(
				href=f"{base_url}/users/", rel="self", method="GET", title="API Root"
			),
			"documentation": Link(
				href=f"{base_url}/users/docs",
				rel="documentation",
				method="GET",
				title="API Documentation",
			),
			"redoc": Link(
				href=f"{base_url}/users/redoc",
				rel="redoc",
				method="GET",
				title="API Redoc",
			),
			"healthcheck": Link(
				href=f"{base_url}/users/health",
				rel="healthcheck",
				method="GET",
				title="Health Check",
			),
			"profile": Link(
				href=f"{base_url}/users/profile/",
				rel="profile",
				method="GET",
				title="API Semantic",
			),
		},
	}


@profile_router.get(
	"/description", response_model=dict[str, Any], status_code=status.HTTP_200_OK
)
async def profile_description(request: Request) -> dict[str, Any]:
	"""
	## Get Profile Description
	Endpoint to get the profile description of the user.
	Returns:
		dict[str, Any]: Returns a dict response with the profile description
	"""
	return {
		"resources": {
			"users": {
				"description": "Manage user profiles, including creation, retrieval, updating, and deletion.",
				"properties": {
					"id": "Unique identifier for the user",
					"full_name": "Full name of the user",
					"email": "Email address of the user",
					"created_at": "Timestamp when the user was created",
					"updated_at": "Timestamp when the user was last updated",
					"is_active": "Indicates if the user is active",
				},
				"operations": {
					"user_creation": "Create a new user profile",
					"user_retrieval": "Retrieve user profile by ID",
					"user_update": "Update user profile by ID",
					"user_deletion": "Delete user profile by ID",
					"user_list": "List all user profiles",
				},
			}
		}
	}
