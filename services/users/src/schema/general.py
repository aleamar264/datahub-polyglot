from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field


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
	create_user: Link | None = Field(None, description="Link to create a new user")
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
					"create_user": {
						"href": "https://example.com/users/create",
						"rel": "create",
						"method": "POST",
						"title": "Create User",
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
						"href": "https://example.com/users/{id}/update",
						"rel": "update_user",
						"method": "PUT",
						"title": "Update User by ID",
					},
					"delete_user": {
						"href": "https://example.com/users/{id}/delete",
						"rel": "delete_user",
						"method": "DELETE",
						"title": "Delete User by ID",
					},
				}
			]
		}
	}


class User(BaseModel):
	id: UUID = Field(
		description="Unique identifier for the user", default_factory=uuid4
	)
	full_name: str = Field(..., max_length=255, description="Full name of the user")
	email: EmailStr
	created_at: datetime
	updated_at: datetime | None = None
	is_active: bool = False


class PaginatedResponse(BaseModel):
	"""
	Represents a paginated response for a collection of items.
	"""

	items: list[User] = Field(
		...,
		description="List of items in the current page",
	)
	cursor: str | None = Field(
		None, description="Cursor for pagination, used to fetch the next page"
	)
	links: LinkCollection = Field(..., description="Links for navigation between pages")
