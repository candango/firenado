# Firenado Framework 

**master:** [![Build Status](https://travis-ci.org/candango/firenado.svg?branch=master)](https://travis-ci.org/candango/firenado)
[![Code Health](https://landscape.io/github/candango/firenado/master/landscape.svg?style=flat)](https://landscape.io/github/candango/firenado/master)
[![Documentation Status](https://readthedocs.org/projects/firenado/badge/?version=latest)](https://readthedocs.org/projects/firenado/?badge=latest)

**develop:** [![Build Status develop](https://travis-ci.org/candango/firenado.svg?branch=develop)](https://travis-ci.org/candango/firenado)
[![Code Health](https://landscape.io/github/candango/firenado/develop/landscape.svg?style=flat)](https://landscape.io/github/candango/firenado/develop)
[![Documentation Status](https://readthedocs.org/projects/firenado/badge/?version=develop)](http://firenado.readthedocs.org/en/develop/?badge=develop)


## Introduction

Firenado is a web framework that extends the original Tornado Web framework
adding new features like loose couple components, server side session layer, 
yaml based configuration files and more.

## Installation

```
pip install firenado
```

## Usage

Creating and running a new application:

```shell
firenado project init helloworld
cd helloworld
firenado app run
```

By default an application will be created with a redis based session and a 
redis data source defied and linked to the session.

Firenado don't install redispy so it is necessary to either install it or turn
the session as file based. You can disable the session engine too.

To change the session type to file go to helloworld/conf/firenado.yaml and
change the session definition to:

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

If your helloworld project isn't on the python path just go 
helloworld/conf/firenado.yaml and configure the application settings:

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

Firenado is one of [Candango Open Source Group]
(http://www.candango.org/projects/) initiatives. It is available under
the [Apache License, Version 2.0]
(http://www.apache.org/licenses/LICENSE-2.0.html).

This web site and all documentation is licensed under [Creative
Commons 3.0] (http://creativecommons.org/licenses/by/3.0/).