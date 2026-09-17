# hope-bitcaster

Reusable Django integration that mirrors HOPE users and events into a remote
[Bitcaster](https://github.com/unicef/hope-bitcaster) notification server via
the `bitcaster-sdk` package.

## Install

```bash
pip install hope-bitcaster
```

Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "hope_bitcaster.apps.AppConfig",
]
```

## Settings

| Setting | Required | Description |
| --- | --- | --- |
| `BITCASTER_ENABLED` | yes | Master switch. When falsy the client is never created and all calls are no-ops. |
| `BITCASTER_BAE` | yes | Bitcaster endpoint URL: `https://<API_KEY>@<HOST>/api/o/<ORG>/`. |
| `BITCASTER_PROJECT_SLUG` | yes | Default project slug. |
| `BITCASTER_APPLICATION_SLUG` | yes | Default application slug. |
| `BITCASTER_CLIENT_CLASS` | no | SDK client import path. Defaults to `bitcaster_sdk.async_client.AsyncClient`. |
| `BITCASTER_USER_ADAPTER` | no | Import path of a callable returning tenant metadata for a user (see below). |

When `BITCASTER_BAE`, `BITCASTER_PROJECT_SLUG` or `BITCASTER_APPLICATION_SLUG`
is missing, the client logs a warning and notifications are disabled.

## User synchronisation

Saving a user model triggers `post_save`, which registers the user with
Bitcaster; deleting one triggers `pre_delete`, which unregisters it. The
registration is an upsert, so it is safe to call repeatedly.

For bulk/backfill synchronisation run:

```bash
python manage.py sync_bitcaster_users
```

### Tenant metadata with an adapter

Set `BITCASTER_USER_ADAPTER` to an import path of a callable that receives the
user and returns a mapping:

```python
# myproject/bitcaster.py
def user_adapter(user):
    return {
        "custom_fields": {"country_office": user.country_office.slug},
        "distribution_list": user.country_office.slug,
    }
```

```python
BITCASTER_USER_ADAPTER = "myproject.bitcaster.user_adapter"
```

The adapter may return only `custom_fields`, only `distribution_list`, or both.
If it raises, the error is logged and the user is synced without metadata so a
failed adapter never breaks a user save. When no adapter is configured,
`custom_fields` defaults to `{}` and `distribution_list` to `None`.

### Reacting to role / tenancy changes

Tenant and role changes usually live on related models (for example `UserRole`)
and do not touch the user row, so `User.post_save` does not fire. Connect the
public helper to those models:

```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from hope_bitcaster import sync_user
from myapp.models import UserRole


@receiver([post_save, post_delete], sender=UserRole)
def on_user_role_changed(sender, instance, **kwargs):
    sync_user(instance.user_id)  # instance or pk, inline
    # or, deferred via Celery:
    # from hope_bitcaster.tasks import sync_user_to_bitcaster
    # sync_user_to_bitcaster.delay(instance.user_id)
```

`sync_user` accepts a user instance or a primary key and is a no-op when
Bitcaster is disabled or the user no longer exists.

## Triggering events

```python
from hope_bitcaster.client import get_hope_bitcaster_client

client = get_hope_bitcaster_client()
if client is not None:
    client.trigger_event("payment.completed", {"pk": 1})
```

Events use the default project/application unless overridden, which allows
routing to tenant-scoped applications:

```python
client.trigger_event(
    "payment.completed",
    {"pk": 1},
    project="hope",
    application="country-report-afghanistan",
)
```

`trigger_event` is fire-and-forget. A done-callback logs any asynchronous
failure (for example a full internal queue or an HTTP error) without blocking
the caller.

## Admin

Mix `BitcasterUserAdminMixin` into a user `ModelAdmin` to expose a
**Sync selected users to Bitcaster** action. The action is only shown when
`BITCASTER_ENABLED` is truthy.
