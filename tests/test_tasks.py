import pytest
from factories import UserFactory
from fakes import RecordingClient

from hope_bitcaster.tasks import sync_user, sync_user_to_bitcaster, unregister_user_from_bitcaster


def test_sync_task_is_no_op_when_client_is_none(settings):
    settings.BITCASTER_ENABLED = False

    sync_user_to_bitcaster(user_pk=999)

    assert RecordingClient.instances == []


@pytest.mark.django_db
def test_sync_task_is_no_op_for_missing_user(bitcaster_settings):
    sync_user_to_bitcaster(user_pk=99999)

    assert RecordingClient.last().registered == []


@pytest.mark.django_db
def test_sync_task_registers_user(bitcaster_settings):
    user = UserFactory()

    sync_user_to_bitcaster(user_pk=user.pk)

    assert [call["username"] for call in RecordingClient.last().registered] == [user.username]


@pytest.mark.django_db
def test_sync_user_accepts_instance(bitcaster_settings):
    user = UserFactory()

    sync_user(user)

    assert RecordingClient.last().registered[0]["username"] == user.username


def test_sync_user_is_no_op_when_client_is_none(settings):
    settings.BITCASTER_ENABLED = False

    sync_user(999)

    assert RecordingClient.instances == []


@pytest.mark.django_db
def test_sync_user_is_no_op_for_missing_pk(bitcaster_settings):
    sync_user(99999)

    assert RecordingClient.last().registered == []


def test_unregister_task_is_no_op_when_client_is_none(settings):
    settings.BITCASTER_ENABLED = False

    unregister_user_from_bitcaster(username="ghost")

    assert RecordingClient.instances == []


def test_unregister_task_unregisters_user(bitcaster_settings):
    unregister_user_from_bitcaster(username="ghost")

    assert RecordingClient.last().unregistered == [{"project": "project", "application": "app", "username": "ghost"}]
