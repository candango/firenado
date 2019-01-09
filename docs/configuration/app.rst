Application
===========

The application configuration section properties to the tornado application to
be launched by the


Here is an example of an app section:

.. code-block:: yaml

   app:
    component: "myapp"
    data:
      sources:
        - session
        - mydata
    port: 9091


Configuration Items
~~~~~~~~~~~~~~~~~~~

addresses
~~~~~~~~~

List of addresses the application will be listen for requests.

- Type: list
- Default value: ["::", "0.0.0.0"]

component
~~~~~~~~~

Firenado component to be set as the application component. This is the main
application's component.

When running `firenado proj init <project_name>` command a component is created
in the app.py file and set as in the conf/firenado.yml file.

- Type: string
- Default value: None

.. code-block:: yaml

   app:
    component: "myapp"

data
~~~~

Dictionary containing application data related properties.

sources
~~~~~~~

List of data sources to be created into the application during the launch
process. The list items are names of data sources defined in the configuration
data section.

Data sources can be defined in system and application levels.

- Type: list
- Default value: []

.. code-block:: yaml

   app:
    data:
      sources:
        - mydata
        - session

pythonpath
~~~~~~~~~~

Paths to be added to PYTHONPATH environment variable during the application
launch process.

- Type: string
- Default value: None

.. code-block:: yaml

   app:
    pythonpath: "..:/a/path/somewhere:"


port
~~~~

Port the application will be listen for requests.

- Type: int
- Default value: 8888

.. code-block:: yaml

   app:
    port: 9092


settings
~~~~~~~~

Settings to be passed to the Tornado application to be launched by Firenado.

- Type: dictionary
- Default value: {}

.. code-block:: yaml

   app:
    settings:
      cookie_secret: "kljasdf;lkasjdf;lasdkfjasd;lfkjasdf;lkasdjfasd"
      debug: true
      xsrf_cookies: true

- See:

 - http://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings

socket
~~~~~~

Unix socket path the application will be listen. When socket is defined either
addresses and port are ignored.

- Type: string
- Default value: None

.. code-block:: yaml

   app:
    pythonpath: "/tmp/myapp_socket"
