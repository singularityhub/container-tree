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

import os
from copy import deepcopy
from random import choice
from containertree.utils import (
    check_install, 
    parse_image_uri
)
import requests
import json
import re

from .node import ( MultiNode, Node )
from .loading import (
    _load_http,
    _load_list,
    _load_json,
    _load_container_diff,
    _update
)


class CollectionTree(object):

    def __init__(self, inputs=None, tag=None):
        '''a collection tree is similar to a container tree, except instead
           of a filesystem we have a tree of containers, where we walk up
           the tree (finding parents via the Dockerfile) until we get to scratch
           or cannot proceed (with a 404, etc.) We produce a tree of containers
           that are based on FROM statements, and we obtain the metadata about
           the containers from container-diff. The root of the tree (scratch)
           is the only one to be of type "Node"
        '''

        # Update the root to be for scratch
        self.root = Node('scratch', {'size': 0, 'Name': 'scratch'}, tag=None)
        self.data = None
         
        # Count the nodes
        self.count = 1
        
        # Sets self.data and builds self.tree
        if inputs != None:
            self.load(inputs)

        # If data is loaded, make the tree
        if self.data:
            self._make_tree(tag=tag)

    def __str__(self):
        return "CollectionTree<%s>" % self.count
    def __repr__(self):
        return "CollectionTree<%s>" % self.count

# Add / Remove Operations


    def remove(self, name, node=None, tag=None, parent=None, parent_tag=None, idx=None):
        '''find a path in the tree and remove (and return) the node if found.
           The function returns None if the Node wasn't in the tree (and wasn't
           found and removed). The way this is designed, we cannot remove the
           root node (but we just return it). If a tag is not provided,
           remove entire node with children tags.
         '''

        if node == None:
            node = self.root

        # Did we find the node based on name?
        if node.label == name:

            removed = deepcopy(node)

            # Case 1: we want to remove the entire namespace
            if tag == None:          
                del node

            # Otherwise copy the node, remove from parent
            elif tag in node.children:
               
               # Only keep tag of interest
               new_children = {tag : removed.children[tag]}
               removed.children = new_children
         
               # Remove tag from the node always
               del node.children[tag]

               # If no more children tags, remove entire node
               if len(node.children) == 0:
                   if parent_tag != None:
                       del parent.children[parent_tag][idx]
                   else:
                       del parent.children[idx]

            return removed

        # Are we starting at scratch?
        elif isinstance(node.children, list):

            for c in range(len(node.children)):
                child = node.children[c]
                removed = self.remove(name, child, tag, node, idx=c)
                if removed != None:
                    return removed
        else:

            # Continue searching through children
            for child_tag in node.children:
                children = node.children[child_tag]

                # Skip over empty lists of children
                if len(children) > 0:

                    for c in range(len(children)):
                        child = children[c]

                        # Use parent, child, and current tag to locate in tree
                        removed = self.remove(name, child, tag, node, child_tag, c)
                        if removed != None:
                            return removed
        return None


# Searching Functions

    def find(self, name, tag=None, node=None):
        '''find a container in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words). If the user
           specifies a tag, return the node only if the tag is included.
           For addition of a new tag to a node, leave the tag blank to
           return the general collection node (and then add it)
         '''

        if node == None:
            node = self.root

        # Did we find the node?
        if node.label == name:
            # if no tag is defined, return the entire node
            if tag == None:
                return node
            if tag in node.children:
                return node

        # Absolutely no children
        if len(node.children) == 0:
            return None

        # Are we at the root?
        if isinstance(node.children, list):
            for child in node.children:
                found_node = self.find(name, tag, child)
                if found_node != None:
                    return found_node
            return None

        # Otherwise (type dict), search children organized by tag
        for child_tag in node.children:
            for child in node.children[child_tag]:
                found_node = self.find(name, tag, child)
                if found_node != None:
                    return found_node

        return None


    def search(self, name, number=None, node=None, tag=None):
        '''find a basename in the tree. If number is defined, return
           up to that number. 
        '''
        found = []
 
        # We always start at the root  
        if node == None:
            node = self.root

        # Look for the name in the current node
        if name in node.label:
            if tag == None:
                found.append(node)
            else:
                if tag in node.children:
                    found.append(node)

        # No children, no search
        if len(node.children) == 0:
            return found

        # Does the user want to cut out early?
        if number != None:
            if len(found) >= number:
                return found

        # Not at current node, search children!
        for child_tag in node.children:
            for children in node.children[child_tag]:
                for child in children:
                    found += self.search(name, number, child, tag)
                    if number != None:
                        if len(found) >= number:
                            return found
        return found           


    def trace(self, name, node=None, tag=None):
        '''find a path in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words)
         '''
        if node == None:
            node = self.root

        # Find the node, is it in the tree?
        tracedNode = self.find(name, tag=tag)

        # Trace it's path
        if tracedNode != None:
            for child_tag in node.children:
                children = node.children[child_tag]
                for child in children:
                    traces = self._trace(name, child, tag)
                    if tracedNode in traces:
                        return [self.root] + traces


    def _trace(self, name, node, tag=None, traces=None):
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
            if node.label == name and tag in node.children:
                return traces
            else:
                traces = []

        # Keep searching over children        
        for child_tag in node.children:
            for children in node.children[child_tag]:
                for child in children:
                    self._trace(name, child, tag, traces)
        return traces


# Loading Functions

    def load(self, uri, fromuri, tag=None):
        ''' uri must be the uri for a container. fromuri can be a uri OR
            a Dockerfile for the uri given (to extract from)
        '''
        self.update(uri, fromuri, tag)


    def _load(self, uri, fromuri):
        '''when we start here, we've been passed a Dockerfile.
        '''

        # Case 1. if we loaded a container-diff uri, it will be a uri
        if not "Dockerfile" in fromuri:     
            return {"Image": uri, "From": fromuri}

        # Case 2: Load the FROM in the Dockerfile            
        if os.path.exists(fromuri):
            froms = [x for x in self._load_dockerfile(fromuri, action="FROM") if x]

            # If we find the FROM, we want to extract history to get all from
            # In future, could support more than one from here
            if len(froms) > 0:
                 
                # Some containers have "as build, etc."
                fromuri = froms[0].split(' ')[0]

                # Validate the uris
                for image in [uri, fromuri]:
                    if not parse_image_uri(image):
                        return None

                # Don't allow environment vars or similar
                literals = ['$', '}', '{', "'", '"']
                expression = "(%s)" % '|'.join(["[%s]" %x for x in literals])
                regexp = re.compile(expression)

                # Another condition for not parsing, if a variable is in uri
                if not regexp.search(uri) and not regexp.search(fromuri):
                    return {"Image": uri, "From": fromuri}


    def _load_dockerfile(self, dockerfile, action=None):
        '''extract one or more actions from a Dockerfile. If action is not
           defined, then return all that are found.
        '''
        lines = []
        with open(dockerfile, 'r') as filey:
            for line in filey.readlines():
                if action != None:
                    match = re.search("^%s" % action.upper(), line.strip().upper())
                    if match:
                        line = (line[match.end()+1:]).strip()
                        lines.append(line)
                else:
                    lines.append(line)
        return lines



    def update(self, uri, fromuri, tag=None):
        '''update will load in new data (without distributing an old self.data)
        '''

        # Loads {"Image": ... "From": ...}, unless Dockerfile not found
        data = self._load(uri, fromuri)

        # If we have loaded data, continue
        if data:
            self._make_tree(data['Image'], data['From'], tag=tag)


# Tree Generation


    def _make_tree(self, uri, fromuri, tag=None):
        '''construct the tree from the loaded data (self.data) which for
           this collection tree is a URI for a Docker image. Since we are making
           the tree starting with a single container and building based on
           FROM statements, the nodes correspond to different containers,
           and they are tagged with container tags.

           The tree has a structure that has namespace as node, and tags
           as internal dictionaries to point to lists of children. For
           example:
 
               Node<mhart/alpine-node>
                  {"children":     
                      {"4": [] }
                      {"6": [] }
                  }

           When we export the tree, the children get combined into one list
           and tagged with their parent tag.

           Parameters
           ==========
           uri: the container uri to add
           fromuri: the from uri (the parent of the container, or it's base)
           tag: if defined, a tag to give the node (not the container tag)
        '''
        # Parse the uri to get namespace, and rest
        uriImage = parse_image_uri(uri)
        uriFrom = parse_image_uri(fromuri)        

        # Update uri and fromuri
        uri = uriImage['nodeUri']
        fromuri = uriFrom['nodeUri']

        # Find the node in the tree, if it exists (the uri without tag/version)
        nodeImage = self.find(uri)
        nodeFrom = self.find(fromuri) 

        # Boolean to indicate add to root
        append_root = False
 
        # If FROM not in tree, create
        if nodeFrom == None:
            nodeFrom = MultiNode(fromuri, {"Name": fromuri })
            append_root = True
        else:
            nodeFrom.counter += 1

        # If the tag isn't there, add it
        if uriFrom['repo_tag'] not in nodeFrom.children:
            nodeFrom.children[uriFrom['repo_tag']] = []

        # If node Image isn't in tree, create it
        if nodeImage == None:
            nodeImage = MultiNode(uri, {"Name": uri })
            nodeImage.leaf = True
        else:
            nodeImage.counter += 1

        # Add the tag if it's not there
        if uriImage['repo_tag'] not in nodeImage.children:
            nodeImage.children[uriImage['repo_tag']] = []

        # We now have a nodeFrom and a nodeImage, append nodeImage
        nodeFrom.children[uriFrom['repo_tag']].append(nodeImage)

        # We only append library to the root.
        if append_root is True and nodeFrom.label.startswith('library'):
            if nodeFrom not in self.root.children:
                self.root.children.append(nodeFrom)

        if tag is not None:
            if tag not in nodeImage.tags:
                nodeImage.tags.add(tag)



    def _makeda_tree(self, uri, fromuri, tag=None):
        '''construct the tree from the loaded data (self.data) which for
           this collection tree is a URI for a Docker image. Since we are making
           the tree starting with a single container and building based on
           FROM statements, the nodes correspond to different containers,
           and they are tagged with container tags.

           The tree has a structure that has namespace as node, and tags
           as internal dictionaries to point to lists of children. For
           example:
 
               Node<mhart/alpine-node>
                  {"children":     
                      {"4": [] }
                      {"6": [] }
                  }

           When we export the tree, the children get combined into one list
           and tagged with their parent tag.

           Parameters
           ==========
           uri: the container uri to add
           fromuri: the from uri (the parent of the container, or it's base)
           tag: if defined, a tag to give the node (not the container tag)
        '''
        # Parse the uri to get namespace, and rest
        uriImage = parse_image_uri(uri)
        uriFrom = parse_image_uri(fromuri)        

        # Update uri and fromuri
        uri = uriImage['nodeUri']
        fromuri = uriFrom['nodeUri']

        # Find the node in the tree, if it exists (the uri without tag/version)
        nodeImage = self.find(uri, tag=uriImage['repo_tag'])
        nodeFrom = self.find(fromuri, tag=uriFrom['repo_tag'])  

        # Case 1: Both Child and Parent are in Tree
        if nodeImage != None and nodeFrom != None:
            nodeImage.counter += 1
            nodeFrom.counter += 1

        # Case 2: Parent is in tree, but not child
        elif nodeImage == None and nodeFrom != None:
            nodeImage = MultiNode(uri, {"Name": uri })
            nodeImage.leaf = True

            # Tags for image represented until children
            nodeImage.children[uriImage['repo_tag']] = []

            # Add the tag as a child (we found node, we know tag is there)
            # Case 2A: nodeFrom is the root, scratch doesn't have tags
            if isinstance(nodeFrom.children, list):
                nodeFrom.children.append(nodeImage)
            else:
                nodeFrom.children[uriFrom['repo_tag']].append(nodeImage)

        # Case 3: Child is in tree, but not parent
        elif nodeImage != None and nodeFrom == None:

            # Look to see if node exists (we know tag doesn't)
            nodeFrom = self.find(fromuri)  
            
            # If still None, we need an entire new Node!
            if nodeFrom == None:
                nodeFrom = MultiNode(fromuri, {"Name": fromuri })

            # Do we need to add the tag?
            if uriFrom['repo_tag'] not in nodeFrom.children:
                nodeFrom.children[uriFrom['repo_tag']] = []

            # Remove the nodeImage (just removes the tag, returns node
            # with just that tag
            nodeImage = self.remove(name=uri, tag=uriImage['repo_tag'])
            nodeImage.counter += 1

            # Add as child to new parent (this is first tag defined)
            nodeFrom.children[uriFrom['repo_tag']].append(nodeImage)

            # If we found it on the second try, might already exist 
            if nodeFrom not in self.root.children:
                self.root.children.append(nodeFrom)

        # Case 4: Both aren't in tree
        if nodeImage == None and nodeFrom == None:
            nodeFrom = MultiNode(fromuri, {"Name": fromuri })
            nodeImage = MultiNode(uri, {"Name": uri })
            nodeImage.leaf = True
            nodeImage.children[uriImage['repo_tag']] = []
            nodeFrom.children[uriFrom['repo_tag']] = [nodeImage]
            self.root.children.append(nodeFrom)

        if tag is not None:
            if tag not in nodeImage.tags:
                nodeImage.tags.add(tag)



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

            # If not the root node (scratch, tags are in keys)
            if not isinstance(current.children, list):
                tags += list(current.children.keys())

            new_node = {'color': choice(colors),
                        'key': current.label,
                        'name': current.label,
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

            # Case 1: We are at the root (and have list)
            if isinstance(current.children, list):
                children = current.children
            else:
                children = []
                for tag in current.children:
                    children += current.children[tag]

            # Traverse remainder of children
            for child in children:
                traverse(nodes=new_node, current=child)

        nodes = dict()
        traverse(nodes)
                
        # If the user provided a file, export to it
        if filename is not None:
            with open(filename, 'w') as filey:
                filey.writelines(json.dumps(nodes))
            return filename

        return nodes
       
    def get_count(self, name, tag=None):
        '''find a path in the tree and return the node if found
        '''
        counter = 0
        node = self.find(name, tag=tag)
        if node:
            counter = node.counter
        return counter


# Loading Functions
CollectionTree._update = _update
CollectionTree._load_http = _load_http
CollectionTree._load_list = _load_list
CollectionTree._load_json = _load_json
CollectionTree._load_container_diff = _load_container_diff
