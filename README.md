# Firenado Framework 

**master:** [![Build Status](https://travis-ci.org/candango/firenado.svg?branch=master)](https://travis-ci.org/candango/firenado)
[![Code Health](https://landscape.io/github/candango/firenado/master/landscape.svg?style=flat)](https://landscape.io/github/candango/firenado/master)
[![Documentation Status](https://readthedocs.org/projects/firenado/badge/?version=latest)](https://readthedocs.org/projects/firenado/?badge=latest)

**develop:** [![Build Status develop](https://travis-ci.org/candango/firenado.svg?branch=develop)](https://travis-ci.org/candango/firenado)
[![Code Health](https://landscape.io/github/candango/firenado/develop/landscape.svg?style=flat)](https://landscape.io/github/candango/firenado/develop)
[![Documentation Status](https://readthedocs.org/projects/firenado/badge/?version=develop)](http://firenado.readthedocs.org/en/develop/?badge=develop)


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

To install only redis-py:

```
pip install firenado[redis]
```

Complete installation:

```
pip install firenado[pexpect, redis, sqlalchemy]
```

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

Firenado is one of [Candango Open Source Group](http://www.candango.org/projects/) initiatives. It is available under
the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).

This web site and all documentation is licensed under [Creative
Commons 3.0](http://creativecommons.org/licenses/by/3.0/).
