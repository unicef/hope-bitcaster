import sys
from pathlib import Path

import pytest


here = Path(__file__).parent
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(here))
windows = pytest.mark.skipif(sys.platform != "win32", reason="requires windows")

win32only = pytest.mark.skipif("sys.platform != 'win32'")


def skip_if_django_version(v):
    return pytest.mark.skipif("django.VERSION[:2]>={}".format(v), reason="Skip if django>={}".format(v))


@pytest.fixture(autouse=True)
def reset_bitcaster_singleton():
    from fakes import RecordingClient
    from hope_bitcaster.client import HopeBitcasterClient

    HopeBitcasterClient.reset()
    RecordingClient.reset()
    yield
    HopeBitcasterClient.reset()
    RecordingClient.reset()


@pytest.fixture
def bitcaster_settings(settings):
    settings.BITCASTER_ENABLED = True
    settings.BITCASTER_BAE = "https://testkey@bitcaster.example.com/api/o/org/"
    settings.BITCASTER_PROJECT_SLUG = "project"
    settings.BITCASTER_APPLICATION_SLUG = "app"
    settings.BITCASTER_CLIENT_CLASS = "fakes.RecordingClient"
    settings.BITCASTER_USER_ADAPTER = None
    return settings
