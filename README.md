# Firenado Framework 

[![Latest PyPI version](https://img.shields.io/pypi/v/firenado.svg)](https://pypi.org/project/firenado/)
[![Number of PyPI downloads](https://img.shields.io/pypi/dm/firenado.svg)](https://pypi.org/project/firenado/#files)
[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fcandango%2Ffirenado%2Fbadge&style=flat)](https://actions-badge.atrox.dev/candango/firenado/goto)
[![GitHub license](https://img.shields.io/github/license/candango/firenado)](https://github.com/candango/firenado/blob/develop/LICENSE)

## Introduction

Firenado is a Python web framework that encapsulates and extends
[Tornado](http://www.tornadoweb.org) organizing the application in
components also adding a server side session layer, yaml based configuration
files as other features common that will help developers building web
applications and services.

Firenado is a web framework that extends the original Tornado Web framework
adding new features like loose couple components, server side session layer, 
yaml based configuration files and more.

## Installation

Installing Firenado will only force the installation of pyyaml, Tornado and
six. We call it the basic installation:

```
pip install firenado
```

It is possible to install extra packages as redis-py, sqlalchemy and pexpect.

Installing only redis-py:

```
pip install firenado[redis]
```

Installing only redis-py:

```
pip install firenado[sqlalchemy pexpect]
```

Installing only redis (redis-py, hiredis):

```
pip install firenado[sqlalchemy pexpect]
```

Installing redis and schedule(croniter):

```
pip install firenado[redis schedule]
```

Complete installation(what it is being the case, everytime):

```
pip install firenado[all]
```

> In the future, the installation logic will be inverted. Redis and pexpect
> will be added by default, and disabling them using optional parameters.
>
> The sqlalchemy and schedule(croniter) optionals will remain as is.
>
> With that change if you want just add schedule to the redis and pexpect:
>
> ``` pip install firenado[schedule] ```
>
> Maybe you want an agent with scheduled features and no redis:
>
> ``` pip install firenado[schedule noredis] ```
>
> Or don't need ProcessLaucher but sqlalchemy support:
>
> ``` pip install firenado[sqlalchemy nopexpect] ```
>
> See: #401

## Usage

Creating and running a new application:

```shell
firenado project init helloworld
cd helloworld
firenado app run
```

An application will be created with the redis based session engine
and a redis data source linked to the session.

Firenado won't install redis-py so it is necessary to inform the extra
requirement parameter or install it separately. It is possible to change 
the session to a file based engine or disable the session engine completely.

In order to change the session type to file go to helloworld/conf/firenado.yml
and change the session definition to:

```yaml
# Session types could be:
# file or redis.
session:
  type: file
  enabled: true
  # Redis session handler configuration
  #data:
  #  source: session
  # File session handler related configuration
  path: /tmp
```

If your helloworld project isn't located in the python path just go 
helloworld/conf/firenado.yml and changed it to:

```yaml
app:
  component: helloworld
  data:
    sources:
        # Set here references from sources defined on data.sources
        - session
  pythonpath: ..
  port: 8888
```

## Support

Firenado is one of [Candango Open Source Group
](http://www.candango.org/projects/) initiatives. It is available under
the [Apache License, Version 2.0
](http://www.apache.org/licenses/LICENSE-2.0.html).

This web site and all documentation is licensed under [Creative
Commons 3.0](http://creativecommons.org/licenses/by/3.0/).
