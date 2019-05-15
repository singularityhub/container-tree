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
from containertree.logger import bot
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

    def __init__(self, inputs=None, tag=None, first_level='library'):
        '''a collection tree is similar to a container tree, except instead
           of a filesystem we have a tree of containers, where we walk up
           the tree (finding parents via the Dockerfile) until we get to scratch
           or cannot proceed (with a 404, etc.) We produce a tree of containers
           that are based on FROM statements, and we obtain the metadata about
           the containers from container-diff. The root of the tree (scratch)
           is the only one to be of type "Node." We define the base family
           of the tree as library, and this is used to control what can be 
           added. If you don't want to limit the root node's first level,
           then set first_level to an empty string.
        '''

        # Update the root to be for scratch
        self.root = Node('scratch', {'size': 0, 'Name': 'scratch'}, tag=None)
        self.data = None
        self._first_level = first_level

        # Count the nodes
        self.count = 1

        # Keep an index of all nodes
        self._index = {'scratch': ''}     

        # Sets self.data and builds self.tree
        if inputs != None:
            self.load(inputs)

        # If data is loaded, make the tree
        if self.data:
            self._make_tree(tag=tag, first_level=first_level)

    def __str__(self):
        return "CollectionTree<%s>" % self.count
    def __repr__(self):
        return "CollectionTree<%s>" % self.count


# Add / Remove Operations


    def remove(self, name, node=None, tag=None):
        '''find a path in the tree and remove (and return) the node if found.
           The function returns None if the Node wasn't in the tree (and wasn't
           found and removed). The way this is designed, we cannot remove the
           root node (but we just return it). If a tag is not provided,
           remove entire node with children tags.
         '''

        # Special case of first call, run function on root
        if node == None:
            node = self.root
            return self.remove(name, node, tag)

        # Set removed node to None
        removed = None

        # Iterate through children, and look for name
        # The top level of the tree doesn't have tags
        if isinstance(node.children, list):
            for child in node.children:

                # Did we find the node?
                if child.label == name:

                    # Case 1: we are given a tag
                    if tag != None:
                        if tag in child.children:
                            del child.children[tag]

                    # Case 2: we delete the entire node (and all tags)
                    else:
                        node.children = [c for c in node.children if c != child]

                    # Return the deleted node
                    self.count -= 1
                    return child
                
                # If we don't find the node, look for it in child
                removed = self.remove(name, child, tag)
                if removed != None:
                    return removed

        # All other nodes have dictionaries
        else:

            for child_tag, children in node.children.items():

                for child in children:

                    # Did we find the node?
                    if child.label == name:

                        # Case 1: we are given a tag
                        if tag != None:
                            if tag in child.children:
                                del child.children[tag]

                        # Case 2: we delete the entire node (and all tags) from list
                        else: 
                            childs = node.children[child_tag]
                            childs = [c for c in childs if c != child]
                            node.children[child_tag] = childs

                        # Return the deleted node
                        self.count -= 1
                        return child
                  
                    # If we don't find the node, look for it in child
                    removed = self.remove(name, child, tag)
                    if removed != None:
                        return removed

        return removed


# Searching Functions

    def find(self, name, tag=None, node=None):
        '''find a container in the tree and return the node if found.
           This base function is suited for searches that don't build
           on themselves (e.g., not filepaths or words). If the user
           specifies a tag, return the node only if the tag is included.
           For addition of a new tag to a node, leave the tag blank to
           return the general collection node (and then add it)
        '''
        # Only do index search if started from root
        if node == None:
            node = self.root
            found = self._find(name, tag, node)
            if found != None:
                return found

        # Did we find the node?
        if node.label == name:

            # if no tag is defined, return the entire node
            if tag == None:
                return node

            # Unless they want a tag, return the tag
            if tag in node.children:
                return node

            # Otherwise, we found the node, but not the right tag
            else:
                return None
              
        # Search through children
        for child in node.get_children():
            found_node = self.find(name, tag, child)
            if found_node != None:
                return found_node


    def _find(self, name, tag, node):
        '''a helper to find that tries finding with the index first.
        '''
        found = None

        # Otherwise, check the index for the node
        if name in self._index:
            lookup = self._index[name].split('|')

            # Pop the root node
            lookup.pop(0)
            children = self.root.children

            while lookup:
                childname = lookup.pop(0)
                childtag = lookup.pop(0)

                node = [x for x in children if x.name == childname][0]
                children = node.children[childtag]
 
            for found in children:
                if found.name == name:
                    return found               

        return found

    def search(self, name, number=None, node=None, tag=None, exact=False):
        '''find a basename in the tree. If number is defined, return
           up to that number. If exact is True, only grab exact matches
        '''
        found = []
 
        # We always start at the root  
        if node == None:
            node = self.root

        # Look for the name in the current node
        if name in node.label:
            
            if tag == None:

                # Only add exact matches
                if exact == True and name == node.label:
                    found.append(node)
                elif exact == False:
                    found.append(node)
            else:
                if tag in node.children:

                    # Only add exact matches
                    if exact == True and name == node.label:
                        found.append(node)

                    # Allow user to specify name via <collection>/<repo>:<tag>
                    elif exact == True and name == "%s:%s" % (node.label, tag):
                        found.append(node)

        # No children, no search
        if len(node.children) == 0:
            return found

        # Does the user want to cut out early?
        if number != None:
            if len(found) >= number:
                return found

        # Recursively search over children
        for child in node.get_children():
            found += self.search(name, number, child, tag, exact)
            if number != None:
                if len(found) >= number:
                    return found

        return found           


    def trace(self, name, node=None):
        '''find a path in the tree and return the node if found.
            We don't take a tag, assuming that the node returned is unique for
            the container name, and thus will have any associated tags.
         '''
        if node == None:
            node = self.root

        # Find the node, is it in the tree?
        tracedNode = self.find(name)

        # Trace it's path
        if tracedNode != None:
            return self._trace(name, node, tracedNode)


    def _trace(self, name, node, targetNode, traces=None):
        '''find a path in the tree and return the node if found.
        '''
        if traces == None:
            traces = []

        # Always add node we are searching
        traces.append(node)

        # Case 1: the node IS the target node
        if node == targetNode:
            return traces

        # Case 2: We found a leaf node, so we need to reset traces
        if node.leaf == True:
            return []

        else:
            for child in node.get_children():
                traces = self._trace(name, child, targetNode, traces)
                if targetNode in traces:
                    return traces
                traces = []

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

        # Case 1: It's not valid to have a Dockerfile as the image URI
        if "Dockerfile" in uri:
            if os.path.exists(uri):
                bot.error('A Dockerfile only makes sense as a fromuri')
                bot.error('Did you correctly specify the variable order?')
                return None

        # Case 2. if we loaded a container-diff uri, it will be a uri
        if not "Dockerfile" in fromuri:     
            return {"Image": uri, "From": fromuri}

        # Case 3: Load the FROM in the Dockerfile            
        if os.path.exists(fromuri):
            froms = [x for x in self._load_dockerfile(fromuri, action="FROM") if x]

            # If we find the FROM, we want to extract history to get all from
            # In future, could support more than one from here
            if len(froms) > 0:
                 
                # We can't use any AS statements 
                if " as " in froms[0].lower():
                    return None

                # Remove any extra comments, etc. next to FROM <container>
                fromuri = froms[0].split(' ')[0]

                # Validate the uris
                for image in [uri, fromuri]:
                    if not parse_image_uri(image):
                        return None
                    # Don't allow uppercase or invalid endings
                    if image.isupper() or re.search('-$', image):
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
           a status of False indicates the uri/fromuri were valid, but not
           added / created / present in the tree. A value of None indicates
           the data was not parseable.
        '''
        # Loads {"Image": ... "From": ...}, unless Dockerfile not found
        data = self._load(uri, fromuri)

        # If we have loaded data, continue, returns True if nodes created/added
        if data:
            return self._make_tree(data['Image'], data['From'], tag=tag)


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

           Returns
           =======
           present: boolean to indicate if the nodes exist, typically meaning
                    they were created, added, or already found.
                    This boolean should be used to keep track of pairs that
                    weren't able to be added to the tree because of not having
                    a connection to the root.
        '''
        present = False

        # Parse the uri to get namespace, and rest
        uriImage = parse_image_uri(uri)
        uriFrom = parse_image_uri(fromuri)        

        # Update uri and fromuri
        uri = uriImage['nodeUri']

        # Special case of scratch
        if fromuri != 'scratch':
            fromuri = uriFrom['nodeUri']

        # Find the node in the tree, if it exists (the uri without tag/version)
        nodeImage = self.find(uri)
        nodeFrom = self.find(fromuri) 

        # If they both exist, and are added correctly, do nothing.
        if nodeImage != None and nodeFrom != None:

            # Only return already present if found with exact tag/parent
            if uriImage['repo_tag'] in nodeFrom.children:
                if nodeImage in nodeFrom.children[uriImage['repo_tag']]: 

                    # Ensure we have the child tag
                    if uriImage['repo_tag'] not in nodeImage.children:
                        nodeImage.children[uriImage['repo_tag']] = []
                    nodeImage.counter +=1
                    return True

        # Boolean to indicate add to root
        append_root = False
 
        # If FROM not in tree, create
        if nodeFrom == None:
            nodeFrom = MultiNode(fromuri, {"Name": fromuri })
            append_root = True

        # If the tag isn't there, add it (this is the parent)
        if isinstance(nodeFrom.children, dict):
            if uriFrom['repo_tag'] not in nodeFrom.children:
                nodeFrom.children[uriFrom['repo_tag']] = []

        # If node Image isn't in tree, create it
        if nodeImage == None:
            nodeImage = MultiNode(uri, {"Name": uri })
            nodeImage.leaf = True
            self.count += 1
        else:
            nodeImage.counter += 1

        # Add the (child) tag if it's not there
        if uriImage['repo_tag'] not in nodeImage.children:
            nodeImage.children[uriImage['repo_tag']] = []

        # Remove the nodeImage from the tree, if it's found
        self.remove(name = nodeImage.label)

        # Add the tag, if defined (this is not the uri tag, but another)
        if tag is not None:
            if tag not in nodeImage.tags:
                nodeImage.tags.add(tag)
       
        # Special case for the root node, update the lookup and add first level
        if nodeFrom == self.root:
            self._index[nodeImage.name] = self._index[nodeFrom.name]

            # The image isn't in root's children, but we can add it there!
            if nodeImage not in nodeFrom.children and nodeImage.label.startswith(self._first_level):
                nodeFrom.children.append(nodeImage)    
                present = True

        else:

            # We now have a nodeFrom and a nodeImage, we can append        
            if nodeImage not in nodeFrom.children[uriFrom['repo_tag']]:
                nodeFrom.children[uriFrom['repo_tag']].append(nodeImage)
                present = True

            # We only append library to the root.
            if append_root is True:

                # We can append
                if nodeFrom.label.startswith(self._first_level):

                    # If adding to the root, we likely don't have the parent node
                    if nodeFrom.name not in self._index:
                        self._index[nodeFrom.name] = self._index[self.root.name]

                    self._index[nodeImage.name] = '%s|%s|%s' %(self._index[nodeFrom.name],
                                                               nodeFrom.name,
                                                               uriFrom['repo_tag'])

                    if nodeFrom not in self.root.children:
                        self.root.children.append(nodeFrom)             
                    present = True

                # If we need to append to the root but the nodeFrom label isn't in it
                else:
                    present = False 

        # If it was a leaf, no longer is
        nodeFrom.leaf = False
        return present


# Export Functions

    def paths(self, leaves_only=False, 
                    add_tags=True, 
                    tag_prefix='.',
                    label=None):

        '''Get all paths to nodes, as an iterator

           Parameters
           ==========
           leaves_only: only get leaf nodes
           add_tags: add tags to tree (also as folders)
           tag_prefix: if adding tags, use this prefix.
           label: get the path for one (string) or more (list) nodes.
        '''

        def traverse(current, path='', label=None):

            # Update the path with the current
            path = path + '/' + current.name

            # Does the user want to export leaves only?
            if (leaves_only and current.leaf) or not leaves_only:

                # Does the user only want specific label(s)?
                if label != None:
                    if current.name in label:
                        label.remove(current.name)
                        yield path
                else:
                    yield path

            # Case 1: We are at the root (and have list)
            if isinstance(current.children, list):
                for child in current.children:
                    for new_path in traverse(child, path, label):
                        yield new_path

            # Case 2: we have a dictionary
            else:
                for tag, children in current.children.items():
                    for child in children:

                        # tags are represented by hidden folders
                        if add_tags:
                            new_path = path + '/' + tag_prefix + tag

                        # But if the user doesn't want that detail
                        else:
                            new_path = path

                        # Reveal the paths
                        for new_path in traverse(child, new_path, label):
                            yield new_path

        # Does the user want a particular set of labels?
        if label != None:
            if not isinstance(label, list):
                label = [label]

            # Create a set for more efficient lookup
            label = set(label)

        for path in traverse(self.root, label=label):
            yield path


    def get_paths(self, leaves_only=False, add_tags=True, tag_prefix='.', label=None):

        '''Get all paths to nodes, in a list.

           Parameters
           ==========
           leaves_only: only get leaf nodes
           add_tags: add tags to tree (also as folders)
           tag_prefix: if adding tags, use this prefix.
           label: get the path for one (string) or more (list) nodes.
        '''
        return list(self.paths(add_tags=add_tags,
                               leaves_only=leaves_only, 
                               tag_prefix=tag_prefix,
                               label=label))


    def get_nodes(self):
        '''return a list of nodes (a call to __iter__)
        '''
        return list(self.__iter__())


    def __iter__(self):
        '''an iterator over MultiNodes to yield nodes, one at a time.
        '''
        def traverse(current, seen):
            for child in current.get_children():
                if child.name not in seen:
                    seen.add(child.name)
                    yield child
                    for child in traverse(child, seen):
                        yield child

        seen = set()
        for node in traverse(self.root, seen):
            yield node  


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

            # Traverse remainder of children
            for child in current.get_children():
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
