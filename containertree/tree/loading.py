#
# Copyright (C) 2018-2019 Vanessa Sochat.
#
# Loading data helper functions are consistent between trees, and shared here.
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


from containertree.logger import bot
from containertree.utils import ( 
    check_install, 
    run_command,
    read_json,
    get_tmpfile
)
import os
import re
import sys
import json
import requests

def _update(self, inputs, tag=None):
    '''_update is a helper function for update and load. We return
       data based on the inputs provided, and return loaded to the
       calling function. The subsequent action is up to the calling
       function.

       Parameters
       ==========
       inputs: the list of files (json/url export from ContainerDiff,
                 OR the uri of a container (to run container-diff).
       tag: if defined, a tag or label to identify
    '''
    data = None

    # Load data from web / url
    if re.search("https?://", inputs):
        data = self._load_http(inputs)

    # Load data from file
    elif os.path.exists(inputs):
        if inputs.endswith('json'):
            data = self._load_json(inputs)

        # Otherwise, pass on the filepath to the _load function
        else:
            print('Unrecognized extension, passing %s to _load subclass' % inputs) 
            data = inputs

    # Last effort is to run container-diff
    elif check_install(quiet=True):
        data = self._load_container_diff(inputs)
        if not data:
            bot.warning('No container-diff output found for %s' % inputs)
    else:
         print('Error loading %s' % inputs)
    return data


def update(self, inputs, tag=None):
    '''update will load in new data (without distributing an old self.data)

       Parameters
       ==========
       inputs: the list of files (json/url export from ContainerDiff,
                     OR the uri of a container (to run container-diff).
       tag: if defined, a tag or label to identify
    '''
    data = self._update(inputs)

    # If we have loaded data, continue
    if data:
        data = self._load(data)
        self._make_tree(data=data, tag=tag)


def load(self, inputs):
    ''' Load a set of files from json into the container tree.
        This means:
 
        1/ Reading in the data file
        2/ Creating a Node for each path portion
        3/ Assembling the nodes into the tree

        The data format must be a list of files, minimally
        with "Name" corresponding to the full path.

    '''
    data = self._update(inputs)
    if data not in [None, [], {}]:
        self.data = data
        self.data = self._load()

def _load(self, data=None):
    '''a function called by load, intended for subclass to call if additional
       parsing is needed.
    '''
    return self.data


def _load_http(self, url):
    '''load json from http. We assume it to be json because other formats
       aren't supported yet
    '''
    response = requests.get(url)

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print('JsonDecodeError of web address!')
            sys.exit(1)

def _load_json(self, inputs):
    '''read the inputs from a json file
    '''
    # Read in the raw data file
    with open(inputs) as filey:
        data = json.load(filey)
    return data


def _load_list(self, inputs):
    '''load a inputs. If the files are found to exist and Size is not
       included, calculate it.
    '''
    finished = []
    for entry in inputs:

        # If it's a filepath, convert to dictionary
        if not isinstance(entry, dict):
            entry = {'Name': entry}

        if "Name" not in entry:
            print('Skipping %s, no "Name" provided!' %entry)
            continue

        # If we don't have a size and the file exists, calculate one
        if "Size" not in entry and os.path.exists(entry['Name']):
            entry['Size'] = os.path.getsize(entry['Name'])
        finished.append(entry) 

    return finished


def _load_container_diff(self, container_name, output_file=None, types=None):
    '''call container-diff directly on the command line to extract
       the layers of interest.
    '''
    layers = dict()

    # Stop short if we don't have container-diff
    if not check_install(quiet=True):
        print('container-diff executable not found, cannot extract %s' % inputs)
        return layers

    if types == None:
        types = ['pip', 'apt', 'history', 'file']

    # Common error to provide just a string type
    if not isinstance(types, list):
        types = [types]

    types = ["--type=%s" % t for t in types]

    if output_file == None:
        output_file = get_tmpfile(prefix="container-diff")

    cmd = ["container-diff", "analyze", container_name]
    response = run_command(cmd + types + ["--output", output_file, "--json",
                                          "--quiet", "--no-cache",
                                          "--verbosity=panic"])

    if response['return_code'] == 0 and os.path.exists(output_file):
        layers = read_json(output_file)
        os.remove(output_file)
    else:
        print(response['message'])

    return layers
