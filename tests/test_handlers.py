from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from factories import UserFactory

from hope_bitcaster.client import HopeBitcasterClient


@pytest.mark.django_db
def test_user_save_calls_register_user_directly():
    mock_client = MagicMock(spec=HopeBitcasterClient)
    with patch("hope_bitcaster.handlers.get_hope_bitcaster_client", return_value=mock_client):
        user = get_user_model().objects.create_user(username="signaluser", email="signal@example.com", password="pass")

    mock_client.register_user.assert_called_with(user)


@pytest.mark.django_db
def test_user_delete_calls_unregister_user_directly():
    user = UserFactory()
    username = user.username
    mock_client = MagicMock(spec=HopeBitcasterClient)
    with patch("hope_bitcaster.handlers.get_hope_bitcaster_client", return_value=mock_client):
        user.delete()

    mock_client.unregister_user.assert_called_once_with(username)


@pytest.mark.django_db
def test_user_handlers_are_no_ops_when_client_is_none():
    with patch("hope_bitcaster.handlers.get_hope_bitcaster_client", return_value=None):
        user = get_user_model().objects.create_user(username="noop-save", email="noop@example.com", password="pass")
        user.delete()
