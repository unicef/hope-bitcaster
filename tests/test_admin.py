import pytest
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory
from factories import SuperUserFactory, UserFactory
from fakes import RecordingClient

from hope_bitcaster.admin import BitcasterUserAdminMixin, sync_to_bitcaster


class DemoUserAdmin(BitcasterUserAdminMixin, ModelAdmin):
    pass


@pytest.fixture
def admin_instance():
    return DemoUserAdmin(get_user_model(), AdminSite())


@pytest.fixture
def rf():
    return RequestFactory()


def build_request(rf, user):
    request = rf.get("/")
    request.user = user
    request.session = "session"
    request._messages = FallbackStorage(request)
    return request


@pytest.mark.django_db
def test_sync_action_hidden_when_bitcaster_disabled(admin_instance, rf, settings):
    settings.BITCASTER_ENABLED = False

    actions = admin_instance.get_actions(build_request(rf, SuperUserFactory()))

    assert "sync_to_bitcaster" not in actions


@pytest.mark.django_db
def test_sync_action_visible_when_bitcaster_enabled(admin_instance, rf, bitcaster_settings):
    actions = admin_instance.get_actions(build_request(rf, SuperUserFactory()))

    assert "sync_to_bitcaster" in actions


@pytest.mark.django_db
def test_sync_action_warns_when_client_not_configured(admin_instance, rf, settings):
    settings.BITCASTER_ENABLED = False
    request = build_request(rf, SuperUserFactory())

    sync_to_bitcaster(admin_instance, request, get_user_model().objects.none())

    assert any("not enabled" in message.message for message in get_messages(request))


@pytest.mark.django_db
def test_sync_action_syncs_all_selected_users(admin_instance, rf, bitcaster_settings):
    users = [UserFactory() for _ in range(3)]
    queryset = get_user_model().objects.filter(pk__in=[u.pk for u in users])
    request = build_request(rf, SuperUserFactory())

    sync_to_bitcaster(admin_instance, request, queryset)

    registered = RecordingClient.last().registered
    assert {call["username"] for call in registered} == {user.username for user in users}


@pytest.mark.django_db
def test_sync_action_reports_success_count(admin_instance, rf, bitcaster_settings):
    UserFactory.create_batch(2)
    queryset = get_user_model().objects.all()
    request = build_request(rf, SuperUserFactory())

    sync_to_bitcaster(admin_instance, request, queryset)

    assert any(str(queryset.count()) in message.message for message in get_messages(request))
