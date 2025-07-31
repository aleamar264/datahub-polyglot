from datetime import UTC, datetime
from typing import Any, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from common.role import Role
import re
from utils.exceptions import GeneralError


class Link(BaseModel):
	"""
	Represents a hyperlink with a URL and an optional label.
	"""

	href: str = Field(..., description="The URL of the link")
	rel: str = Field(
		...,
		description="The relationship type of the link, e.g., 'self', 'next', 'prev'",
	)
	method: str = Field(
		"GET", description="The HTTP method to use for the link, e.g., 'GET', 'POST'"
	)
	title: str | None = Field(
		None, description="An optional title for the link, providing additional context"
	)

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"href": "https://example.com",
					"rel": "self",
					"method": "GET",
					"title": "Example Link",
				}
			]
		}
	}


class LinkCollection(BaseModel):
	"""
	Represents a collection of links, typically used in API responses to provide
	navigation and related resources.
	"""

	self: Link = Field(
		...,
		description="Self link pointing to the current resource or endpoint",
	)
	next: Link | None = Field(None, description="Link to the next page of results")
	prev: Link | None = Field(None, description="Link to the previous page of results")
	first: Link | None = Field(None, description="Link to the first page of results")
	last: Link | None = Field(None, description="Link to the last page of results")

	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"self": {
						"href": "https://example.com",
						"rel": "self",
						"method": "GET",
						"title": "Example Link",
					},
					"next": {
						"href": "https://example.com/next",
						"rel": "self",
						"method": "GET",
						"title": "Example Link",
					},
					"prev": {
						"href": "https://example.com/prev",
						"rel": "self",
						"method": "GET",
						"title": "Example Link",
					},
					"last": {
						"href": "https://example.com/last",
						"rel": "self",
						"method": "GET",
						"title": "Example Link",
					},
					"first": {
						"href": "https://example.com/first",
						"rel": "self",
						"method": "GET",
						"title": "Example Link",
					},
				}
			]
		}
	}


class UserLinks(BaseModel):
	self: Link = Field(
		...,
		description="Self link pointing to the user's profile or details",
	)
	collection: Link | None = Field(None, description="Link to the collection of users")
	get_users: Link | None = Field(None, description="Link to get all users")
	get_user: Link | None = Field(None, description="Link to get a specific user by ID")
	update_user: Link | None = Field(
		None, description="Link to update a specific user by ID"
	)
	delete_user: Link | None = Field(
		None, description="Link to delete a specific user by ID"
	)
	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"self": {
						"href": "https://example.com/users/123",
						"rel": "self",
						"method": "GET",
						"title": "User Profile",
					},
					"collection": {
						"href": "https://example.com/users",
						"rel": "collection",
						"method": "GET",
						"title": "User Collection",
					},
					"get_users": {
						"href": "https://example.com/users",
						"rel": "get_users",
						"method": "GET",
						"title": "Get Users",
					},
					"get_user": {
						"href": "https://example.com/users/{id}",
						"rel": "get_user",
						"method": "GET",
						"title": "Get User by ID",
					},
					"update_user": {
						"href": "https://example.com/users/{id}",
						"rel": "update_user",
						"method": "PUT",
						"title": "Update User by ID",
					},
					"delete_user": {
						"href": "https://example.com/users/{id}",
						"rel": "delete_user",
						"method": "DELETE",
						"title": "Delete User by ID",
					},
					"soft_delete_user": {
						"href": "https://example.com/users/soft_delete/{id}",
						"rel": "soft_delete_user",
						"method": "POST",
						"title": "Soft delete user by ID",
					},
				}
			]
		}
	}


class UserBase(BaseModel):
	full_name: str = Field(..., max_length=255, description="Full name of the user")
	email: EmailStr


class UserAttributes(BaseModel):
	is_active: bool = Field(default=True)
	role: Role = Field(default=Role.USER)
	email_verified: bool = Field(default=False)
	last_login_at: datetime | None = None
	login_attempts: int = Field(default=0)
	updated_at: datetime | None = None
	created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class UserSave(UserBase, UserAttributes):
	password_hash: str = Field(...)


class UserResponse(UserBase, UserAttributes):
	id: UUID = Field(
		description="Unique identifier for the user", default_factory=uuid4
	)
	model_config = ConfigDict(from_attributes=True)


class CreationPassword(BaseModel):
	password: str = Field(...)
	password2: str = Field(...)

	@model_validator(mode="after")
	def validate_password(self) -> Self:
		pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+])[^\s]{8,20}$"
		if self.password != self.password2:
			raise GeneralError("Both password should be the same")
		if not re.fullmatch(pattern, self.password):
			raise GeneralError(
				"The password should be at leasts 8 long characters, and should contain\
					one o more special character (!@#$%^&*()_+)"
			)
		return self


class UserCreation(UserBase, CreationPassword): ...


class UserUpdate(BaseModel):
	is_active: bool = False


class PaginatedResponse(BaseModel):
	"""
	Represents a paginated response for a collection of items.
	"""

	items: list[UserResponse] = Field(
		...,
		description="List of items in the current page",
	)
	cursor: str | None = Field(
		None, description="Cursor for pagination, used to fetch the next page"
	)
	links: LinkCollection = Field(..., description="Links for navigation between pages")


class AuthLinks(BaseModel):
	self: Link = Field(
		...,
		description="Self link pointing to the user's profile or details",
	)
	register: Link | None = Field(None, description="Link to register user")
	verify_email: Link | None = Field(None, description="Link to verify the user email")
	resend_verification_email: Link | None = Field(
		None, description="Link to resend email verification"
	)
	request_reset_password: Link | None = Field(
		None, description="Link to request reset password"
	)
	reset_password: Link | None = Field(None, description="Link to reset password")
	login: Link | None = Field(None, description="Link to login")
	model_config = {
		"json_schema_extra": {
			"examples": [
				{
					"self": {
						"href": "https://example.com/users/auth/",
						"rel": "self",
						"method": "GET",
						"title": "User Profile",
					},
					"register": {
						"href": "https://example.com/users/auth/register",
						"rel": "auth_register",
						"method": "POST",
						"title": "Auth Registration",
					},
					"verify_email": {
						"href": "https://example.com/users/auth/verify-email",
						"rel": "verify_email",
						"method": "GET",
						"title": "Verify user by email",
					},
					"resend_verify_email": {
						"href": "https://example.com/users/auth/resend-verification",
						"rel": "resend_email_verification",
						"method": "POST",
						"title": "Resend email verification",
					},
					"reset_password": {
						"href": "https://example.com/users/auth//request-password-reset",
						"rel": "reset_password",
						"method": "POST",
						"title": "Reset Password",
					},
					"login": {
						"href": "https://example.com/users/auth/login",
						"rel": "auth_login",
						"method": "POST",
						"title": "Auth Login",
					},
				}
			]
		}
	}


class ResponseCreationUserData(BaseModel):
	user: str
	id: UUID


class ResponseCreationUser(BaseModel):
	data: ResponseCreationUserData


class WelcomeUser(ResponseCreationUserData):
	full_name: str


class ResendEmailVerification(BaseModel):
	email: EmailStr


class Embedded(BaseModel):
	message: Any


class Response(BaseModel):
	embedded: Embedded = Field(alias="_embedded", default=...)
	links: Any = Field(alias="_links", default=...)


class ResetPasswordToken(BaseModel):
	token: str
	user: EmailStr


class ResetPassword(CreationPassword):
	token: str
