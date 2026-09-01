from typing import Any

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from hope_bitcaster.client import get_hope_bitcaster_client


@receiver(post_save, sender=get_user_model())
def handle_user_saved(sender: type, instance: Any, **kwargs: Any) -> None:
    client = get_hope_bitcaster_client()
    if client is None:
        return
    client.register_user(instance)


@receiver(pre_delete, sender=get_user_model())
def handle_user_deleted(sender: type, instance: Any, **kwargs: Any) -> None:
    # NOTE: QuerySet.delete() bypasses per-instance signals, so bulk deletions
    # will NOT unregister affected users from Bitcaster.
    client = get_hope_bitcaster_client()
    if client is None:
        return
    client.unregister_user(instance.username)
