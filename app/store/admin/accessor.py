import typing
from hashlib import sha256

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def get_by_email(self, email: str) -> Admin | None:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session() as session:
            session: AsyncSession
            res = await session.scalars(query)
            raw_res = res.first()
            if raw_res:
                return Admin(
                    id=raw_res.id,
                    email=raw_res.email,
                    password=raw_res.password
                )
            return None

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = AdminModel(
            email=email,
            password=sha256(password.encode()).hexdigest()
        )
        async with self.app.database.session() as session:
            session: AsyncSession
            connection = session.connection()
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
        return Admin(
            id=admin.id,
            email=admin.email,
            password=admin.password
        )
