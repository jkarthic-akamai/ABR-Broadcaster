#!/bin/bash

set -e
if [ -d "wsgi-scripts/db" ]; then
	rm -rf wsgi-scripts/db
fi
mkdir wsgi-scripts/db
chmod 777 wsgi-scripts/db
