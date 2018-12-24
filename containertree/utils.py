#
# Copyright (C) 2018 Vanessa Sochat.
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
import os
import tempfile

def get_installdir():
    return os.path.abspath(os.path.dirname(__file__))


def read_json(filename, mode='r'):
    '''read_json reads in a json file and returns
       the data structure as dict.
    '''
    with open(filename, mode) as filey:
        data = json.load(filey)
    return data


def get_template(name):
    '''return an html template based on name.
    '''
    here = get_installdir()
    template_folder = os.path.join(here, 'templates')
    template_file = "%s/%s.html" %(template_folder, name)
    if os.path.exists(template_file):
        return template_file


def get_tmpfile(prefix=""):
    '''get a temporary file with an optional prefix.

       Parameters
       ==========
       prefix: prefix the file with this string.
    '''

    tmpdir = tempfile.mkdtemp()
    prefix = os.path.join(tmpdir, os.path.basename(prefix))
    fd, tmp_file = tempfile.mkstemp(prefix=prefix)
    os.close(fd)
    return tmp_file


def run_container_diff(container_name, output_file=None):
    '''Run container-diff to extract the diff data structure with
       packages (Pip and Apt) and History
    '''
    layers = dict()

    if output_file == None:
        output_file = get_tmpfile(prefix="container-diff")
    response = run_command(["container-diff", "analyze", container_name,
                            "--type=pip", "--type=apt", "--type=history",
                            "--output", output_file, "--json",
                            "--quiet","--verbosity=panic"])
    if response['return_code'] == 0 and os.path.exists(output_file):
        layers = read_json(output_file)
        os.remove(output_file)

    return layers


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
    cmd = [software, '--version']
    try:
        version = run_command(cmd, software)
    except: # FileNotFoundError
        return False

    if version is not None:
        if quiet is False and version['return_code'] == 0:
            version = version['message']
            print("Found %s version %s" % (software, version))
        return True
    return False
