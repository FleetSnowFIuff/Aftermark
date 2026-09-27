#!/bin/sh
set -eu
cd "$(dirname "$0")"
exec .venv/bin/python -m aftermark --data-dir "$PWD/.local/library" serve --open
