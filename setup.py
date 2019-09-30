#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019.

# SMHI,
# Folkborgsvägen 1,
# Norrköping,
# Sweden

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>
#   Adam Dybbroe <adam.dybbroe@smhi.se>

# This file is part of pytroll.

# mpop is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mpop is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with mpop.  If not, see <http://www.gnu.org/licenses/>.

"""Setup file for pytroll monitor utilities
"""

from setuptools import setup
import versioneer

NAME = 'pytroll-monitor'

setup(name=NAME,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Monitoring tools for pytroll production runners',
      author='Martin Raspaud, Adam Dybbroe',
      author_email='martin.raspaud@smhi.se',
      packages=['pytroll_monitor', ],
      zip_safe=False,
      scripts=[],
      data_files=[],
      )
