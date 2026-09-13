"""In-memory stand-ins for the bitcaster-sdk HTTP clients.

These are real classes (not ``unittest.mock`` objects) implementing the small
slice of the SDK interface that ``hope_bitcaster`` uses. They let the tests
exercise the real ``HopeBitcasterClient`` wiring, settings lookup, signals and
admin code without any network or background threads.
"""

from __future__ import annotations

from concurrent.futures import Future
from typing import Any


class RecordingClient:
    """Synchronous SDK client double that records every call."""

    instances: list[RecordingClient] = []

    def __init__(
        self,
        bae: str | None = None,
        debug: bool = False,
        project: str | None = None,
        application: str | None = None,
        timeout: Any = None,
    ) -> None:
        self.bae = bae
        self.debug = debug
        self.project = project
        self.application = application
        self.timeout = timeout
        self.registered: list[dict[str, Any]] = []
        self.unregistered: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []
        self.domains: list[tuple[str, str]] = []
        type(self).instances.append(self)

    @classmethod
    def reset(cls) -> None:
        RecordingClient.instances = []

    @classmethod
    def last(cls) -> RecordingClient:
        return RecordingClient.instances[-1]

    def set_domain(self, project: str, application: str) -> None:
        self.project = project
        self.application = application
        self.domains.append((project, application))

    def register_user(self, **kwargs: Any) -> dict[str, Any]:
        self.registered.append(kwargs)
        return {"created": True}

    def unregister_user(self, project: str, application: str, username: str) -> dict[str, Any]:
        payload = {"project": project, "application": application, "username": username}
        self.unregistered.append(payload)
        return {"deleted": 1}

    def trigger_event(self, event: str, context: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        self.events.append({"event": event, "context": context or {}})
        return {"triggered": True}


class FutureRecordingClient(RecordingClient):
    """Asynchronous SDK client double: every call returns a pending Future.

    ``client.future`` may be replaced by a test before triggering to simulate a
    request that fails or completes immediately.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.future: Future[Any] = Future()
        self.last_future: Future[Any] | None = None

    def _result(self) -> Future[Any]:
        self.last_future = self.future
        return self.future

    def register_user(self, **kwargs: Any) -> Future[Any]:
        self.registered.append(kwargs)
        return self._result()

    def unregister_user(self, project: str, application: str, username: str) -> Future[Any]:
        self.unregistered.append({"project": project, "application": application, "username": username})
        return self._result()

    def trigger_event(self, event: str, context: dict[str, Any] | None = None, **kwargs: Any) -> Future[Any]:
        self.events.append({"event": event, "context": context or {}})
        return self._result()
