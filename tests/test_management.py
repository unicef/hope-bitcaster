from io import StringIO
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command

from hope_bitcaster.client import HopeBitcasterClient


def test_command_skips_when_not_configured():
    out = StringIO()
    with patch("hope_bitcaster.management.commands.sync_bitcaster_users.get_hope_bitcaster_client", return_value=None):
        call_command("sync_bitcaster_users", stdout=out)

    assert "skipping" in out.getvalue().lower()


@pytest.mark.django_db
def test_command_syncs_all_users():
    from factories import UserFactory

    users = [UserFactory() for _ in range(3)]
    mock_client = MagicMock(spec=HopeBitcasterClient)

    with patch(
        "hope_bitcaster.management.commands.sync_bitcaster_users.get_hope_bitcaster_client",
        return_value=mock_client,
    ):
        call_command("sync_bitcaster_users")

    from django.contrib.auth import get_user_model

    total = get_user_model().objects.count()
    assert mock_client.register_user.call_count == total
    assert mock_client.register_user.call_count >= len(users)


@pytest.mark.django_db
def test_command_outputs_success_count():
    from factories import UserFactory

    UserFactory.create_batch(4)
    out = StringIO()
    mock_client = MagicMock(spec=HopeBitcasterClient)

    with patch(
        "hope_bitcaster.management.commands.sync_bitcaster_users.get_hope_bitcaster_client",
        return_value=mock_client,
    ):
        call_command("sync_bitcaster_users", stdout=out)

    from django.contrib.auth import get_user_model

    total = get_user_model().objects.count()
    assert str(total) in out.getvalue()
