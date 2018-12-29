Configuration
=============

Firenado extends the Tornado web framework which uses ini files to help
developers to configure theirs applications.

Besides the fact the ini configuration from Tornado is pretty easy and straight
forward to use, it just define key/value structures.

Let's assume that someone wants to define hierarchical configuration structures
. It is necessary create indexes that represent the hierarchy(i.e.
my.hierarchical.index) and the file will be organized in a key/value manner.
In this case the developer assumes the index is structured hierarchically or
some extra development is needed to represent this data as should be in memory.

A key/value structure isn't a problem if the application configuration is
simple. When a project requires lots of configurable parameters ini files can
be overwhelming.

Firenado uses yaml files instead that are organized in a hierarchical structure
and can define lists and dictionaries values instead of only strings. With yaml
boolean and numeric values are resolved with the same time when we consume them
in the python side.

A Firenado application is defined by a configuration file. This file will
define application aspects like session, data sources or the port to listen.
The application file will overload configuration set by framework and system
levels.


The framework config file will define the framework parts like:

- Firenado components offered by the framework
- Data connectors, used to connect to databases
- Log configuration
- Firenado cli management commands
- Session handlers and encoders

On the system config file level it is possible to define system level:

- Firenado components
- Data sources
- Custom data connectors
- Log configuration
- Custom cli managment commands
- Custom Session handlers and encoders

The app config file will define the application component and tornado
behaviour(ie. port or socket, number of processes forked, etc). It is also
possible to configure on this level:

- Data sources used by the application
- If session is enabled and what session handler and encoder is being used by
the application
- Override framework and system configuration

.. toctree::
   :maxdepth: 2

   configuration/app
   configuration/components
   configuration/data
   configuration/data
   configuration/management
   configuration/log
   configuration/session
