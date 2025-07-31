import json
import logging
from datetime import datetime
from typing import Annotated
from uuid import uuid4

from argon2 import PasswordHasher
from fastapi import APIRouter, Body, Depends, Query, Request, status
from pydantic import EmailStr
from redis import RedisError
from redis.asyncio import Redis

from common.broker import broker
from models.users import Users as UserModels
from repository.user import UserRepository
from schema.general import (
	AuthLinks,
	Embedded,
	Link,
	ResendEmailVerification,
	ResetPassword,
	ResetPasswordToken,
	Response,
	ResponseCreationUser,
	ResponseCreationUserData,
	UserCreation,
	UserSave,
	WelcomeUser,
)
from utils.db.async_db_conf import depend_db_annotated
from utils.dependencies.redis_cache import get_master, get_replica
from utils.exceptions import EntityDoesNotExistError, InvalidTokenError, ServiceError
from utils.fastapi.base_url import get_base_url
from utils.fastapi.utils import verify_token

router = APIRouter(prefix="/auth", tags=["auth"])

user_repository = UserRepository(model=UserModels)
ph = PasswordHasher()
logger = logging.getLogger("user_events")

REDIS_TOKEN_EXPIRY = 900
REDIS_PREFIX = "password-reset-token:"


def create_auth_links(request: Request, title: str, rel: str = "self") -> AuthLinks:
	"""
	Create HATEOAS links for authentication-related endpoints.

	Args:
		request (Request): The FastAPI request object
		title (str): The title for the self link
		rel (str, optional): The relation type for the self link. Defaults to "self"

	Returns:
		AuthLinks: A Pydantic model containing all authentication-related links
	"""
	base_url: str = get_base_url(request)

	return AuthLinks(
		self=Link(
			href=f"{base_url}{request.url.path}",
			rel=rel,
			method=request.method,
			title=title,
		),
		register=Link(
			href=f"{base_url}/users/auth/register",
			rel="register_new_user",
			method="POST",
			title="Register a new user account",
		),
		login=Link(
			href=f"{base_url}/users/auth/login",
			rel="user_login",
			method="POST",
			title="Log in to your account",
		),
		verify_email=Link(
			href=f"{base_url}/users/auth/verify-email",
			rel="verify_user_email",
			method="GET",
			title="Verify your email address",
		),
		resend_verification_email=Link(
			href=f"{base_url}/users/auth/resend-verification",
			rel="resend_verification_email",
			method="POST",
			title="Resend the email verification link",
		),
		request_reset_password=Link(
			href=f"{base_url}/users/auth/request-password-reset",
			rel="resend_verification_email",
			method="POST",
			title="Send request for password reset",
		),
		reset_password=Link(
			href=f"{base_url}/users/auth/reset-password",
			rel="resend_verification_email",
			method="POST",
			title="Reset password",
		),
	)


async def find_user_by_email(db: depend_db_annotated, email: EmailStr) -> UserModels:
	"""
	Asynchronously retrieves a user from the database by their email address.

	Args:
		db (depend_db_annotated): The database session
		email (EmailStr): The email address to search for

	Returns:
		UserModels: The found user model

	Raises:
		EntityDoesNotExistError: If no user is found with the specified email
	"""
	if (
		user := await user_repository.get_entity_by_args(
			column=UserModels.email, entity_schema_value=email, db=db
		)
	) is None:
		raise EntityDoesNotExistError(f"No user found with email: {email}")
	return user


@router.post(
	"/register",
	summary="Register new User",
	description="Register a new user",
	status_code=status.HTTP_201_CREATED,
	response_model=Response,
)
async def create_user(
	body: UserCreation, db: depend_db_annotated, request: Request
) -> Response:
	"""
	Register a new user in the system.

	Args:
		body (UserCreation): The user registration data
		db (depend_db_annotated): The database session
		request (Request): The FastAPI request object

	Returns:
		Response: Registration response with user data and HATEOAS links

	Publishes:
		- Event 'user.created' with welcome user data
	"""
	new_user = UserSave(
		**body.model_dump(exclude={"password", "password2"}),
		password_hash=ph.hash(body.password),
	)
	user = await user_repository.create_entity(new_user, db)
	data_user = ResponseCreationUserData(user=body.email, id=user.id)
	return_user_created = ResponseCreationUser(data=data_user)
	await broker.publish(
		message=WelcomeUser(**data_user.model_dump(), full_name=user.full_name),
		topic="user.created",
	)
	return Response(
		_embedded=Embedded(message=return_user_created),
		_links=create_auth_links(request, title="Register a new user account"),
	)


@router.get("/verify-email", response_model=Response)
async def verify_email(
	token: Annotated[str, Query()], db: depend_db_annotated, request: Request
) -> Response:
	"""
	Verify a user's email address using a verification token.

	Args:
		token (str): The email verification token
		db (depend_db_annotated): The database session
		request (Request): The FastAPI request object

	Returns:
		Response: Verification response with success message and HATEOAS links

	Raises:
		HTTPException: If token is invalid or expired
	"""
	id = verify_token(token_to_verify=token)
	await user_repository.update_entity(
		db=db,
		entity_id=id,
		filter=(),
		entity_schema={"email_verified": True, "updated_at": datetime.now()},  # type: ignore
	)
	return Response(
		_embedded=Embedded(message=f"The user {id} was verified"),
		_links=create_auth_links(request=request, title="Verify your email address"),
	)


@router.post(
	"/resend-verification",
	response_model=Response,
	status_code=status.HTTP_202_ACCEPTED,
)
async def resend_mail_verification(
	db: depend_db_annotated,
	request: Request,
	body: Annotated[ResendEmailVerification, Body()],
) -> Response:
	"""
	Resend email verification link to user.

	Args:
		db (depend_db_annotated): The database session
		request (Request): The FastAPI request object
		body (ResendEmailVerification): The email to resend verification to

	Returns:
		Response: Confirmation message with HATEOAS links

	Publishes:
		- Event 'user.verification_token.created' with user data

	Raises:
		EntityDoesNotExistError: If user email not found
	"""
	user = await find_user_by_email(db=db, email=body.email)
	if user.email_verified:
		return Response(
			_embedded=Embedded(
				message="This email has already been verified. Please log in."
			),
			_links=create_auth_links(
				request=request, title="Resend the email verification link"
			),
		)
	await broker.publish(
		message=WelcomeUser(user=user.email, id=user.id, full_name=user.full_name),
		topic="user.verification_token.created",
	)
	return Response(
		_embedded=Embedded(
			message="A verification email has been sent. Please check your inbox or spam folder."
		),
		_links=create_auth_links(
			request=request, title="Resend the email verification link"
		),
	)


@router.post(
	"/request-password-reset",
	response_model=Response,
	status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
	db: depend_db_annotated,
	request: Request,
	body: Annotated[ResendEmailVerification, Body()],
	redis: Annotated[Redis, Depends(get_master)],
) -> Response:
	"""
	Initiate a password reset process for a user by generating a reset token and sending a reset email.

	Args:
		db (depend_db_annotated): The database session dependency.
		request (Request): The FastAPI request object.
		body (ResendEmailVerification): The request body containing the user's email address.
		redis (Redis): Redis connection for storing the password reset token.

	Returns:
		Response: Confirmation message with HATEOAS links.

	Publishes:
		- Event 'user.reset_requested' with the reset token and user email.

	Raises:
		EntityDoesNotExistError: If no user is found with the provided email.
	"""
	user = await find_user_by_email(db=db, email=body.email)
	uuid_reset = uuid4()
	user_encode = json.dumps({"id": str(user.id)})
	try:
		await redis.setex(
			name=f"{REDIS_PREFIX}:{str(uuid_reset)}",
			value=user_encode,
			time=REDIS_TOKEN_EXPIRY,
		)
	except RedisError as redis_error:
		raise ServiceError("Cache service unavailable") from redis_error
	await broker.publish(
		message=ResetPasswordToken(token=str(uuid_reset), user=user.email),
		topic="user.reset_requested",
	)
	return Response(
		_embedded=Embedded(
			message="A reset password email has been sent. Please check your inbox or spam folder."
		),
		_links=create_auth_links(request=request, title="Reset password link"),
	)


@router.post("/reset-password", response_model=Response)
async def reset_password(
	db: depend_db_annotated,
	request: Request,
	redis: Annotated[Redis, Depends(get_replica)],
	body: ResetPassword,
) -> Response:
	redis_value: str = await redis.get(name=f"{REDIS_PREFIX}:{body.token}")
	if redis_value is None:
		raise InvalidTokenError(message="The token already expired or is incorrect")
	id: str = json.loads(redis_value)["id"]
	user = await user_repository.update_entity(
		db=db,
		entity_id=id,
		entity_schema={
			"password_hash": ph.hash(body.password),
			"login_attempts": 0,
			"updated_at": datetime.now(),
		},
	)
	await broker.publish(message=user.email, topic="user.password_reset")
	return Response(
		_embedded=Embedded(
			message="The password has been update succefully. Please login."
		),
		_links=create_auth_links(request=request, title="Reset password"),
	)
