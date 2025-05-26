from typing import Annotated

from fastapi import APIRouter, Query, status

from schema.users import FilterParameters

router = APIRouter(tags=["users"], prefix="/")


@router.get(
	"/",
	summary="Get Users",
	description="Get all users",
	status_code=status.HTTP_200_OK,
)
async def get_users(filter_query: Annotated[FilterParameters, Query()]) -> None: ...


@router.get(
	"/{user_uuid}",
	description="Get a specific user by UUID",
	status_code=status.HTTP_200_OK,
)
async def get_user(user_uuid: str) -> None: ...


@router.post(
	"/",
	summary="Create User",
	description="Create a new user",
	status_code=status.HTTP_201_CREATED,
)
async def create_user() -> None: ...


@router.put(
	"/{user_uuid}",
	summary="Update User",
	description="Update a specific user by UUID",
	status_code=status.HTTP_200_OK,
)
async def update_user(user_uuid: str) -> None: ...


@router.delete(
	"/{user_uuid}",
	summary="Delete User",
	description="Delete a specific user by UUID",
	status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_uuid: str) -> None: ...
