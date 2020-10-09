# -*- coding: UTF-8 -*-
#
# Copyright 2015-2020 Flavio Garcia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .tornadoweb import TornadoComponent
from cartola import config, sysexits
from datetime import datetime, timedelta
import logging
from six import iteritems
import sys
import tornado.ioloop

logger = logging.getLogger(__name__)

try:
    from croniter import croniter
except ImportError:
    logger.error("*** DEPENDENCY ERROR ***\n The croniter module isn't "
                 "installed.\n You need to either install firenado with "
                 "extras(all or schedule) or install croniter to use "
                 "firenado.schedule package.\n\n Possible fixes:\n  pip "
                 "install firenado[all]\n  pip install firenado[schedule]\n  "
                 "pip install croniter\n\n You can also add firenado[all] or "
                 "firenado[scheudle] or croniter to you requirements file "
                 "also.\n It's recommended to use firenado with extras "
                 "instead of installing croniter directly to avoid any "
                 "version compatibility error.\n The croniter package"
                 "installed by extras was tested with firenado and no errors "
                 "are expected during the execution.")
    sys.exit(sysexits.EX_FATAL_ERROR)


def next_from_cron(cron):
    """ Return next schedule run offset from now to the time of execution

    :param cron: The cron string
    :return:
    """
    iterator = croniter(cron, datetime.now())
    return iterator.get_next(datetime)


class Scheduler(object):

    def __init__(self, component, **kwargs):
        """
        Scheduler constructor. It will receive a scheduled component and
        loop interval as parameters.

        :param ScheduledTornadoComponent component: The scheduled component
        that owns the scheduler
        owns the scheduler.
        :param int interval:
        """
        self._can_run = False
        self._id = None
        self._jobs = {}
        self._interval = kwargs.get("interval", 1000)
        self._name = None
        self.component = component
        self._periodic_callback = None

    @property
    def id(self):
        return self._id

    @property
    def jobs(self):
        return [job for _, job in iteritems(self._jobs)]

    @property
    def name(self):
        return self._name

    @property
    def can_run(self):
        return self._can_run

    def add_job(self, job):
        logger.info("Adding job %s into the scheduler [id: %s, name: %s]." %
                    (job.id, self.id, self.name))
        self._jobs[job.id] = job

    def get_job(self, job_id):
        return self._jobs.get(job_id)

    def initialize(self, **kwargs):
        self._id = kwargs.get("id")
        self._name = kwargs.get("name")
        logger.info("Initializing scheduler [id: %s, name: %s]." % (
            self.id, self.name))

    def load_jobs(self):
        raise NotImplementedError

    def remove_job(self, job_id):
        logger.info("Removing job %s from the scheduler [id: %s, name: %s]."
                    % (job_id, self.id, self.name))
        job = self.get_job(job_id)
        if job is None:
            return None
        del(self._jobs[job_id])
        return job.id

    def run(self):
        self.load_jobs()
        logger.info("Scheduler [id: %s, name: %s] interval set to %sms." %
                    (self.id, self.name, self._interval))
        self._periodic_callback = tornado.ioloop.PeriodicCallback(
            self._manage_jobs, self._interval)
        self._periodic_callback.start()

    def _manage_jobs(self):
        logger.debug("Scheduler [id: %s, name: %s] managing jobs." %
                    (self.id, self.name))
        logger.debug("Scheduler [id: %s, name: %s] stopping periodic callback."
                     % (self.id, self.name))
        self._periodic_callback.stop()
        for job in self.jobs:
            if not job.already_scheduled:
                logger.info("Job %s from Scheduler [id: %s, name: %s] isn't "
                            "scheduled yet." % (job.hard_id, self.id,
                                                self.name))
                if job.must_schedule:
                    logger.info(
                        "Job %s from Scheduler [id: %s, name: %s] must be "
                        "scheduled to run at %s." % (
                            job.hard_id, self.id, self.name, job.next_run))
                    job.schedule()
            else:
                logger.debug("Job %s from Scheduler [id: %s, name: %s] already"
                             "scheduled." % (job.hard_id, self.id,
                                                self.name))

        logger.debug("Scheduler [id: %s, name: %s] ending of managing jobs." %
                    (self.id, self.name))
        logger.debug("Scheduler [id: %s, name: %s] starting periodic callback."
                     % (self.id, self.name))
        self._periodic_callback.start()


class ConfScheduler(Scheduler):

    def __init__(self, scheduled_component, **kwargs):
        super(ConfScheduler, self).__init__(scheduled_component, **kwargs)
        self._conf = kwargs.get("conf", None)

    def load_jobs(self):
        if "jobs" in self._conf:
            for job_conf in self._conf['jobs']:
                job_id = job_conf.get("id")
                job_resolved_class = None
                job_cron = job_conf.get("cron")
                job_date = job_conf.get("date")
                job_interval = job_conf.get("interval")
                if 'class' in job_conf:
                    job_resolved_class = config.get_from_string(
                        job_conf['class'])
                if job_resolved_class is None:
                    logger.warning("Firenado Scheduled Job Error:\n    The "
                                   "scheduled class job %s was not found "
                                   "in the file:\n        %s\n    Job id: %s"
                                   "\n    Scheduler: [id: %s, name: %s]"
                                   "\n        Config: %s\n"
                                   "\n    Please fix this issue.\n" %
                                   (job_conf['class'],
                                    self.component.get_complete_config_file(),
                                    job_id, self.id, self.name, job_conf))
                else:
                    if job_id is None:
                        logger.warning(
                            "Firenado Scheduled Job Error:\n    The "
                            "scheduled job id not defined in the "
                            "file:\n        %s"
                            "\n    Scheduler: [id: %s, name: %s]"
                            "\n        Config: %s\n"
                            "\n    Please fix this issue.\n" %
                            (self.component.get_complete_config_file(),
                             self.id, self.name, job_conf))
                    else:
                        if (job_cron is None and job_date is None
                                and job_interval is None):
                            logger.warning(
                                "Firenado Scheduled Job Error:\n    The "
                                "scheduled must have a cron or date or "
                                "interval defined in the file:\n        %s\n  "
                                "  Job id: %s\n    Scheduler: [id: %s, "
                                "name: %s]\n        Config: %s\n"
                                "\n    Please define either a cron string or "
                                "date.\n" %
                                (self.component.get_complete_config_file(),
                                 job_id, self.id, self.name, job_conf))
                        else:
                            self.add_job(job_resolved_class(self, **job_conf))

    def initialize(self):
        has_error = False
        if self._conf is None:
            logger.warning("It is not possible to initialize the scheduler "
                           "because the configuration is missing.")
            has_error = True
        if "id" not in self._conf:
            logger.warning("It is not possible to initialize the scheduler "
                           "because id is missing in the configuration "
                           "provided.\n Config: %s" % self._conf)
            has_error = True
        if "name" not in self._conf:
            logger.warning("It is not possible to initialize the scheduler "
                           "because name is missing in the configuration "
                           "provided.\n Config: %s" % self._conf)
            has_error = True

        if not has_error:
            self._can_run = True
            super(ConfScheduler, self).initialize(**self._conf)

        if "interval" in self._conf:
            self._interval = self._conf['interval']


class ScheduledJob(object):

    def __init__(self, scheduler, **kwargs):
        self._scheduler = scheduler
        self._id = kwargs.get('id')
        self._date = kwargs.get('date')
        self._cron = kwargs.get('cron')
        self._interval = kwargs.get('interval')
        self._periodic_callback = None

    @property
    def id(self):
        return self._id

    @property
    def hard_id(self):
        return "%s:%s:%s" % (self._id, self.__class__.__name__, id(self))

    @property
    def date(self):
        return self._date

    @property
    def cron(self):
        return self._cron

    @property
    def already_scheduled(self):
        return self._periodic_callback is not None

    @property
    def next_run(self):
        if self._interval:
            return datetime.now() + timedelta(milliseconds=self._interval)
        if self._cron:
            return next_from_cron(self.cron)
        # TODO: run if date is defined
        return datetime.now() + timedelta(days=-356)

    @property
    def next_interval(self):
        now = datetime.now()
        delta = self.next_run - now
        return delta.total_seconds() * 1000

    @property
    def must_schedule(self):
        return self.next_interval > 0

    def schedule(self):
        next_interval = self.next_interval
        logger.info("Job %s from Scheduler [id: %s, name: %s] scheduled to run"
                    " at next interval of %sms." % (self.hard_id,
                                                    self._scheduler.id,
                                                    self._scheduler.name,
                                                    self.next_interval))
        self._periodic_callback = tornado.ioloop.PeriodicCallback(
            self._run_job, next_interval)
        self._periodic_callback.start()

    async def _run_job(self):
        """ Run the job
        :return None:
        """
        self._periodic_callback.stop()
        logger.info(
            "Running job %s from Scheduler [id: %s, name: %s]." % (
                self.hard_id, self._scheduler.id, self._scheduler.name))
        future = self.run()
        if future is not None:
            logger.debug(
                "Running job %s from Scheduler [id: %s, name: %s] "
                "asynchronously. " % (self.hard_id, self._scheduler.id,
                                      self._scheduler.name))
            await future
        logger.info(
            "Job %s removed from Scheduler [id: %s, name: %s]" % (
                self.hard_id, self._scheduler.id, self._scheduler.name))
        self._periodic_callback = None
        return

    def run(self):
        pass


class ScheduledTornadoComponent(TornadoComponent):

    def __init__(self, name, application):
        super(ScheduledTornadoComponent, self).__init__(name, application)
        self._interval = 1000
        self._has_conf = False
        self._schedulers = {}

    @property
    def has_schedulers(self):
        return len(self._schedulers) > 0

    @property
    def schedulers(self):
        return [schedule for _, schedule in iteritems(self._schedulers)]

    def get_config_filename(self):
        return "%s_%s" % (self.name, "schedule")

    def get_scheduler(self, name):
        if name in self.schedulers:
            return self.schedulers[name]
        return None

    def _config_schedule_component(self):
        if "interval" in self.schedule_conf():
            self._interval = self.conf['interval']
        logger.info("Scheduled component %s interval set to %sms." %
                    (self.name, self._interval))
        if "schedulers" in self.schedule_conf():
            logger.info("Initializing %s schedulers." % self.name)
            self._initialize_schedulers()
        else:
            logger.warning("No scheduler was defined in the scheduled "
                           "component %s.\n\n%s\n* It is necessary either "
                           "define schedulers or scheduler loaders in the \n*"
                           " %s config file. \n* %s-- Firenado scheduled "
                           "component\n%s\n" %
                           (self.name, "*" * 70,
                            self.get_config_file(), " " * 37, "*" * 70))

    def _initialize_schedulers(self):
        for scheduler_conf in self.conf['schedulers']:
            scheduler = ConfScheduler(self, interval=self._interval,
                                      conf=scheduler_conf)
            scheduler.initialize()
            if scheduler.can_run:
                self._schedulers[scheduler.id] = scheduler
                scheduler.run()

    def schedule_conf(self):
        return self.conf

    def initialize(self):
        if self.has_conf:
            logger.info("Configuration file found. Starting scheduled "
                        "component %s initialization." % self.name)
            self._config_schedule_component()
        else:
            logger.warning("No configuration file was found. Scheduled"
                           "component %s won't initialize")
