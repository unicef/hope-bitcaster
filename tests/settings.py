DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "hope_bitcaster.apps.AppConfig",
]

SECRET_KEY = "test-secret-key-not-for-production"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

BITCASTER_ENABLED = False
BITCASTER_BAE = ""
BITCASTER_CLIENT_CLASS = "bitcaster_sdk.async_client.AsyncClient"
BITCASTER_PROJECT_SLUG = "hope"
BITCASTER_APPLICATION_SLUG = "payment-gateway"
