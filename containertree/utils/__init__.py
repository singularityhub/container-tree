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

from .https import ( get, call )
from .fileio import (
    get_installdir,
    read_json,
    get_template,
    get_templates,
    get_tmpfile,
    get_tmpdir,
    read_file,
    recursive_find,
    run_command,
    print_json,
    write_file,
    write_json,
    check_install    
)

from .docker import (
    parse_image_uri,
    DockerInspector
)
