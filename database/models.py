import uuid

from sqlalchemy import Column, String, Boolean, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .engine import BaseORM


class User(BaseORM):
    __tablename__ = "users"

    # * Columns
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_disabled = Column(Boolean, nullable=False, default=False)

    # * Relations
    password = relationship("Password", back_populates="user")

    # * Constraints
    __table_args__ = (
        Index("user_id_idx", id, postgresql_using="hash"),
        Index("user_name_idx", name, postgresql_using="hash"),
        Index("user_email_idx", name, postgresql_using="hash"),
    )


class Password(BaseORM):
    __tablename__ = "passwords"

    # * Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    hash = Column(Text, unique=True, nullable=False)

    # * Relations
    user = relationship("User", back_populates="password")

    # * Constraints
    __table_args__ = (
        Index("password_id_idx", id, postgresql_using="hash"),
        Index("password_hash_idx", hash, postgresql_using="hash"),
    )
