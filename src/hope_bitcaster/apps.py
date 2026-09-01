from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = "hope_bitcaster"
    verbose_name = "Bitcaster"

    def ready(self) -> None:
        from . import handlers  # noqa: F401, PLC0415
