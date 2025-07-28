from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum as sql_enum
from sqlalchemy.dialects.postgresql import BOOLEAN, INTEGER, TIMESTAMP, VARCHAR
from sqlalchemy.dialects.postgresql import UUID as pg_uuid
from sqlalchemy.orm import Mapped, mapped_column

from common.role import Role
from utils.db.general import MixInNameTable

from .base import Base


class Users(Base, MixInNameTable):
	id: Mapped[UUID] = mapped_column(
		pg_uuid(as_uuid=True), primary_key=True, nullable=False, default=uuid4
	)
	full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=False)
	email: Mapped[str] = mapped_column(
		VARCHAR(255), nullable=False, unique=True, index=True
	)
	password_hash: Mapped[str] = mapped_column(VARCHAR(255), unique=False)
	role: Mapped[str] = mapped_column(sql_enum(Role), index=True)
	email_verifies: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC), index=True
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True, default=None
	)
	is_active: Mapped[bool] = mapped_column(
		BOOLEAN, nullable=False, default=True, index=True
	)
	last_login_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True
	)
	login_attempts: Mapped[int] = mapped_column(
		INTEGER, default=0, nullable=False, unique=False
	)


# class Token(Base, MixInNameTable):
# 	...