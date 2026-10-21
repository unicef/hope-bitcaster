import logging
from concurrent.futures import Future

import pytest
from factories import UserFactory
from fakes import FutureRecordingClient, RecordingClient

from hope_bitcaster.client import HopeBitcasterClient, get_hope_bitcaster_client


def test_get_client_disabled():
    assert get_hope_bitcaster_client() is None


def test_get_client_missing_bae_returns_none_and_logs_warning(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_BAE = ""

    with caplog.at_level(logging.WARNING):
        result = get_hope_bitcaster_client()

    assert result is None
    assert "Bitcaster not fully configured" in caplog.text


def test_get_client_returns_instance(bitcaster_settings):
    result = get_hope_bitcaster_client()

    assert isinstance(result, HopeBitcasterClient)
    assert len(RecordingClient.instances) == 1


def test_get_client_caches_singleton(bitcaster_settings):
    first = get_hope_bitcaster_client()
    second = get_hope_bitcaster_client()

    assert first is second
    assert len(RecordingClient.instances) == 1


def test_get_client_constructs_sdk_with_correct_args(bitcaster_settings):
    get_hope_bitcaster_client()

    sdk = RecordingClient.last()
    assert sdk.bae == "https://testkey@bitcaster.example.com/api/o/org/"
    assert sdk.project == "project"
    assert sdk.application == "app"


@pytest.mark.django_db
def test_register_user_sends_expected_payload(bitcaster_settings):
    user = UserFactory(email="u@example.com", first_name="Alice", last_name="Smith", is_active=True)

    get_hope_bitcaster_client().register_user(user)

    assert RecordingClient.last().registered == [
        {
            "project": "project",
            "application": "app",
            "username": user.username,
            "email": "u@example.com",
            "first_name": "Alice",
            "last_name": "Smith",
            "custom_fields": {},
            "active": True,
            "addresses": [{"value": "u@example.com"}],
            "distribution_list": None,
        }
    ]


@pytest.mark.django_db
def test_register_user_uses_adapter_metadata(bitcaster_settings):
    bitcaster_settings.BITCASTER_USER_ADAPTER = "adapters.user_adapter"
    user = UserFactory(email="u@example.com")

    get_hope_bitcaster_client().register_user(user)

    kwargs = RecordingClient.last().registered[0]
    assert kwargs["custom_fields"] == {"country_office": "afghanistan"}
    assert kwargs["distribution_list"] == "afghanistan"


@pytest.mark.django_db
def test_register_user_adapter_failure_falls_back_to_defaults(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_USER_ADAPTER = "adapters.failing_adapter"
    user = UserFactory()

    with caplog.at_level(logging.WARNING):
        get_hope_bitcaster_client().register_user(user)

    kwargs = RecordingClient.last().registered[0]
    assert kwargs["custom_fields"] == {}
    assert kwargs["distribution_list"] is None
    assert "adapter" in caplog.text


@pytest.mark.django_db
def test_register_user_with_async_client_does_not_block(bitcaster_settings):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    user = UserFactory()

    get_hope_bitcaster_client().register_user(user)

    sdk = FutureRecordingClient.last()
    assert sdk.registered[0]["username"] == user.username
    assert sdk.last_future is not None
    assert not sdk.last_future.done()


@pytest.mark.django_db
def test_register_user_no_warning_until_future_resolves(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()
    assert sdk.future is not None
    user = UserFactory()

    with caplog.at_level(logging.WARNING):
        client.register_user(user)
        assert "failed" not in caplog.text
        sdk.future.set_exception(Exception("later failure"))

    assert f"Bitcaster user registration for '{user.username}' failed" in caplog.text
    assert "later failure" in caplog.text


@pytest.mark.django_db
def test_register_user_no_warning_on_success(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()
    user = UserFactory()

    with caplog.at_level(logging.WARNING):
        client.register_user(user)
        sdk.future.set_result({"ok": True})

    assert "failed" not in caplog.text


@pytest.mark.django_db
def test_register_user_logs_on_immediate_failure(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()

    failed = Future()
    failed.set_exception(Exception("queue is full"))
    sdk.future = failed
    user = UserFactory()

    with caplog.at_level(logging.WARNING):
        client.register_user(user)

    assert f"Bitcaster user registration for '{user.username}' failed" in caplog.text
    assert "queue is full" in caplog.text


def test_unregister_user_sends_expected_payload(bitcaster_settings):
    get_hope_bitcaster_client().unregister_user("demo-user")

    assert RecordingClient.last().unregistered == [
        {"project": "project", "application": "app", "username": "demo-user"}
    ]


def test_unregister_user_with_async_client_does_not_block(bitcaster_settings):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"

    get_hope_bitcaster_client().unregister_user("demo-user")

    sdk = FutureRecordingClient.last()
    assert sdk.unregistered[0]["username"] == "demo-user"
    assert sdk.last_future is not None
    assert not sdk.last_future.done()


def test_unregister_user_no_warning_until_future_resolves(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()
    assert sdk.future is not None

    with caplog.at_level(logging.WARNING):
        client.unregister_user("demo-user")
        assert "failed" not in caplog.text
        sdk.future.set_exception(Exception("later failure"))

    assert "Bitcaster user unregistration for 'demo-user' failed" in caplog.text
    assert "later failure" in caplog.text


def test_unregister_user_no_warning_on_success(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()

    with caplog.at_level(logging.WARNING):
        client.unregister_user("demo-user")
        sdk.future.set_result({"deleted": 1})

    assert "failed" not in caplog.text


def test_unregister_user_logs_on_immediate_failure(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()

    failed = Future()
    failed.set_exception(Exception("queue is full"))
    sdk.future = failed

    with caplog.at_level(logging.WARNING):
        client.unregister_user("demo-user")

    assert "Bitcaster user unregistration for 'demo-user' failed" in caplog.text
    assert "queue is full" in caplog.text


def test_trigger_event_calls_sdk_with_default_domain(bitcaster_settings):
    get_hope_bitcaster_client().trigger_event("some_event", {"pk": 1})

    sdk = RecordingClient.last()
    assert sdk.domains == [("project", "app")]
    assert sdk.events == [{"event": "some_event", "context": {"pk": 1}}]


def test_trigger_event_overrides_project_and_application(bitcaster_settings):
    get_hope_bitcaster_client().trigger_event("some_event", {}, project="hope", application="country-afghanistan")

    sdk = RecordingClient.last()
    assert sdk.domains == [("hope", "country-afghanistan")]
    assert sdk.events[0]["event"] == "some_event"


def test_trigger_event_no_warning_until_future_resolves(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()
    assert sdk.future is not None

    with caplog.at_level(logging.WARNING):
        client.trigger_event("some_event", {})
        assert "failed" not in caplog.text
        sdk.future.set_exception(Exception("later failure"))

    assert "Bitcaster event 'some_event' failed" in caplog.text
    assert "later failure" in caplog.text


def test_trigger_event_no_warning_on_success(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()

    with caplog.at_level(logging.WARNING):
        client.trigger_event("some_event", {})
        sdk.future.set_result({"ok": True})

    assert "failed" not in caplog.text


def test_trigger_event_logs_on_immediate_failure(bitcaster_settings, caplog):
    bitcaster_settings.BITCASTER_CLIENT_CLASS = "fakes.FutureRecordingClient"
    client = get_hope_bitcaster_client()
    sdk = FutureRecordingClient.last()

    failed = Future()
    failed.set_exception(Exception("queue is full"))
    sdk.future = failed

    with caplog.at_level(logging.WARNING):
        client.trigger_event("some_event", {})

    assert "Bitcaster event 'some_event' failed" in caplog.text
    assert "queue is full" in caplog.text
