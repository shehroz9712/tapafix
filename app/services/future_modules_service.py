class FutureModulesService:
    """Reserved module payloads (booking, chat, packages, coins)."""

    @staticmethod
    def booking_placeholder() -> dict:
        return {"module": "booking", "status": "reserved"}

    @staticmethod
    def chat_placeholder() -> dict:
        return {"module": "chat", "status": "reserved"}

    @staticmethod
    def packages_placeholder() -> dict:
        return {"module": "packages", "status": "reserved"}

    @staticmethod
    def coins_placeholder() -> dict:
        return {"module": "coins", "status": "reserved"}
