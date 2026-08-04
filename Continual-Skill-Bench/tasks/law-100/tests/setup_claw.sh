#!/bin/bash
set -e
mkdir -p /app/workspace
if [ -d /root/data ]; then
  cp -r /root/data /app/workspace/ || true
fi
