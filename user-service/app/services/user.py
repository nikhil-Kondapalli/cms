from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EmailAlreadyExistsException,
    UserNotFoundException,
)
from app.core.logging import logger
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.user import UserCreate, UserResponse, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repository.get_by_email(email.lower())

    async def create_user(
        self,
        payload: UserCreate,
    ) -> User:
        existing = await self.user_repository.get_by_email(payload.email.lower())
        if existing:
            raise EmailAlreadyExistsException()
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            role=payload.role,
        )
        logger.info(
            "Creating user %s",
            payload.email,
        )
        await self.user_repository.create(user)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return user

    async def list_users(
        self,
        pagination: PaginationParams,
    ):

        users = await self.user_repository.list(
            pagination.offset,
            pagination.limit,
        )

        total = await self.user_repository.count()

        return PaginatedResponse[UserResponse].create(
            content=[UserResponse.model_validate(user) for user in users],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def get_user(
        self,
        user_id,
    ):
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException()
        return user

    async def update_user(
        self,
        user_id,
        payload: UserUpdate,
    ):
        user = await self.get_user(user_id)
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.is_active is not None:
            user.is_active = payload.is_active
        if payload.role is not None:
            user.role = payload.role

        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
        return user

    async def delete_user(
        self,
        user_id,
    ):
        user = await self.get_user(user_id)
        await self.user_repository.delete(user)
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def search_users(
        self,
        query: str,
        pagination: PaginationParams,
    ):

        users = await self.user_repository.search(
            query=query,
            offset=pagination.offset,
            limit=pagination.limit,
        )

        return [UserResponse.model_validate(user) for user in users]
