Services
========

The way firenado organizes the logic to be executed in several parts of an
application is defining services.

Those services can be injected with the decorator
``firenado.service.served_by``. This decorator will add an instance of a
service to a method of any data connected object. Examples of data connected
classes are ``firenado.tornadoweb.TornadoHandler`` and any descendent of
``firenado.service.FirenadoService``.

Creating a service and decorating a handler:

.. code-block::python

   from firenado import service, tornadoweb
   # Importing a package with some services
   import another_service_package


   class MyService(service.FirenadoService):
       def do_something(self):
           # Self consumer will be the handler where this service was
           # called from.
           self.consumer.write("Something was done")


   class MyHandlerBeingServed(tornadoweb.TornadoHandler):
       # A good way to keep the reference is keeping the type hint
       my_service: MyService
       service_from_another_package: another_service_package.AnotherService

       @service.served_by(MyService)
       # you can also set the attribute/property name to be used
       @service.served_by(another_service_package.AnotherService,
           attribute_name="service_from_another_package"
       )
       def get(self):
           # The anotation service.served_by added self.my_service
           # here. The attribute/property name will be converted from the
           # cammel cased class to dashed separated.
           self.my_service.do_something()
           self.service_from_another_package.do_another_thing()

You can also add services to another services using the decorator:
