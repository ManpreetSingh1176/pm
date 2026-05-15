#!/usr/bin/env sh
if [ -z "$1" ]; then
  echo "Usage: $0 <pid>"
  exit 1
fi
kill "$1" || exit 1
