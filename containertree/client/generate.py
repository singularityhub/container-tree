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

from containertree import ContainerFileTree
from containertree.utils import ( 
    get_tmpdir, 
    get_template, 
    read_json, 
    read_file
)
from containertree.server import serve_template
from containertree.logger import bot
import shutil
import tempfile

import json
import sys
import os


def main(args):
    
    # No image or uri provided, print help
    if len(args.image) == 0:
        subparser.print_help()
        sys.exit(1)

    image = args.image.pop(0)

    # Step 1: Generate container tree object from Docker URI
    tree = ContainerFileTree(image)
    bot.debug(tree)

    # Step 2: Create a webroot to serve from
    webroot = args.output
    if args.output is None:
        webroot = get_tmpdir('containertree-')

    if not os.path.exists(webroot):
        os.mkdir(webroot)

    bot.debug('Webroot: %s' % webroot)

    # Copy the template to the webroot
    template = get_template(args.template)
    shutil.copyfile(template, "%s/index.html" % webroot)

    # If the user wants to print to terminal, we don't save
    filename = None
    if args.printout == None:
        filename='%s/data.json' % webroot

    # Export data.json
    bot.debug('Exporting data for d3 visualization')
    data = tree.export_tree(filename)

    # Does the user want to view the tree?
    if args.view:
        # Generate the data.json
        serve_template(webroot, 9779)

    # Does the user want to print output?
    elif args.printout != None: 
        if args.printout == "data.json":
            print(data)
        elif args.printout == "index.html":
            template = read_file(template)
            print(template)

    return webroot
