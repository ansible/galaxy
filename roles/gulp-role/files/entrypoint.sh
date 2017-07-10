#!/bin/bash 
set -x

/usr/bin/gulp build

exec "$@"
