import pytest
from django.contrib.auth import get_user_model
from factories import UserFactory
from fakes import RecordingClient


@pytest.mark.django_db
def test_user_save_registers_user(bitcaster_settings):
    user = get_user_model().objects.create_user(username="signaluser", email="signal@example.com", password="pass")

    assert [call["username"] for call in RecordingClient.last().registered] == [user.username]


@pytest.mark.django_db
def test_user_delete_unregisters_user(bitcaster_settings):
    user = UserFactory()
    username = user.username

    user.delete()

    assert RecordingClient.last().unregistered == [{"project": "project", "application": "app", "username": username}]


@pytest.mark.django_db
def test_user_handlers_are_no_ops_when_bitcaster_disabled(settings):
    settings.BITCASTER_ENABLED = False

    user = get_user_model().objects.create_user(username="noop-save", email="noop@example.com", password="pass")
    user.delete()

    assert RecordingClient.instances == []
