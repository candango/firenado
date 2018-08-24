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

.. toctree::
   :maxdepth: 2

   components/static_maps
