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
from cartola import sysexits
from datetime import datetime
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


def next_from_cron(cron_string):
    """ Return next schedule run offset from now to the time of execution

    :param cron_string: The cron string
    :return:
    """
    iterator = croniter(cron_string, datetime.now())
    return iterator.get_next(datetime)


class Scheduler(object):

    def __init__(self, scheduled_component, **kwargs):
        """
        Scheduler constructor. It will receive a scheduled component and
        loop interval as parameters.

        :param basestring scheduled_component: The scheduled component that
        owns the scheduler.
        :param int interval:
        """
        self._can_run = False
        self._id = None
        self._jobs: {}
        self._interval = kwargs.get("interval", 1000)
        self._name = None
        self._scheduled_component = scheduled_component
        self._periodic_callback = None

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def can_run(self):
        return self._can_run

    def initialize(self, **kwargs):
        self._id = kwargs.get("id")
        self._name = kwargs.get("name")

    def run(self):
        logger.info("Scheduler [id: %s, name: %s] interval set to %sms." %
                    (self.id, self.name, self._interval))
        self._periodic_callback = tornado.ioloop.PeriodicCallback(
            self._manage_schedulers, self._interval)
        self._periodic_callback.start()

    def _manage_schedulers(self):
        self._periodic_callback.stop()
        print("Managing schedulers")
        self._periodic_callback.start()


class ConfScheduler(Scheduler):

    def __init__(self, scheduled_component, **kwargs):
        super(ConfScheduler, self).__init__(scheduled_component, **kwargs)
        self._conf = kwargs.get("conf", None)

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

    def __init__(self, _id, date, cron_string):
        self._id = _id
        self._date = date
        self._cron_string = cron_string

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        return self._date

    @property
    def cron_string(self):
        return self._cron_string

    def already_scheduled(self, _id, date):
        return self._id == _id and self._date == date

    def must_run(self):
        now = datetime.now()
        delta = self._date - now
        return delta.total_seconds() < 0


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
