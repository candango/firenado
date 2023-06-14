import click
import firenado.conf
import logging
import os
import taskio
from taskio import core
import sys


@taskio.root(taskio_conf=firenado.conf.taskio_conf)
def firenado_cli(ctx):
    pass
