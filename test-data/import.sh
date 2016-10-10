#!/bin/bash

psql -h postgres -d galaxy -U galaxy -f /galaxy/test-data/disable_triggers.sql
cat /galaxy/test-data/role_data.dmp.gz | gunzip | psql -h postgres -d galaxy -U galaxy 
psql -h postgres -d galaxy -U galaxy -f /galaxy/test-data/enable_triggers.sql
