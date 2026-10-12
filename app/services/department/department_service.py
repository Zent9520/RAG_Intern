from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from backend.app.repositories.access_control.department_repository import (
    DepartmentRepository,
)


class DepartmentService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
    ):

        return await DepartmentRepository.get_all(
            db,
        )