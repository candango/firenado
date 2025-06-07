# Copyright 2015-2025 Flavio Garcia
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

from .section import create_section
import click
import cloup
from firenado import get_version
import importlib


class FirenadoHeaded:

    def get_help(self, ctx: click.Context) -> str:
        """Formats the help into a string and returns it.

        Calls :meth:`format_help` internally.
        """
        formatter = ctx.make_formatter()
        self.format_help(ctx, formatter)
        help = f"Firenado Framework __version__\n\n{formatter.getvalue()}"
        return help.replace("__version__", get_version())


@cloup.group("Firenado", show_subcommand_aliases=True, cls=FirenadoHeaded)
def cli():
    return 0


create_section("firenado", cli, "Commands are:\n\nFirenado")

submodules = ["app", "project"]
for submodule in submodules:
    importlib.import_module(f"firenado.cli.commands.{submodule}")
