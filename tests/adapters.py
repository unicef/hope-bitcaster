from typing import Any


def user_adapter(user: Any) -> dict[str, Any]:
    return {
        "custom_fields": {"country_office": "afghanistan"},
        "distribution_list": "afghanistan",
    }


def failing_adapter(user: Any) -> dict[str, Any]:
    raise RuntimeError("adapter boom")
