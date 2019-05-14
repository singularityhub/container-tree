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

import json
from subprocess import (
    Popen,
    PIPE,
    STDOUT
)
import fnmatch
import os
from glob import glob
import tempfile

def get_installdir():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def recursive_find(base, pattern=None):
    '''recursively find files that match a pattern, in this case, we will use
       to find Dockerfiles

       Paramters
       =========
       base: the root directory to start the seartch
       pattern: the pattern to search for using fnmatch
    '''
    if pattern is None:
        pattern = "*"

    for root, dirnames, filenames in os.walk(base):
        for filename in fnmatch.filter(filenames, pattern):
            yield os.path.join(root, filename)


def read_json(filename, mode='r'):
    '''read_json reads in a json file and returns
       the data structure as dict.
    '''
    with open(filename, mode) as filey:
        data = json.load(filey)
    return data


def write_json(json_obj, filename, mode="w", print_pretty=True):
    ''' write_json will (optionally,pretty print) a json object to file
    
        Parameters
        ==========
        json_obj: the dict to print to json
        filename: the output file to write to
        pretty_print: if True, will use nicer formatting
    '''
    with open(filename, mode) as filey:
        if print_pretty:
            filey.writelines(print_json(json_obj))
        else:
            filey.writelines(json.dumps(json_obj))
    return filename


def write_file(filename, content, mode="w"):
    '''write_file will open a file, "filename" and write content, "content"
        and properly close the file
    '''
    with open(filename, mode) as filey:
        filey.writelines(content)
    return filename


def read_file(filename, mode='r'):
    '''read_text file and return string of content
    '''
    with open(filename, mode) as filey:
        content = filey.read()
    return content


def print_json(json_obj):
    ''' just dump the json in a "pretty print" format
    '''
    return json.dumps(
                    json_obj,
                    indent=4,
                    separators=(
                        ',',
                        ': '))


def get_template(name):
    '''return an html template based on name.
    '''
    here = get_installdir()
    template_folder = os.path.join(here, 'templates')
    template_file = "%s/%s.html" %(template_folder, name)
    if os.path.exists(template_file):
        return template_file


def get_templates():
    '''list ids of html templates (based on name, without extension).
    '''
    here = get_installdir()
    template_folder = os.path.join(here, 'templates')
    templates = glob('%s/*.html' % template_folder)
    templates = [os.path.basename(x).replace('.html', '') for x in templates]
    return templates


def get_tmpfile(prefix="", tmpdir=None):
    '''get a temporary file with an optional prefix.

       Parameters
       ==========
       prefix: prefix the file with this string.
       tmpdir: the root directory to use (defaults to new temporary folder)
    '''
    if tmpdir == None:
        tmpdir = tempfile.mkdtemp()
    prefix = os.path.join(tmpdir, os.path.basename(prefix))
    fd, tmp_file = tempfile.mkstemp(prefix=prefix)
    os.close(fd)
    return tmp_file


def get_tmpdir(prefix=""):
    '''get a temporary folder with an optional prefix.

       Parameters
       ==========
       prefix: prefix the file with this string.
    '''
    tmpdir = tempfile.gettempdir()
    tmpfile = get_tmpfile(prefix, tmpdir)
    os.remove(tmpfile)    
    os.mkdir(tmpfile)
    return tmpfile


def run_command(cmd, sudo=False):
    '''run_command uses subprocess to send a command to the terminal.

        Parameters
        ==========
        cmd: the command to send, should be a list for subprocess
        error_message: the error message to give to user if fails,
        if none specified, will alert that command failed.

    '''
    if sudo is True:
        cmd = ['sudo'] + cmd

    try:
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    except FileNotFoundError:
        cmd.pop(0)
        output = Popen(cmd, stderr=STDOUT, stdout=PIPE)

    t = output.communicate()[0],output.returncode
    output = {'message':t[0],
              'return_code':t[1]}

    if isinstance(output['message'], bytes):
        output['message'] = output['message'].decode('utf-8')

    return output



def check_install(software='container-diff', quiet=True):
    '''check_install to ensure we have container-diff installed
       before trying to use it.

       Parameters
       ==========
       software: the software to check if installed
       quiet: should we be quiet? (default True)
    '''
    cmd = ['which', software]
    try:
        found = run_command(cmd)
    except: # FileNotFoundError
        return False

    if found['return_code'] == 0:
        if quiet is False:
            print(found['message'])
        return True
    return False
