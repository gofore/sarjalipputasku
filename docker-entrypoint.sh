#!/bin/bash
set -eo pipefail
shopt -s nullglob
/usr/local/bin/gunicorn -w 2 -b 0.0.0.0:8000 server:app
