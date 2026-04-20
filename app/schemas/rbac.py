from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import LoginAsOption


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    description: str | None = None
    allows_self_registration: bool = False


class RoleAssignPermissions(BaseModel):
    permission_ids: list[int] = Field(default_factory=list)


class RoleAssignUser(BaseModel):
    role_id: int | None = Field(
        default=None,
        description="RBAC role id; required when account_role is admin.",
    )
    account_role: LoginAsOption = Field(
        ...,
        description="Account surface role for route scoping: user/provider/admin.",
    )


class RoleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    allows_self_registration: bool


class RoleDetailOut(RoleSummary):
    permissions: list[str] = Field(default_factory=list)


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    module: str
    description: str | None
