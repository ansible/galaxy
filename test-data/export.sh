#!/bin/bash


pg_dump -h postgres -U galaxy -a -t main_role -t main_role_* -t main_platform -t main_category \
-t main_tag -t main_roleversion -t main_namespace galaxy | gzip >/galaxy/test-data/role_data.dmp.gz
