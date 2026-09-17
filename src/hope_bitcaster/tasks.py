from typing import Any

from celery import shared_task
from django.contrib.auth import get_user_model

from hope_bitcaster.client import get_hope_bitcaster_client

__all__ = ["sync_user", "sync_user_to_bitcaster", "unregister_user_from_bitcaster"]


def sync_user(user: Any) -> None:
    """Push a single user's current state to Bitcaster.

    Accepts a user instance or a primary key. Safe to call from signal
    receivers on related models (for example role/tenancy changes) since it
    is a no-op when Bitcaster is disabled or the user no longer exists.
    """
    client = get_hope_bitcaster_client()
    if client is None:
        return
    user_model = get_user_model()
    if not isinstance(user, user_model):
        try:
            instance = user_model.objects.get(pk=user)
        except (user_model.DoesNotExist, ValueError):
            return
        client.register_user(instance)
        return
    client.register_user(user)


@shared_task()
def sync_user_to_bitcaster(user_pk: Any) -> None:
    sync_user(user_pk)


@shared_task()
def unregister_user_from_bitcaster(username: str) -> None:
    client = get_hope_bitcaster_client()
    if client is None:
        return
    client.unregister_user(username)
