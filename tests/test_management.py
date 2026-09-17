from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from factories import UserFactory
from fakes import RecordingClient


def test_command_skips_when_not_configured(settings):
    settings.BITCASTER_ENABLED = False
    out = StringIO()

    call_command("sync_bitcaster_users", stdout=out)

    assert "skipping" in out.getvalue().lower()
    assert RecordingClient.instances == []


@pytest.mark.django_db
def test_command_syncs_all_users(bitcaster_settings):
    users = [UserFactory() for _ in range(3)]

    call_command("sync_bitcaster_users")

    registered = RecordingClient.last().registered
    assert len(registered) == get_user_model().objects.count()
    assert {call["username"] for call in registered} >= {user.username for user in users}


@pytest.mark.django_db
def test_command_outputs_success_count(bitcaster_settings):
    UserFactory.create_batch(4)
    out = StringIO()

    call_command("sync_bitcaster_users", stdout=out)

    assert str(get_user_model().objects.count()) in out.getvalue()
