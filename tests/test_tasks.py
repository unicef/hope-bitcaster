from unittest.mock import MagicMock, patch

import pytest

from hope_bitcaster.client import HopeBitcasterClient
from hope_bitcaster.tasks import sync_user_to_bitcaster, unregister_user_from_bitcaster


def test_sync_task_is_no_op_when_client_is_none():
    with patch("hope_bitcaster.tasks.get_hope_bitcaster_client", return_value=None):
        sync_user_to_bitcaster(user_pk=999)


@pytest.mark.django_db
def test_sync_task_is_no_op_for_missing_user():
    mock_client = MagicMock(spec=HopeBitcasterClient)
    with patch("hope_bitcaster.tasks.get_hope_bitcaster_client", return_value=mock_client):
        sync_user_to_bitcaster(user_pk=99999)

    mock_client.register_user.assert_not_called()


@pytest.mark.django_db
def test_sync_task_calls_register_user(bitcaster_settings):
    from factories import UserFactory

    user = UserFactory()
    mock_client = MagicMock(spec=HopeBitcasterClient)
    with patch("hope_bitcaster.tasks.get_hope_bitcaster_client", return_value=mock_client):
        sync_user_to_bitcaster(user_pk=user.pk)

    mock_client.register_user.assert_called_once_with(user)


def test_unregister_task_is_no_op_when_client_is_none():
    with patch("hope_bitcaster.tasks.get_hope_bitcaster_client", return_value=None):
        unregister_user_from_bitcaster(username="ghost")


def test_unregister_task_calls_unregister_user():
    mock_client = MagicMock(spec=HopeBitcasterClient)
    with patch("hope_bitcaster.tasks.get_hope_bitcaster_client", return_value=mock_client):
        unregister_user_from_bitcaster(username="ghost")

    mock_client.unregister_user.assert_called_once_with("ghost")
