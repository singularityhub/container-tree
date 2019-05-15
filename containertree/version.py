#
# Copyright (C) 2018-2019 Vanessa Sochat.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__version__ = "0.0.49"
AUTHOR = 'Vanessa Sochat'
AUTHOR_EMAIL = 'vsochat@stanford.edu'
NAME = 'containertree'
PACKAGE_URL = "http://www.github.com/singularityhub/container-tree"
KEYWORDS = 'generate container trees'
DESCRIPTION = "Generate container trees"
LICENSE = "LICENSE"

################################################################################
# Global requirements


INSTALL_REQUIRES = (
    ('requests', {'min_version': '2.18.4'}),
    ('pygments', {'min_version': '2.1.3'}),
)


INSTALL_ANALYSIS = (
    ('pandas', {'min_version': None}),
)

INSTALL_REQUIRES_ALL = (INSTALL_REQUIRES + INSTALL_ANALYSIS)
