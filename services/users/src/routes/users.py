from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Query, Request, status

from models.users import Users as UserModels
from repository.user import UserRepository
from schema.general import Link, UserLinks, UserResponse, UserUpdate
from schema.users import FilterParameters, PaginationResponse, Response
from utils.db.async_db_conf import depend_db_annotated
from utils.fastapi.base_url import get_base_url

router = APIRouter(prefix="/users", tags=["users"])
user_repository = UserRepository(model=UserModels)


def create_user_links(rel: str, request: Request, title: str) -> UserLinks:
	base_url: str = get_base_url(request)

	return UserLinks(
		self=Link(
			href=f"{base_url}{request.url.path}",
			rel=rel,
			method=request.method,
			title=title,
		),
		collection=Link(
			href=f"{base_url}/users",
			rel="User",
			method="GET/POST/PUT/DELETE",
			title="Actions for the users",
		),
		delete_user=Link(
			href=f"{base_url}/users/user_uuid",
			rel="DELETE_USER",
			method="DELETE",
			title="Delete a specific user",
		),
		get_user=Link(
			href=f"{base_url}/users/user_uuid",
			rel="GET_USERS",
			method="GET",
			title="Retrieve a specific user",
		),
		get_users=Link(
			href=f"{base_url}/users/",
			rel="GET_USER",
			method="GET",
			title="Retrieve all the users",
		),
		update_user=Link(
			href=f"{base_url}/users/user_uuid",
			rel="UPDATE_USER",
			method="POST",
			title="Update a specific user",
		),
	)


def to_user_response(user: UserModels) -> UserResponse:
	return UserResponse(**user.__dict__)


@router.get(
	"/",
	summary="Get Users",
	description="Get all users",
	status_code=status.HTTP_200_OK,
	response_model=PaginationResponse,
)
async def get_users(
	filter_query: Annotated[FilterParameters, Query()],
	db: depend_db_annotated,
	request: Request,
) -> PaginationResponse:
	items, count = await user_repository.get_entity_pagination(
		db=db,
		filter=(),  # type: ignore
		limit=filter_query.limit,
		offset=filter_query.offset,
		order_by=filter_query.sort,
	)
	return PaginationResponse(
		result=[to_user_response(item) for item in items],
		_links=create_user_links(
			request=request, title="Retrieve a list of users", rel="self"
		),
		max_items=count,
	)


@router.get(
	"/{user_uuid}",
	response_model=Response,
	description="Get a specific user by UUID",
	status_code=status.HTTP_200_OK,
)
async def get_user(
	user_uuid: str, db: depend_db_annotated, request: Request
) -> Response:
	user = await user_repository.get_entity_by_id(entity_id=user_uuid, db=db)
	return Response(
		result=to_user_response(user),
		_links=create_user_links(
			request=request, title="Retrieve specific user", rel="self"
		),
	)


@router.put(
	"/{user_uuid}",
	summary="Update User",
	description="Update a specific user by UUID",
	status_code=status.HTTP_200_OK,
)
async def update_user(
	body: UserUpdate, user_uuid: str, request: Request, db: depend_db_annotated
) -> Response:
	user = await user_repository.update_entity(
		entity_id=user_uuid,
		db=db,
		entity_schema={**body.model_dump(), **{"updated_at": datetime.now(UTC)}},
		filter=(),
	)
	return Response(
		result=to_user_response(user),
		_links=create_user_links(request=request, title="Update user", rel="self"),
	)


@router.delete(
	"/{user_uuid}",
	summary="Delete User",
	description="Delete a specific user by UUID",
	status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_uuid: str, db: depend_db_annotated) -> None:
	await user_repository.delete_entity(entity_id=user_uuid, db=db, filter=())


@router.post(
	"/soft_delete/{user_uuid}",
	summary="Soft Delete",
	description="Soft Delete (only disable from access)",
	status_code=status.HTTP_200_OK,
)
async def soft_delete(user_id: str, db: depend_db_annotated) -> Response:
	body: dict[str, bool] = {"is_active": False}
	user = await user_repository.update_entity(
		entity_id=user_id, entity_schema=body, db=db, filter=()
	)
	return Response(
		result=to_user_response(user),
		_links=create_user_links(request=request, title="Soft Delete", rel="self"),
	)
