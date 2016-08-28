Firenado Framework
==================

**master:** |travis_master| |landscape_master| |readthedocs_latest|

**develop:** |travis_develop| |landscape_develop| |readthedocs_develop|

.. |travis_master| image:: https://travis-ci.org/candango/firenado.svg?branch=master
   :target: https://travis-ci.org/candango/firenado
   :alt: Build Status Master

.. |landscape_master| image:: https://landscape.io/github/candango/firenado/master/landscape.svg?style=flat
   :target: https://landscape.io/github/candango/firenado/master
   :alt: Code Health

.. |readthedocs_latest| image:: https://readthedocs.org/projects/firenado/badge/?version=latest
   :target: https://readthedocs.org/projects/firenado/?badge=latest
   :alt: Documentation Status


.. |travis_develop| image:: https://travis-ci.org/candango/firenado.svg?branch=develop
   :target: https://travis-ci.org/candango/firenado
   :alt: Build Status develop

.. |landscape_develop| image:: https://landscape.io/github/candango/firenado/develop/landscape.svg?style=flat
   :target: https://landscape.io/github/candango/firenado/develop
   :alt: Code Health

.. |readthedocs_develop| image:: https://readthedocs.org/projects/firenado/badge/?version=develop
   :target: http://firenado.readthedocs.org/en/develop/?badge=develop
   :alt: Documentation Status


Introduction
------------

Firenado is a web framework that extends the original Tornado Web framework
adding new features like loose couple components, server side session layer,
yaml based configuration files and more.


Installation
------------

::

  pip install firenado



Usage
-----

Creating and running a new application:

::

  > firenado project init helloworld
  > helloworld
  > firenado app run

By default an application will be created with a redis based session and a
redis data source defied and linked to the session.

Firenado don't install redispy so it is necessary to either install it or turn
the session as file based. You can disable the session engine too.

To change the session type to file go to helloworld/conf/firenado.yml and
change the session definition to:

::

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

If your helloworld project isn't on the python path just go
helloworld/conf/firenado.yml and configure the application settings:

::

  app:
    component: helloworld
    data:
      sources:
          # Set here references from sources defined on data.sources
          - session
    pythonpath: ..
    port: 8888


Support
-------

Firenado is one of
`Candango Open Source Group <http://www.candango.org/projects>`_
initiatives. It is available under the
`Apache License, Version 2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

This web site and all documentation is licensed under
`Creative Commons 3.0 <http://creativecommons.org/licenses/by/3.0/>`_.
