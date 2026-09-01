from unittest.mock import MagicMock, patch

import pytest
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from hope_bitcaster.admin import BitcasterUserAdminMixin, sync_to_bitcaster
from hope_bitcaster.client import HopeBitcasterClient


class DemoUserAdmin(BitcasterUserAdminMixin, ModelAdmin):
    pass


@pytest.fixture
def admin_instance():
    return DemoUserAdmin(get_user_model(), AdminSite())


@pytest.fixture
def rf():
    return RequestFactory()


def test_sync_action_hidden_when_bitcaster_disabled(admin_instance, rf, settings):
    settings.BITCASTER_ENABLED = False
    request = rf.get("/")
    request.user = MagicMock()
    actions = admin_instance.get_actions(request)
    assert "sync_to_bitcaster" not in actions


def test_sync_action_visible_when_bitcaster_enabled(admin_instance, rf, bitcaster_settings):
    request = rf.get("/")
    request.user = MagicMock()
    actions = admin_instance.get_actions(request)
    assert "sync_to_bitcaster" in actions


@pytest.mark.django_db
def test_sync_action_warns_when_client_not_configured(rf, settings):
    settings.BITCASTER_ENABLED = False
    request = rf.get("/")
    request.user = MagicMock()
    modeladmin = MagicMock()

    with patch("hope_bitcaster.admin.get_hope_bitcaster_client", return_value=None):
        sync_to_bitcaster(modeladmin, request, get_user_model().objects.none())

    modeladmin.message_user.assert_called_once()
    call_args = modeladmin.message_user.call_args
    assert "not enabled" in call_args[0][1]


@pytest.mark.django_db
def test_sync_action_syncs_all_selected_users(rf, bitcaster_settings):
    from factories import UserFactory

    users = [UserFactory() for _ in range(3)]
    queryset = get_user_model().objects.filter(pk__in=[u.pk for u in users])
    request = rf.get("/")
    request.user = MagicMock()
    modeladmin = MagicMock()
    mock_client = MagicMock(spec=HopeBitcasterClient)

    with patch("hope_bitcaster.admin.get_hope_bitcaster_client", return_value=mock_client):
        sync_to_bitcaster(modeladmin, request, queryset)

    assert mock_client.register_user.call_count == 3


@pytest.mark.django_db
def test_sync_action_reports_success_count(rf, bitcaster_settings):
    from factories import UserFactory

    users = [UserFactory() for _ in range(2)]
    queryset = get_user_model().objects.filter(pk__in=[u.pk for u in users])
    request = rf.get("/")
    request.user = MagicMock()
    modeladmin = MagicMock()
    mock_client = MagicMock(spec=HopeBitcasterClient)

    with patch("hope_bitcaster.admin.get_hope_bitcaster_client", return_value=mock_client):
        sync_to_bitcaster(modeladmin, request, queryset)

    modeladmin.message_user.assert_called_once()
    call_args = modeladmin.message_user.call_args
    assert "2" in call_args[0][1]
