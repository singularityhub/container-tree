#!/usr/bin/env python

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

import containertree
import argparse
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(description="ContainerTrees in Python")

    # Global Variables
    parser.add_argument('--debug', dest="debug", 
                        help="use verbose logging to debug.", 
                        default=False, action='store_true')

    parser.add_argument('--quiet', dest="quiet", 
                        help="suppress additional output.", 
                        default=False, action='store_true')

    parser.add_argument('--version', dest="version", 
                        help="print version and exit.", 
                        default=False, action='store_true')

    description = 'actions for ContainerTree Python'
    subparsers = parser.add_subparsers(help='containertree actions',
                                       title='actions',
                                       description=description,
                                       dest="command")

    # View templates
    templates = subparsers.add_parser("templates",
                                       help="View available tree templates")

    # Generate Tree
    generate = subparsers.add_parser("generate",
                                      help="Generate a container tree.")

    generate.add_argument("image", nargs=1,
                          help='Docker Container URI', 
                          type=str)

    generate.add_argument('--force','-f', dest="force", 
                          help="force generate if output file exists.", 
                          default=False, action='store_true')

    generate.add_argument('--view', dest="view", 
                           help="open a web browser to view tree.", 
                           default=False, action='store_true')

    generate.add_argument('--template', dest="template", 
                           help="templates to choose from for tree", 
                           default='files_tree', type=str)

    generate.add_argument('--output', dest="output", 
                           help="output folder to generate static files", 
                           default=None, type=str)

    generate.add_argument('--print', dest="printout", 
                           help="print a specific output file to the terminal", 
                           default=None, type=str)

    return parser


def get_subparsers(parser):
    '''get_subparser will get a dictionary of subparsers, to help with printing help
    '''

    actions = [action for action in parser._actions 
               if isinstance(action, argparse._SubParsersAction)]

    subparsers = dict()
    for action in actions:
        # get all subparsers and print help
        for choice, subparser in action.choices.items():
            subparsers[choice] = subparser

    return subparsers



def main():
    '''allow the user to generate container trees from the command line
    '''

    parser = get_parser()
    subparsers = get_subparsers(parser)

    def help(return_code=0):
        '''print help, including the software version and active client 
           and exit with return code.
        '''

        version = containertree.__version__

        print("\nContainerTree v%s" % version)
        parser.print_help()
        sys.exit(return_code)

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)
    
    # If the user didn't provide any arguments, show the full help
    if len(sys.argv) == 1:
        help()

    if args.quiet is True:
        os.environ['MESSAGELEVEL'] = "QUIET"
    elif args.debug is False:
        os.environ['MESSAGELEVEL'] = "DEBUG"

    # Show the version and exit
    if args.version is True:
        print(containertree.__version__)
        sys.exit(0)

    # Does the user want a shell?
    if args.command == "generate": from .generate import main
    elif args.command == "templates": from .templates import main

    # Pass on to the correct parser
    return_code = 0
    try:
        main(args)
        sys.exit(return_code)
    except UnboundLocalError:
        return_code = 1

    help(return_code)

if __name__ == '__main__':
    main()
