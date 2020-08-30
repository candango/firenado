Schedule
========

If you need to crate an application with scheduled actions Firenado provides a
structure to do it.

Using a scheduled component is possible to define a scheduler via configuration
and point to tasks that could be run once or in a interval.


Setting up a scheduled component:
---------------------------------

Instead of creating extending TornadoComponent extend it from
ScheduledTornadoComponent.

.. code-block:: python

   from . import handlers
   from firenado import schedule


   class SchedappComponent(schedule.ScheduledTornadoComponent):

We added the component to conf/firenado.yml and enabled it.

.. code-block:: yaml

   components:
     - id: schedapp
       class: schedapp.app.SchedappComponent
       enabled: true

This component could be used as the application component if you need.

.. code-block:: yaml

   app:
     component: 'schedapp'

By default Firenado will look for <component_id>_schedule.[yml|yaml] config
file. Here is an example with a config based scheduler running a cron based
scheduled task(the file is conf/schedapp_schedule.yml):

.. code-block:: yaml

   schedulers:
     - id: scheduler1
       name: Scheduler Example 1
       jobs:
         - id: job1
           class: schedapp.jobs.PrintTestJob
           cron: "*/1 * * * *"
           custom_property: Custom property from job1.

The configuration file is define the scheduler scheduler1 that manages a job
identified as job1 that runs every minute and a custom property to be used
by the the class schedapp.jobs.PrintTestJob. Here is the the job
implementation:

.. code-block:: python

   from firenado.schedule import ScheduledJob

   
   class PrintTestJob(ScheduledJob):

       def __init__(self, scheduler, **kwargs):
           super(PrintTestJob, self).__init__(scheduler, **kwargs)
           self._custom_property = kwargs.get('custom_property', None)

       def run(self):
            print("This is the custom property value: %s" % self._custom_property)

As demonstrated above we need to create a class that extends from ScheduledJob
and implements the run method. We used the constructor to consume the custom
property defined in the schedule config file and used it to print a message.
