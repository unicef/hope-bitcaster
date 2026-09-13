import logging
import threading
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.utils.module_loading import import_string

if TYPE_CHECKING:  # pragma: no cover
    from bitcaster_sdk.abstract_client import AbstractClient
    from django.contrib.auth.base_user import AbstractBaseUser

logger = logging.getLogger(__name__)

_domain_lock = threading.Lock()


class HopeBitcasterClient:
    _instance: "HopeBitcasterClient | None" = None

    def __init__(self, sdk_client: "AbstractClient", project: str, application: str) -> None:
        self._client = sdk_client
        self._project = project
        self._application = application

    @classmethod
    def from_settings(cls) -> "HopeBitcasterClient | None":
        bae = settings.BITCASTER_BAE
        project = settings.BITCASTER_PROJECT_SLUG
        application = settings.BITCASTER_APPLICATION_SLUG
        if not all([bae, project, application]):
            logger.warning("Bitcaster not fully configured — notifications disabled")
            return None
        client_class = import_string(settings.BITCASTER_CLIENT_CLASS)
        sdk_client = client_class(bae=bae, project=project, application=application)
        return cls(sdk_client=sdk_client, project=project, application=application)

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @staticmethod
    def _extract_user_metadata(user: "AbstractBaseUser") -> tuple[dict[str, Any], str | None]:
        adapter_path = getattr(settings, "BITCASTER_USER_ADAPTER", None)
        if not adapter_path:
            return {}, None
        try:
            adapter = import_string(adapter_path)
            data = adapter(user) or {}
            return dict(data.get("custom_fields") or {}), data.get("distribution_list")
        except Exception:  # noqa: BLE001
            logger.warning("Bitcaster user adapter %r failed; syncing without metadata", adapter_path, exc_info=True)
            return {}, None

    def register_user(self, user: "AbstractBaseUser") -> None:
        custom_fields, distribution_list = self._extract_user_metadata(user)
        self._client.register_user(
            project=self._project,
            application=self._application,
            username=user.username,
            email=user.email,
            first_name=getattr(user, "first_name", "") or "",
            last_name=getattr(user, "last_name", "") or "",
            custom_fields=custom_fields,
            active=user.is_active,
            addresses=[{"value": user.email}],
            distribution_list=distribution_list,
        )

    def unregister_user(self, username: str) -> None:
        self._client.unregister_user(
            project=self._project,
            application=self._application,
            username=username,
        )

    @staticmethod
    def _log_future_error(event_name: str, future: "Future[Any]") -> None:
        error = future.exception()
        if error is not None:
            logger.warning("Bitcaster event '%s' failed: %s", event_name, error)

    def trigger_event(
        self,
        event_name: str,
        payload: dict[str, Any],
        *,
        application: str | None = None,
        project: str | None = None,
    ) -> None:
        target_project = project or self._project
        target_application = application or self._application
        with _domain_lock:
            self._client.set_domain(target_project, target_application)
            result = self._client.trigger_event(event_name, context=payload)
        if isinstance(result, Future):
            result.add_done_callback(lambda future: self._log_future_error(event_name, future))


def get_hope_bitcaster_client() -> "HopeBitcasterClient | None":
    if HopeBitcasterClient._instance is not None:
        return HopeBitcasterClient._instance
    if not settings.BITCASTER_ENABLED:
        return None
    client = HopeBitcasterClient.from_settings()
    HopeBitcasterClient._instance = client
    return client
