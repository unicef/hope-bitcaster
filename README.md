=============================
hope-bitcaster
=============================


[![Test](https://github.com/unicef/hope-bitcaster/actions/workflows/test.yml/badge.svg)](https://github.com/unicef/hope-bitcaster/actions/workflows/test.yml)
[![Lint](https://github.com/unicef/hope-bitcaster/actions/workflows/lint.yml/badge.svg)](https://github.com/unicef/hope-bitcaster/actions/workflows/lint.yml)
[![codecov](https://codecov.io/github/unicef/hope-bitcaster/graph/badge.svg?token=FBUB7HML5S)](https://codecov.io/github/unicef/hope-bitcaster)
[![Documentation](https://github.com/unicef/hope-bitcaster/actions/workflows/docs.yml/badge.svg)](https://unicef.github.io/hope-bitcaster/)
[![Pypi](https://badge.fury.io/py/unicef-hope-bitcaster.svg)](https://badge.fury.io/py/unicef-hope-bitcaster)
[![Docker Pulls](https://img.shields.io/docker/pulls/unicef/hope-bitcaster)](https://hub.docker.com/repository/docker/unicef/hope-bitcaster/tags)

Simple django app to expose system infos like libraries version, database server.

Easy to extend to add custom checks.

## Features


    - dump system informations
    - admin integration
    - API to add custom checks
    - simple echo
    - retrieve library version


## Quickstart

Install hope_bitcaster::

    pip install hope_bitcaster

put it in your `INSTALLED_APPS`::

    INSTALLED_APPS=[
        ...
        'hope_bitcaster'
    ]

add relevant entries in your url.conf::

    urlpatterns = (
        ....
        url(r'', include(hope_bitcaster.urls)),
    )
