#!/bin/bash
set +x

# remove any lingering log files that might be owned by root
rm -f /galaxy_logs/*.log 

galaxy-manage migrate --noinput --fake-initial
honcho start 
