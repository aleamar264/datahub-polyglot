import logging
from typing import Annotated

from argon2 import PasswordHasher
from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse

from common.broker import broker
from models.users import Users as UserModels
from repository.user import UserRepository
from schema.general import (
	AuthLinks,
	Link,
	ResponseCreationUser,
	ResponseCreationUserData,
	UserCreation,
	UserSave,
	WelcomeUser,
)
from utils.db.async_db_conf import depend_db_annotated
from utils.fastapi.base_url import get_base_url
from utils.fastapi.utils import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

user_repository = UserRepository(model=UserModels)
ph = PasswordHasher()
logger = logging.getLogger("user_events")


def create_auth_links(request: Request, title: str, rel: str):
	base_url: str = get_base_url(request)

	return AuthLinks(
		self=Link(
			href=f"{base_url}{request.url.path}",
			rel=rel,
			method=request.method,
			title=title,
		),
		register=Link(
			href=f"{base_url}/auth/register",
			rel="REGISTER_USER",
			method="POST",
			title="Register user",
		),
		login=Link(
			href=f"{base_url}/auth/login",
			rel="LOGIN_USER",
			method="POST",
			title="Login user",
		),
	)


@router.post(
	"/register",
	summary="Register new User",
	description="Register a new user",
	status_code=status.HTTP_201_CREATED,
	response_model=ResponseCreationUser,
)
async def create_user(
	body: UserCreation, db: depend_db_annotated, request: Request
) -> ResponseCreationUser:
	new_user = UserSave(
		**body.model_dump(exclude={"password", "password2"}),
		password_hash=ph.hash(body.password),
	)
	user = await user_repository.create_entity(new_user, db)
	data_user = ResponseCreationUserData(user=body.email, id=user.id)
	return_user_created = ResponseCreationUser(message="User created", data=data_user)
	await broker.publish(
		message=WelcomeUser(**data_user.model_dump(), full_name=user.full_name),
		topic="user.created",
	)
	return return_user_created


@router.get("/verify-email", response_class=JSONResponse)
async def verify_email(
	token: Annotated[str, Query()], db: depend_db_annotated, request: Request
) -> JSONResponse:
	id = verify_token(token_to_verify=token)
	await user_repository.update_entity(
		db=db,
		entity_id=id,
		filter=(),
		entity_schema={"email_verified": True},  # type: ignore
	)
	return JSONResponse(
		content=f"The user {id} was verified", status_code=status.HTTP_200_OK
	)
