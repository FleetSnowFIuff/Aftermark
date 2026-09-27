#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 -m venv .venv
.venv/bin/python -m pip install -e .
printf '%s\n' 'Ready. Run: sh start-aftermark.sh'
