Services
========

Firenado helps you to write services using the data source structure provided
defined in the application configuration, and a simple mechanism to hook those
services to another services, handlers, or any data connected class.

A service are injected to a data connected class using the
``firenado.service.with_service`` decorator, that will add an instance of a
service to the object during the method execution.

Examples of data connected classes are ``firenado.tornadoweb.TornadoHandler``
and any descendant of ``firenado.service.DataConnectedMixin``.

How to create a service and decorate a handler with it:

.. code-block:: python

   from firenado.tornadoweb import TornadoHandler
   from firenado.service import with_service
   # Importing a package with some services
   import another_service_package


   class MyService(service.FirenadoService):
       def do_something(self):
           # Self consumer will be the handler where this service was
           # called from.
           self.consumer.write("Something was done")


   class MyHandlerBeingServed(TornadoHandler):
       # A good way to keep the reference is keeping the type hint
       my_service: MyService
       service_from_another_package: another_service_package.AnotherService

       @with_service(MyService)
       # you can also set the attribute/property name to be used
       @with_service(another_service_package.AnotherService,
           attribute_name="service_from_another_package")
       def get(self):
           # The decorator with_service will add self.my_service during the
           # method execution. The attribute/property name will be converted to
           # the snake cased service class name equivalent.
           self.my_service.do_something()
           # This service was added using the attribute_name parameter of the
           # with_service decorator
           self.service_from_another_package.do_another_thing()

You can also add services to another services using the decorator:
