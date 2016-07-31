Configuration
=============

Firenado extends the Tornado web framework which uses ini files to help
developers to configure theirs applications.

As the ini configuration from Tornado is pretty easy and straight forward to
use, ini files(specially the one Tornado offers) just define key/value
structures.

If someone wants to define hierarchical configuration structures it is
necessary create indexes that represent the hierarchy(i.e.
my.hierarchical.index) but the file will be read as key/value. Either the
developer assumes the index is structured hierarchically or some extra
development is needed to represent this data as should be in memory.

This is not a problem if the application configuration is simple but if the
project requires lots of configurable parameters than you need a better option.

Firenado uses yaml files instead. TODO give the yaml benefits.

The app is bootstraped using the app configuration file. This file will
overload default parameters defined by the framework and system levels.

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

   configuration/firenado
   configuration/component
