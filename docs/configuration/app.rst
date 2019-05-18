Application
===========

The application configuration section set properties to the application to be
launched by Firenado.

The configuration items will set aspects like application data sources or
addresses and ports to listen for requests.


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

process
~~~~~~~

Configuration to fork the Tornado process to be launched by Firenado.

If the num_processes value is set to None the ioloop will be started without
forking.

If num_processes is set to a value bigger than 0 the ioloop will be forked with
this amount as number of child processes. If num_processes is set to zero the
number of cpu will be used to fork the main process.

The max_restarts value will only be used if num_processes is not none.

- Type: dictionary
- Default value: {'num_processes': None, 'max_restarts': 100}

.. code-block:: yaml

   app:
    process:
      num_processes: 4
      max_restarts: 150

- See:

 - https://www.tornadoweb.org/en/stable/process.html#tornado.process.fork_processes
 - https://www.tornadoweb.org/en/stable/httpserver.html#tornado.httpserver.HTTPServer

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

wait_before_shutdown
~~~~~~~~~~~~~~~~~~~~

Time in seconds to wait before trigger the application shutdown.

- Type: int
- Default value: 0

.. code-block:: yaml

   app:
    wait_before_shutdown: 5