=============================
hope-bitcaster
=============================


[![Test](https://github.com/unicef/hope-bitcaster/actions/workflows/test.yml/badge.svg)](https://github.com/unicef/hope-bitcaster/actions/workflows/test.yml)
[![Lint](https://github.com/unicef/hope-bitcaster/actions/workflows/lint.yml/badge.svg)](https://github.com/unicef/hope-bitcaster/actions/workflows/lint.yml)
[![codecov](https://codecov.io/github/unicef/hope-bitcaster/graph/badge.svg?token=FBUB7HML5S)](https://codecov.io/github/unicef/hope-bitcaster)
[![Documentation](https://github.com/unicef/hope-bitcaster/actions/workflows/docs.yml/badge.svg)](https://unicef.github.io/hope-bitcaster/)
[![Pypi](https://badge.fury.io/py/unicef-hope-bitcaster.svg)](https://badge.fury.io/py/unicef-hope-bitcaster)
[![Docker Pulls](https://img.shields.io/docker/pulls/unicef/hope-bitcaster)](https://hub.docker.com/repository/docker/unicef/hope-bitcaster/tags)

Reusable Django integration that mirrors HOPE users and events into a remote
[Bitcaster](https://github.com/unicef/hope-bitcaster) notification server via
the `bitcaster-sdk` package.

## Features

    - sync users to Bitcaster on `post_save` / `pre_delete`
    - tenant metadata (custom fields / distribution lists) via an adapter
    - tenant-scoped event routing (per-call project / application override)
    - public `sync_user()` helper for role / tenancy change signals
    - Celery tasks and a `sync_bitcaster_users` management command
    - Django admin "Sync selected users" action

## Quickstart

Install hope-bitcaster::

    pip install hope-bitcaster

put it in your `INSTALLED_APPS`::

    INSTALLED_APPS = [
        ...
        "hope_bitcaster.apps.AppConfig",
    ]

configure it::

    BITCASTER_ENABLED = True
    BITCASTER_BAE = "https://<API_KEY>@<HOST>/api/o/<ORG>/"
    BITCASTER_PROJECT_SLUG = "hope"
    BITCASTER_APPLICATION_SLUG = "payment-gateway"

See the [documentation](https://unicef.github.io/hope-bitcaster/) for tenant
metadata adapters, role/tenancy change hooks and event triggering.
