# -*- coding: UTF-8 -*-
#
# Copyright 2015-2019 Flavio Garcia
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

"""
The Explanation from the codes are described here: https://bit.ly/2D2ZFY9

Also see:
    http://tldp.org/LDP/abs/html/exitcodes.html
"""

# Catchall for general errors
EX_CATCHALL = 1
# Misuse of shell builtins (according to Bash documentation)
EX_MISUSE = 2
# Command invoked cannot execute
EX_CANNOT_EXECUTE = 126
# Command not found
EX_NOT_FOUND = 127
# Invalid argument to exit
EX_INVALID_ARGUMENT_TO_EXIT = 128
# Fatal error signal "n"
EX_FATAL_ERROR = 128
# Script terminated by Control-C
EX_TERMINATED_BY_CRTL_C = 130
# Exit status out of range
EX_OUT_OF_RANGE = 255

# successful termination
EX_OK = 0
# base value for error messages
EX__BASE = 64
# command line usage error
EX_USAGE = 64
# data format error
EX_DATAERR = 65
# cannot open input
EX_NOINPUT = 66
# addressee unknown
EX_NOUSER = 67
# host name unknown
EX_NOHOST = 68
# service unavailable
EX_UNAVAILABLE = 69
# internal software error
EX_SOFTWARE = 70
# system error (e.g., can't fork)
EX_OSERR = 71
# critical OS file missing
EX_OSFILE = 72
# can't create (user) output file
EX_CANTCREAT = 73
# input/output error
EX_IOERR = 74
# temp failure; user is invited to retry
EX_TEMPFAIL = 75
# remote error in protocol
EX_PROTOCOL = 76
# permission denied
EX_NOPERM = 77
# configuration error
EX_CONFIG = 78

# maximum listed value
EX__MAX = 78


def exit_fatal(signal):
    import sys
    sys.exit(EX_FATAL_ERROR + signal)
