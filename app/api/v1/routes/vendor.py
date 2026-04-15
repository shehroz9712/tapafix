from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import get_current_user, require_provider
from app.api.v1.deps.controllers import get_vendor_controller
from app.controllers.vendor_controller import VendorController
from app.models.user import User

router = APIRouter(dependencies=[require_provider()])


@router.get("/dashboard")
async def vendor_dashboard(
    vendor: Annotated[User, Depends(get_current_user)],
    controller: Annotated[VendorController, Depends(get_vendor_controller)],
):
    return await controller.dashboard(vendor)
