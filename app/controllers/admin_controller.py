from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.services.user_service import UserService


class AdminController(BaseController):
    def __init__(self, service: UserService):
        self._service = service

    async def list_users(
        self,
        _admin: User,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> JSONResponse:
        users = await self._service.list_users_for_admin(skip=skip, limit=limit)
        payload = self._service.serialize_admin_rows(users)
        return self.respond_success(payload, "Users retrieved")
