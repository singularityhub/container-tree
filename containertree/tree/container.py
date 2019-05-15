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

from random import choice
from containertree.utils import check_install
import requests
import json
import os
import re
import sys

from .base import ( ContainerTreeBase, Node )


class ContainerTree(ContainerTreeBase):

    def __init__(self, inputs=None, tag=None, folder_sep="/"):
        super(ContainerTree, self).__init__(inputs, tag, folder_sep)

    def __str__(self):
        return "ContainerTree<%s>" % self.count
    def __repr__(self):
        return "ContainerTree<%s>" % self.count

    def _make_tree(self, data=None, tag=None):
        '''construct the tree from the loaded data (self.data)
           we should already have a root defined. Since we are making
           the tree for an individual container, the node names are filepaths
           within the container.
        '''

        # If function is used for insert, called
        if data is None:
            data = self.data

        for attrs in data:

            # The starting node is the root node
            node = self.root

            # Add the tag to the new (or existing) node
            if tag is not None:
                if tag not in node.tags:
                    node.tags.add(tag)

            filepaths = attrs['Name'].split(self.folder_sep)
        
            # Add the path to the correct spot in the tree    
            for filepath in filepaths:

                if not filepath:
                    continue

                found = False

                # We are at the root
                if filepath == node.label:
                    found = True

                else:

                    # Search in present node
                    for child in node.children:

                        # We found the parent
                        if child.label == filepath:

                            # Did we find an existing node?
                            if attrs['Name'] == child.name:
                                child.counter += 1

                            # update node to be child that was found
                            node = child
                            found = True
                            break


                # If not found, add new node (child)
                if found is False:
                    new_node = Node(filepath, attrs)
                    self.count +=1

                    # Add to the root (or the last where found)
                    node.children.append(new_node)

                    # Keep working down the tree
                    node = new_node

                # Add the tag to the new (or existing) node
                if tag is not None:
                    if tag not in node.tags:
                        node.tags.add(tag)

            # The last in the list is the leaf (file)
            node.leaf = True


class ContainerDiffTree(ContainerTree):
    '''a container diff tree is a subclass of ContainerTree, specifically
       ready to read in an analysis result of a files export from Google's 
       Container Diff. We simply define the _load method to expect the format of:

       [0]['Analysis'] --> [{"Name":"...", "Size": 123 }]

    '''
    def _load(self, data=None):
        return self._filter_container_diff(data, analyze_type="File")

    def _filter_container_diff(self, data=None, analyze_type="File"):
        ''' class instantiated by subclass to do custom parsing of loaded data.
            In the case of Google container diff, whether from local file
            or web http, we find the "File" Analysis type and return it.

            Parameters
            ==========
            data: if provided, use instead of self.data already with instance
            analyze_type: the key to use for the index of Container-Diff
                          can be one of File, Apt, or Pip
        '''
        if data is None:
            data = self.data

        if not data:
            print('This function should be called with load() to define data.')
            sys.exit(1)

        # User can provide loaded data, as long as correct structure
        if not isinstance(data, list):
            print('Loaded Filelist must be list for Container Diff')

        else:
            for entry in data:
                if "Analysis" in entry and "AnalyzeType" in entry:
                    if entry['AnalyzeType'] == analyze_type:
                        analysis = entry['Analysis']

                        # Warn the user if empty
                        if analysis in [[],{},'', None]:
                            print('Warning, no data found for %s' % analyze_type)
                        return analysis

            # If we get down here, tell the user cannot find what looking for
            if len(data) == 0:
                print('Loaded Container Diff Analysis List is empty')

            else:
                print('%s key missing, is this ContainerDiff export?' % analyze_type)


class ContainerFileTree(ContainerDiffTree):
    '''a container file tree will build a file hierarchy tree using the 
       Container Diff File export. This is the base implementation of 
       ContainerTree, so we don't need to write a function to generate
       the tree here.
    '''

    def _load(self, data=None):
        return self._filter_container_diff(data, analyze_type="File")

    def find(self, filepath):
        '''find a path in the tree and return the node if found. For a Container
           Tree, we expect a filepath. This must be the absolute filepath.
           To do a search, use search instead.
        '''

        # We always start at the root  
        node = self.root

        # No children, no search
        if len(node.children) == 0:
            # They were looking for the root
            if node.label == filepath:
                return node
            return
        
        filepaths = filepath.split(self.folder_sep)
        assembled='/'.join(filepaths)

        # Look for the path in the tree
        for filepath in filepaths:

            if not filepath:
                continue

            # Comparing basenames (<etc>)
            if filepath == node.label:

                # Comparing complete assembled path, return node
                if filepath == assembled:
                    return node

            else:

                # Try and find the filepath in the tree
                for child in node.children:
                    if child.label == filepath:
                        node = child

                        # If the name is what we are looking for, return Node
                        if node.name == assembled:
                            return node
                        break


class ContainerPackageTree(ContainerDiffTree):
    '''a container package tree will generate a container tree based on some
       package manager. Since the output is from container-diff, we expect
       the loaded data to conform to the following, a list of:

       [{'Name': 'zlib1g', 'Size': 159744, 'Version': '1:1.2.8.dfsg-5'}..] 
    '''

    def __str__(self):
        return "Container%sTree<%s>" % (self.analyze_type, self.count)
    def __repr__(self):
        return "Container%sTree<%s>" % (self.analyze_type, self.count)


    def export_vectors(self, node=None, df=None, include_tags=None, 
                             skip_tags=None, regexp_tags=None, 
                             include_versions=False, level=0,
                             package=None):
        '''export one or more vectors to describe containers mapped to a
           package tree. Optionally, the user can include or disclude a set
           of containers, or include/disclude version strings.

           Parameters
           ==========
           node: the node to start the export at (default is root)
           df: the pandas dataframe to update or continue adding to
           include_tags: a list of container uris to include
           skip_tags: a list o container uris to skip
           regexp_tags: include tags based ona regular expression
           include_versions: optionally include versions as part of the features
           package: if the user wants versions, we pass the parent package to
                    the child version node
        '''
        # Only import pandas once
        if "pandas" not in locals():
            import pandas

        # Checks if we have initialized the df yet (can't compare to None)
        if not hasattr(df, 'add'):
            df = pandas.DataFrame()

        if node == None:
            node = self.root

        # Skip the root node (label is '')
        if node.label != '':
            
            containers = node.tags

            # If the user is limiting the containers to include
            if include_tags != None:
                containers = containers.intersection(set(include_tags))

            # If the user is skipping containers or tags
            if skip_tags != None:
                containers = [x for x in containers if x not in skip_tags]

            # If the user wants regular expression filtering
            if regexp_tags != None:
                containers = [x for x in containers if re.search(regexp_tags,x)]

            label = node.label
            add_packages = False

            # If the user wants to include versions, and we are on the verison level
            if include_versions and level == 2:
                label = '%s-v%s' %(package, label)
                add_packages = True

            elif not include_versions and level == 1:
                add_packages = True

            # Add the node packages to the tree
            if add_packages:
                for container in containers:
                    df.loc[container, label] = 1

        # Go through children
        level += 1
        for child in node.children:
            df = self.export_vectors(child, df, include_tags, 
                                                skip_tags, 
                                                regexp_tags,
                                                include_versions,
                                                level,
                                                node.label)
        
        return df


    def _make_tree(self, data=None, tag=None):
        '''construct the tree from the loaded data (self.data)
           we should already have a root defined. Since we are making
           the tree for an individual container, the node names are filepaths
           within the container.
        '''

        # If function is used for insert, called
        if data is None:
            data = self.data

        for package in data:

            # The starting node is the root node
            node = self.root

            # Add the tag to the new (or existing) node
            if tag is not None:
                if tag not in node.tags:
                    node.tags.add(tag)
        
            # Add the node to the tree based on package name
            new_node = self.add(package['Name'], node, tag=tag)

            # Add the version Node
            version_node = self.add(package['Version'], new_node, tag=tag)   

            # The last in the list is the leaf (file)
            version_node.leaf = True


class ContainerPipTree(ContainerPackageTree):
    '''a container pip tree will generate a container tree based on pip
       packages.
    '''
    def __init__(self, inputs=None, tag=None, folder_sep="/"):
        self.analyze_type = "Pip"
        super(ContainerPipTree, self).__init__(inputs, tag, folder_sep)

    def _load(self, data=None):
        return self._filter_container_diff(data, self.analyze_type)


class ContainerAptTree(ContainerPackageTree):
    '''a container apt tree will generate a container tree based on pip
       packages.
    '''
    def __init__(self, inputs=None, tag=None, folder_sep="/"):
        self.analyze_type = "Apt"
        super(ContainerAptTree, self).__init__(inputs, tag, folder_sep)

    def _load(self, data=None):
        return self._filter_container_diff(data, self.analyze_type)
