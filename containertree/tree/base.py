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

import os
from random import choice
from containertree.utils import ( 
    check_install, 
    run_command,
    read_json,
    get_tmpfile
)
import requests
import json
import copy

class ContainerTreeBase(object):

    def __init__(self, inputs=None, folder_sep='/', tag=None):
        '''construct a container tree from some export of files or 
           a string to indicate a container. This is determined by
           the subclass.

           Parameters
           ==========
           list: the json export (files.json) of a tar, can be https
           folder_sep: the character that separates path names
           tag: if defined, ascribe a unique id to the list at each node
                to identify the container. We can add other containers to
                the count.
 
        '''

        # The root node is the root of the fs
        self.root = Node('', {'size': 0, 'Name': '/'}, tag=tag)
        self.data = None
        
        # The character that separates folder/files
        self.folder_sep = folder_sep

        # Count the nodes
        self.count = 1
        
        # Sets self.data and builds self.tree
        if inputs != None:
            self.load(inputs)

        # If data is loaded, make the tree
        if self.data:
            self._make_tree(tag=tag)

# Loading Functions
    
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
                                              "--quiet","--verbosity=panic"])

        if response['return_code'] == 0 and os.path.exists(output_file):
            layers = read_json(output_file)
            os.remove(output_file)
        else:
            print(response['message'])

        return layers


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
        if inputs.startswith('http'):
            data = self._load_http(inputs)

        # Load data from file
        elif os.path.exists(inputs):
            if inputs.endswith('json'):
                data = self._load_file(inputs)
            # Otherwise, pass on the filepath to the _load function
            else:
                print('Unrecognized extension, passing %s to _load subclass' % inputs) 
                data = inputs

        # Last effort is to run container-diff
        elif check_install(quiet=True):
            data = self._load_container_diff(inputs)
        else:
            print('Error loading %s' %inputs)

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


    def __str__(self):
        return "ContainerTreeBase<%s>" % self.count
    def __repr__(self):
        return "ContainerTreeBase<%s>" % self.count


    def insert(self, name, attrs=None, tag=None):
        '''insert a node into the tree.
        '''
        entry = {'Name': name }
        
        if attrs is not None:
            for key,val in attrs.items():
                entry[key] = val

        self._make_tree(data=[entry], tag=tag)


    def add(self, name, node, attrs={}, tag=None):
        '''add a node based on name to the tree, or return found node
        '''             
        # Do we have the package?    
        found = False
        for child in node.children:

           # We found the parent
           if child.label == name:

               # Keep track of how many we have
               child.counter += 1

               # update node to be child that was found
               node = child
               found = True
               break

        # If we get down here, not found, add new node
        if not found:
            new_node = Node(name, attrs)
            self.count +=1

            # Add to the root (or the last where found)
            node.children.append(new_node)
            node = new_node

        # Add the tag to the new (or existing) node
        if tag is not None:
            if tag not in node.tags:
                node.tags.add(tag)

        return node


    def _make_tree(self, data=None, tag=None):
        '''must be instantiated by subclass.'''
        print('_make_tree must be instantiated by the subclass.')


    def export_tree(self, filename=None):
        '''export a data structure for a weighted, colored tree, either just
           the data or the full html / visualization. If filename is defined,
           export the raw data json to the file. If the generate_html is
           True, do the same but embed in html.

           Parameters
           ==========
           filename: if defined, write data to file (and return) otherwise
           return data structure

        '''

        # We will call this recursively
 
        def traverse(nodes={}, current=None):

            colors = ['#0000FF', # blue
                      '#FF7F00', # orange
                      '#FF0000', # red
                      '#7F007F', # purple
                      '#00FFFF', # cyan
                      '#0560D0'] # generic blue

            if current is None:
                current = self.root

            tags = list(current.tags)
            new_node = {'color': choice(colors),
                        'key': current.label,
                        'name': current.label.split('/')[-1],
                        'tags': tags,
                        'attrs': current.get_attributes(),
                        'children': [] }

            # Add the size if was provided!
            if hasattr(current, 'size'):
                new_node['size'] = current.size

            if len(nodes) == 0:
                nodes.update(new_node)
            else:            
                nodes['children'].append(new_node)

            # Iterate through children, add to data structure
            for child in current.children:
                traverse(nodes=new_node, current=child)

        nodes = dict()

        if self.data:
            traverse(nodes, current=self.root)
                
        # If the user provided a file, export to it
        if filename is not None:
            with open(filename, 'w') as filey:
                filey.writelines(json.dumps(nodes))
            return filename

        return nodes


# Searching Functions

    def similarity_score(self, tags):
        '''calculate a similarity score for one or more tags. The score is
           a basic information coefficient where we take into account:
 
           1/ the number of total nodes in context of the tags, meaning
              we add any node that has one or more of containers there
           2/ the number of nodes where the tags are all present
           3/ the number of nodes where one or more tags are missing

        '''
        total = 0       # total number of nodes with one or more
        intersect = 0   # all tags present at nodes
        diff = 0        # one or more tags missing

        def traverse(tags, current, total, intersect, diff):
 
            # All tags are represented in the node
            if all(t in current.tags for t in tags):
                intersect+=1
            else:
                diff+=1

            # If any of the tags are present, we add to total
            if any(t in current.tags for t in tags):
                total+=1

            # Iterate through children, add to data structure
            for child in current.children:
                total,intersect,diff = traverse(tags, child, total, intersect, diff)

            return total, intersect, diff

        # Return data structure so the user knows the components
        total, intersect, diff = traverse(tags, self.root, total, intersect, diff)
 
        result = {'total': total, 
                  'tags': tags,
                  'same': intersect,
                  'diff': diff }

        # Calculate score, percentage of nodes shared

        result['score'] = 0
        if total > 0:
           result['score'] = intersect / total

        return result


    def trace(self, name, node=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)
         '''
        if node == None:
            node = self.root

        # Find the node, is it in the tree?
        tracedNode = self.find(name)

        # Trace it's path
        if tracedNode != None:
            for child in node.children:
                traces = self._trace(name, child)
                if tracedNode in traces:
                    return [self.root] + traces


    def _trace(self, name, node, traces=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)
        '''
        if traces == None:
            traces = []

        # Always add node
        traces.append(node)

        # Did we find a node?
        if node.leaf == True:
            if node.label == name:
                return traces
            else:
                traces = []

        # Keep searching over children        
        for child in node.children:
            self._trace(name, child, traces)
        return traces
       
    def get_count(self, name):
        '''find a path in the tree and return the node if found
        '''
        counter = 0
        node = self.find(name)
        if node:
            counter = node.counter
        return counter


    def find(self, name, node=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)
         '''

        if node == None:
            node = self.root

        # Did we find a node?
        if node.label == name:
            return node

        # No children, we finished search
        if len(node.children) == 0:
            return None

        for child in node.children:
            node = self.find(name, child)
            if node != None:
                return node


    def remove(self, name, node=None):
        '''find a path in the tree and remove (and return) the node if found.
           The function returns None if the Node wasn't in the tree (and wasn't
           found and removed). The way this is designed, we cannot remove the
           root node (but we just return it).
         '''

        if node == None:
            node = self.root

        # Did we find the node?
        if node.label == name:
            return node

        # No children, we finished search
        if len(node.children) > 0:
            for c in range(len(node.children)):
                child = node.children[c]
                to_remove = self.remove(name, child)
                if to_remove != None:
                    del node.children[c]
                    return to_remove


    def search(self, name, number=None, node=None):
        '''find a basename in the tree. If number is defined, return
           up to that number. 
        '''
        found = []
 
        # We always start at the root  
        if node == None:
            node = self.root

        # Look for the name in the current node
        if name in node.label:
            found.append(node)

        # No children, no search
        if len(node.children) == 0:
            return found

        # Does the user want to cut out early?
        if number != None:
            if len(found) >= number:
                return found

        # Not at current node, search children!
        for child in node.children:
            found += self.search(name, number, child)
            if number != None:
                if len(found) >= number:
                    return found
        return found            


class Node(object):
    
    def __init__(self, name, attrs, tag=None):
        ''' a Node is a node in the Trie, meaning that
            it stores a word (a folder, name, or file) and some
            number of children from it. If a Node is a leaf 
            this coincides with the end of a path.

            Parameters
            ==========
            name: the name of the folder or file
            attrs: a dict of attributes to give to the node
            tag: a tag or label (goes into a list) to identify objects belonging

        '''
        self.label = name
        self.children = []
        self.set_attributes(attrs)
        
        # The end of the file path
        self.leaf = False

        # If the tag is defined, tag the node
        self.tags = set()
        if tag is not None:
            self.tags.add(tag)

        # How many times this character appeared in the addition process
        self.counter = 1

    def __str__(self):
        return "Node<%s>" % self.label
    def __repr__(self):
        return "Node<%s>" % self.label
    

    def has(tag):
        '''determine if a node has a tag
        '''
        # All supplied tags are in the list
        if isinstance(tag, list):
            if all(tag) in self.tags:
                return True

        # The single tag is in the list
        if tag in self.tags:
            return True
        return False
              

    def get_attributes(self):
        '''return all attributes of the node (aside from children)'''
        ats = {} 
        for key, val in self.__dict__.items():
            if key !="children":
                if isinstance(val, set):
                    val = list(val)
                ats[key] = val
        return ats


    def set_attributes(self, attrs):
        '''Set a variable number of attributes, likely
           size of the file/folder

           Parameters
           ==========
           attrs: a dict of key,value attribute pairs

        '''

        for name, value in attrs.items():
            self.__setattr__(name.lower(), value)
