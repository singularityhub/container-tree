'''

Copyright (C) 2018-2019 Vanessa Sochat.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import json
import math
import os
import re
import requests
import shutil
import sys
import tempfile
from .https import get, call

########################################################################
# Parsing URIs: we assume the user will provide registry and/or ports
###############################################################################

_reduced_uri = re.compile("(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
                          "(?P<repo>[^:@/]+)"
                          "(?::(?P<tag>[^:@]+))?"
                          "(?:@(?P<version>.+))?"
                          "$"
                          "(?P<namespace>.)?")

_docker_uri = re.compile("(?:(?P<registry>[^/@]+[.:][^/@]*)/)?"
                         "(?P<namespace>(?:[^:@/]+/)+)?"
                         "(?P<repo>[^:@/]+)"
                         "(?::(?P<tag>[^:@]+))?"
                         "(?:@(?P<version>.+))?"
                         "$")

_default_uri = re.compile("(?:(?P<registry>[^/@]+)/)?"
                          "(?P<namespace>(?:[^:@/]+/)+)"
                          "(?P<repo>[^:@/]+)"
                          "(?::(?P<tag>[^:@]+))?"
                          "(?:@(?P<version>.+))?"
                          "$")

def parse_image_uri(image, default_tag='latest', default_namespace='library'):
    '''parse the image uri and return a dictionary to look up namespace,
       tag, and registry. If the name doesn't match a pattern, we return None.

       Parameters
       ==========
       image: the full image uri (e.g., library/ubuntu:latest
       default_tag: the image tag (e.g., latest) default is latest
       default_namespace: the default collection (e.g., library)
    '''

    # Match from docker to default
    uri_regexes = [ _docker_uri,
                    _reduced_uri,
                    _default_uri ]

    for r in uri_regexes:
        match = r.match(image)
        if match:
            break

    if not match:
        # Calling client should expect None to indicate not parseable
        print('Could not parse image %s' % image)
        return None

    registry = match.group('registry')
    namespace = match.group('namespace')
    repo_name = match.group('repo')
    repo_tag = match.group('tag')
    version = match.group('version')

    if namespace:
        namespace = namespace.rstrip('/')

    # replace empty fields with defaults
    if not namespace:
        namespace = default_namespace
    if not repo_tag:
        repo_tag = default_tag

    # Full uri (without registry)
    nodeuri = "%s/%s" %(namespace, repo_name)
    fulluri = nodeuri
    if repo_tag != None:
        fulluri = "%s:%s" %(fulluri, repo_tag)
    if version != None:
        fulluri = "%s@%s" %(fulluri, version)

    # We don't require registry, or version.
    parsed = {'registry': registry,
              'namespace': namespace,
              'repo_name': repo_name,
              'repo_tag': repo_tag,
              'version': version,
              'fullUri': fulluri,
              'nodeUri': nodeuri }

    return parsed


class DockerInspector(object):

    def __init__(self, container_name=None, base=None, version=None):
        self.manifests = {}
        self.uri = container_name
        self._set_base(base, version)
        self.headers = {'Content-Type':"application/json"}

    def __str__(self):
        return "DockerInspector<%s>" % self.uri
    def __repr__(self):
        return "DockerInspector<%s>" % self.uri


    def _set_base(self, base=None, version=None):
        '''set the API base or default to use Docker Hub. 
        '''
        if base is None:
            base = "index.docker.io"

        if version is None:
            version = "v2"

        # <protocol>://<base>/<version>

        self._base = "https://%s" % base
        self._version = version
        self.base = "%s/%s" %(self._base.strip('/'), version)
    
    def update_token(self, response):
        '''update_token uses HTTP basic authentication to get a token for
           Docker registry API V2 operations. We get here if a 401 is
           returned for a request.
    
           Parameters
           ==========
           response: the http request response to parse for the challenge.
    
           https://docs.docker.com/registry/spec/auth/token/
        '''

        not_asking_auth = "Www-Authenticate" not in response.headers
        if response.status_code != 401 or not_asking_auth:
            print("Authentication error, exiting.")
            sys.exit(1)

        challenge = response.headers["Www-Authenticate"]
        regexp = '^Bearer\s+realm="(.+)",service="(.+)",scope="(.+)",?'
        match = re.match(regexp, challenge)

        if not match:
            print("Unrecognized authentication challenge, exiting.")
            sys.exit(1)

        realm = match.group(1)
        service = match.group(2)
        scope = match.group(3).split(',')[0]

        token_url = realm + '?service=' + service + '&expires_in=900&scope=' + scope
    
        # Default headers must be False so that client's current headers not used
        response = self._get(token_url)

        try:
            token = response["token"]
            token = {"Authorization": "Bearer %s" % token}
            self.headers.update(token)

        except Exception:
            print("Error getting token.")
            sys.exit(1)

    def get_manifests(self, digest=None):
        '''get_manifests calls get_manifest for each of the schema versions,
           including v2 and v1. Version 1 includes image layers and metadata,
           and version 2 must be parsed for a specific manifest, and the 2nd
           call includes the layers. If a digest is not provided
           latest is used.

           Parameters
           ==========
           repo_name: reference to the <username>/<repository>:<tag> to obtain
           digest: a tag or shasum version
        '''
    
        # Obtain schema version 1 (metadata) and 2, and image config
        schemaVersions = ['v1', 'v2', 'config']
        for schemaVersion in schemaVersions:
            manifest = self._get_manifest(digest, schemaVersion)
            if manifest is not None:

                # If we don't have a config yet, try to get from version 2 manifest
                if schemaVersion == "v2" and "config" in manifest:
                    print('Attempting to get config as blob in verison 2 manifest')
                    url = self._get_layerLink(repo_name, manifest['config']['digest'])        
                    headers = {'Accept': manifest['config']['mediaType']}
                    self.manifests['config'] = self._get(url, headers=headers)
    
                self.manifests[schemaVersion] = manifest

        return self.manifests


    def get_manifest_selfLink(self, digest=None):
        ''' get a selfLink for the manifest, for use by the client get_manifest
            function, along with the parents pull
     
           Parameters
           ==========
           digest: a tag or shasum version

        '''
        url = "%s/%s/manifests" % (self.base, self.uri)

        # Add a digest - a tag or hash (version)
        if digest is None:
            digest = 'latest'
        return "%s/%s" % (url, digest)


    def get_manifest(self, digest=None, version="v1"):
        '''
           get_manifest should return an image manifest
           for a particular repo and tag.  The image details
           are extracted when the client is generated.
    
           Parameters
           ==========
           digest: a tag or shasum version
           version: one of v1, v2, and config (for image config)

        '''
        manifest = None
        accepts = {'config': "application/vnd.docker.container.image.v1+json",
                   'v1': "application/vnd.docker.distribution.manifest.v1+json",
                   'v2': "application/vnd.docker.distribution.manifest.v2+json" }

        url = self.get_manifest_selfLink(digest)
    
        print("Obtaining manifest: %s" % url)
        headers = {'Accept': accepts[version] }

        try:
            manifest = self._get(url, headers=headers)
            manifest['selfLink'] = url
        except:
            pass

        return manifest
 

################################################################################
# Metadata (Environment, Labels, Runscript)
################################################################################


    def get_config(self, key="Entrypoint", delim=None):
        '''get_config returns a particular key (default is Entrypoint)
            from a VERSION 1 manifest obtained with get_manifest.
    
            Parameters
            ==========
            key: the key to return from the manifest config
            delim: Given a list, the delim to use to join the entries.
            Default is newline

        '''
        cmd = None
    
        # If we didn't find the config value in version 2
        for version in ['config', 'v1']:
            if cmd is None and 'config' in self.manifests:
                
                # First try, version 2.0 manifest config has upper level config
                manifest = self.manifests['config']
                if "config" in manifest:
                    if key in manifest['config']:
                        cmd = manifest['config'][key]
    
                # Second try, config manifest (not from verison 2.0 schema blob)
    
                if cmd is None and "history" in manifest:
                    for entry in manifest['history']:
                        if 'v1Compatibility' in entry:
                            entry = json.loads(entry['v1Compatibility'])
                            if "config" in entry:
                                if key in entry["config"]:
                                    cmd = entry["config"][key]
    
        # Standard is to include commands like ['/bin/sh']
        if isinstance(cmd, list):
            if delim is not None:
                cmd = delim.join(cmd)
        print("Found Docker config (%s) %s" % (key, cmd))
        return cmd

DockerInspector._get = get
DockerInspector._call = call
