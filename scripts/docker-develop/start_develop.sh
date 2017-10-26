#!/bin/bash
set +x

cd /galaxy

honcho start -f "scripts/docker-develop/Procfile"
