from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps.auth import require_user
from app.api.v1.deps.controllers import get_future_modules_controller
from app.controllers.future_modules_controller import FutureModulesController

router = APIRouter(prefix="/modules", tags=["future-modules"])


@router.get("/booking", dependencies=[require_user()])
async def booking_placeholder(
    controller: Annotated[
        FutureModulesController, Depends(get_future_modules_controller)
    ],
):
    return await controller.booking_placeholder()


@router.get("/chat", dependencies=[require_user()])
async def chat_placeholder(
    controller: Annotated[
        FutureModulesController, Depends(get_future_modules_controller)
    ],
):
    return await controller.chat_placeholder()


@router.get("/packages", dependencies=[require_user()])
async def packages_placeholder(
    controller: Annotated[
        FutureModulesController, Depends(get_future_modules_controller)
    ],
):
    return await controller.packages_placeholder()


@router.get("/coins", dependencies=[require_user()])
async def coins_placeholder(
    controller: Annotated[
        FutureModulesController, Depends(get_future_modules_controller)
    ],
):
    return await controller.coins_placeholder()
