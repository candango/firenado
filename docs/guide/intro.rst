Introduction
------------

Firenado is a Python web framework that primarily extends the
`Tornado <http://www.tornadoweb.org>`_ framework and runs over it's web server.

A Firenado application is organized in loose couple components and it is wired
using yaml config files. The framework makes possible to develop components
that can be shared between applications and distributed separately.

When you develop with Firenado you can use the our server side session layer
based on files or redis, and you can develop a custom storage.

Other features are offered shiped at the framework   core or via components.

Instalation
-----------
.. code-block:: bash

   pip install firenado

Usage
-----

Creating and running a new application:

.. code-block:: bash

   firenado project init helloworld
   cd helloworld
   firenado app run

By default an application will be created with a redis based session and a
redis data source defied and linked to the session.

Firenado don't install redispy so it is necessary to either install it or turn
the session as file based. You can disable the session engine too.

To change the session type to file go to helloworld/conf/firenado.yaml and
change the session definition to:

.. code-block:: yaml

   # Session types could be:
   # file or redis.
   session:
    type: file
    enabled: true
    # Redis session handler configuration
    # data:
    #   source: session
    # File session handler related configuration
    path: /tmp

If your helloworld project isn't on the python path just go
helloworld/conf/firenado.yaml and configure the application settings:

.. code-block:: yaml

   app:
     component: helloworld
     data:
     sources:
        # Set here references from sources defined on data.sources
        - session
     pythonpath: ..
     port: 8888


This web site and all documentation is licensed under Creative Commons 3.0.
