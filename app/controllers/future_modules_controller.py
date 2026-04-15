from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.services.future_modules_service import FutureModulesService


class FutureModulesController(BaseController):
    def __init__(self, service: FutureModulesService):
        self._service = service

    async def booking_placeholder(self) -> JSONResponse:
        return self.respond_success(
            self._service.booking_placeholder(),
            "Booking module placeholder",
        )

    async def chat_placeholder(self) -> JSONResponse:
        return self.respond_success(
            self._service.chat_placeholder(),
            "Chat module placeholder",
        )

    async def packages_placeholder(self) -> JSONResponse:
        return self.respond_success(
            self._service.packages_placeholder(),
            "Packages module placeholder",
        )

    async def coins_placeholder(self) -> JSONResponse:
        return self.respond_success(
            self._service.coins_placeholder(),
            "Coins system placeholder",
        )
