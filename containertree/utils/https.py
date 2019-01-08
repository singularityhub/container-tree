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
import sys
import requests

def call(self, url, func, data=None,
                          headers=None, 
                          return_json=True,
                          retry=True,
                          default_headers=True,
                          quiet=False):

    '''call will issue the call, and issue a refresh token
       given a 401 response, and if the client has a _update_token function

       Parameters
       ==========
       func: the function (eg, post, get) to call
       url: the url to send file to
       headers: if not None, update the client self.headers with dictionary
       data: additional data to add to the request
       return_json: return json if successful
       default_headers: use the client's self.headers (default True)

    '''
 
    if data is not None:
        if not isinstance(data, dict):
            data = json.dumps(data)

    heads = dict()
    if default_headers is True:
        heads = self.headers.copy()
    
    if headers is not None:
        if isinstance(headers, dict):
            heads.update(headers)

    response = func(url=url,
                    headers=heads,
                    data=data)

    # Errored response, try again with refresh
    if response.status_code in [500, 502]:
        print("Beep boop! %s: %s" %(response.reason,
                                    response.status_code))
        sys.exit(1)

    # Errored response, try again with refresh
    if response.status_code == 404:

        # Not found, we might want to continue on
        if quiet is False:
            prints("Beep boop! %s: %s" %(response.reason,
                                         response.status_code))
        sys.exit(1)


    # Errored response, try again with refresh
    if response.status_code == 401:

        # If client has method to update token, try it once
        if retry is True and hasattr(self,'update_token'):

            # A result of None indicates no update to the call
            self.update_token(response)
            return self._call(url, func, data=data,
                              headers=headers,
                              return_json=return_json,
                              stream=stream, retry=False)

        bot.error("Your credentials are expired! %s: %s" %(response.reason,
                                                           response.status_code))
        sys.exit(1)

    elif response.status_code == 200:

        if return_json:

            try:
                response = response.json()
            except ValueError:
                bot.error("The server returned a malformed response.")
                sys.exit(1)

    return response

def get(self,url,
             headers=None,
             token=None,
             data=None,
             return_json=True,
             default_headers=True,
             quiet=False):

    '''get will use requests to get a particular url
    '''
    print("GET %s" % url)
    return self._call(url,
                      headers=headers,
                      func=requests.get,
                      data=data,
                      return_json=return_json,
                      default_headers=default_headers,
                      quiet=quiet)
