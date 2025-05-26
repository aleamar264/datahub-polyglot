from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import BOOLEAN, TIMESTAMP, VARCHAR
from sqlalchemy.dialects.postgresql import UUID as pg_uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from utils.db.general import MixInNameTable


class Base(DeclarativeBase): ...


class Users(Base, MixInNameTable):
	id: Mapped[UUID] = mapped_column(
		pg_uuid(as_uuid=True), primary_key=True, nullable=False, default_factory=uuid4
	)
	full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False, unique=False)
	email: Mapped[str] = mapped_column(
		VARCHAR(255), nullable=False, unique=True, index=True
	)
	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False, default=datetime.now(UTC), index=True
	)
	updated_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=True, default=None, index=True
	)
	is_active: Mapped[bool] = mapped_column(
		BOOLEAN, nullable=False, default=False, index=True
	)
