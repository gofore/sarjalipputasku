#!/bin/bash
export OAUTHLIB_INSECURE_TRANSPORT=1
export OAUTHLIB_RELAX_TOKEN_SCOPE=1
/usr/local/bin/gunicorn -w 2 -b 0.0.0.0:8000 server:app
