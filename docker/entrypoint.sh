#!/bin/bash

# If the user asks for a demo, run the generate example
if [ $# -eq 1 ]
  then
    if [ "${1}"  == "demo" ];
        then
            python3 /code/examples/files_tree/generate.py;
            exit 0;
    fi

fi

# Otherwise, forward to containertree executable
exec containertree ${@}
