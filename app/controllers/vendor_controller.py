from fastapi.responses import JSONResponse

from app.controllers.base_controller import BaseController
from app.models.user import User
from app.services.vendor_service import VendorService


class VendorController(BaseController):
    def __init__(self, service: VendorService):
        self._service = service

    async def dashboard(self, vendor: User) -> JSONResponse:
        payload = self._service.dashboard_payload(vendor)
        return self.respond_success(payload, "Vendor dashboard stub")
