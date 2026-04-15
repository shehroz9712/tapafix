from app.models.user import User


class VendorService:
    """Vendor domain logic (placeholder until vendor module is built)."""

    @staticmethod
    def dashboard_payload(user: User) -> dict:
        return {
            "vendor_id": str(user.id),
            "module": "vendor",
            "status": "placeholder",
        }
