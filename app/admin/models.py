from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint

from app.store.database.sqlalchemy_base import db


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])


class AdminModel(db):
    __tablename__ = "admins"

    id = Column('id', Integer)
    email = Column('email', String)
    password = Column('password', String)
    __table_args__ = (
        PrimaryKeyConstraint('id', name='admin_id_pk'),
    )
