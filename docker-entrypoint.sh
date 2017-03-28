#!/bin/bash
export OAUTHLIB_INSECURE_TRANSPORT=1
export OAUTHLIB_RELAX_TOKEN_SCOPE=1
export ENV SARJALIPPUTASKU_DIR=/webapps/sarjalipputasku/config/app.cfg
/usr/local/bin/gunicorn -w 2 -b 0.0.0.0:8000 --reload server:app
