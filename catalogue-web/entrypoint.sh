#!/bin/sh
echo "nginx start at $(date)"
exec nginx -g "daemon off;"