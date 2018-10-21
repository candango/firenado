Components
==========

Firenado is organized in components. A component is a unit that will provide
additional to an application.

The idea behind a component is that we can create a full application or
loose-coupled parts of logic that could be shared between applications.

A component could provide new handlers and mappings, templates, services,
models and other resources to an application in an organized manner.

A Firenado application is defined in the app.component parameter in the
application configuration file:

.. code-block:: yaml

   app:
     component: skell

Components are mapped into the application configuration file:

.. code-block:: yaml

   components:
     - id: skell
       class: skell.app.SkellComponent
       enabled: true
     - id: internal
       class: skell.components.internal.component.SkellInternalComponent
       enabled: true

A component configuration item is contains the follow parameters:

* id

The component id to be registered in the application during the load time.

The id is used to get the component from the application during run time and
to reference a template from another component.

* class

The component class to be loaded during the load time.

* enabled

Defines if the component is enabled or disabled. If isn't informed the
component will be disabled.

Disabled components are not available at run time.


Before and after handler methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For all handler returned by the component it is possible to implement the
methods before_handler and after_handler that will be executed before and after
the some http method be triggered by the Tornado server.

If a component TestComponent has a handler TestHandler that provides a get
method, mapped at /test url, when a request to this method is executed by the
server, the follow methods will be executed in this order:

1. TestComponent.before_handler
2. TestHandler.get
3. TestComponent.after_handler

Both before_handler and after_handler have the current handler as a parameter
and the handler session will be initialized correctly during their execution.

The execution of those methods will happen all the time a handler method
returned by the component is requested. In another words before_handler and
after_handler are global to the handlers returned by the component.

.. code-block:: python

   class TestComponent(firenado.tornadoweb.TornadoComponent):

       def get_handlers(self):
           return [
               (r"/test", handlers.TestHandler),
           ]

       def after_handler(self, handler):
           print("Doing something after handler: %s" % handler)

       def before_handler(self, handler):
           print("Doing something before handler: %s" % handler)

.. toctree::
   :maxdepth: 2

   components/static_maps
