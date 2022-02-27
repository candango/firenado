Schedule
========

If you need to crate an application with scheduled actions Firenado provides a
structure to do it.

Using a scheduled component is possible to define a scheduler via configuration
and point to tasks that could be run once or in a interval.


Setting up a scheduled component:
---------------------------------

Instead of extending direcectly from the regular TornadoComponent use
ScheduledTornadoComponent instead.

.. code-block:: python

   from . import handlers
   from firenado import schedule

   class SchedappComponent(schedule.ScheduledTornadoComponent):


After that just add this component to conf/firenado.yml and enabled it.

.. code-block:: yaml

   components:
     - id: schedapp
       class: schedapp.app.SchedappComponent
       enabled: true

A ScheduledTornadoComponent could be used as the application component if you
want to.

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
         - id: job2
           class: schedapp.jobs.PrintTestJob
           interval: 15000
           custom_property: Custom property from job1.

The configuration file defines the scheduler scheduler1 that manages a job
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

Scheduled job periods:
----------------------

A scheduled job can be set to be executed using an interval or a cron string.

The interval parameter is defined milliseconds and will take priorety over
the cron string parameter. Here is an example with job to be executed every 30
seconds:

.. code-block:: yaml

   schedulers:
     - id: a_scheduler
       name: A scheduler
       jobs:
         - id: interval_job
           class: mypackage.EveryThirdyJob
           interval: 30000

Intevals are good to create fast tasks, the ones that will be executed in less
than one minute, because cron strings have the one minute limitation.

Besides the one minute limitation, cron strings are better for planned tasks,
and maintaing the time to be executed after restarting the application or the
scheduler. See one example:

.. code-block:: yaml

   schedulers:
     - id: another_scheduler
       name: Another scheduler
       jobs:
         - id: cron_based_job
           class: mypackage.TwiceADayJob
           cron: "30 0,12 * * *"

Contrasting with an interval based job, we can set a cron string to execute a
job every day at 1 am ("0 1 * * *") or twice a day (like in the example)
at 0:30 and 12:30 ("30 0,12 * * *"). With intervals we could set 24 hours or
12 hours periods in miliseconds but those values would start to count from the
time we started the application and the scheduled started.

If we start this application every 4 hours that job would never run the
interval based job, the cron based ones in another hand, would be executed
without issues. Unless the restart unfortunately coincide with 0:30 and 12:30
hours of the day and the scheduler would not have time to calculate the next
time to run the job, but that would be bad luck or bad planning. The interval
example with 4 hours restarts is also bad planing and an exageration to
differentiate both strategies.

In another words, interval jobs are better for tasks that need to check in less
than one minute and don't need to be planned, because the next execution will
be calculated when the scheduler started. Cron based jobs are resolved by
`croniter <https://github.com/taichino/croniter>`_ and they are better for
planned periodic jobs.
