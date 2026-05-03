from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.schemas.user import UserProfileUpdate
from app.services.user_service import UserService


class UserController(BaseController):
    def __init__(self, service: UserService):
        self._service = service

    async def me(self, current_user: User) -> JSONResponse:
        data = self._service.serialize_public(current_user)
        return self.respond_success(data, "Current user")

    async def update_profile(
        self,
        current_user: User,
        payload: UserProfileUpdate,
    ) -> JSONResponse:
        user = await self._service.update_profile(current_user, payload)
        data = self._service.serialize_public(user)
        return self.respond_success(data, "Profile updated")
