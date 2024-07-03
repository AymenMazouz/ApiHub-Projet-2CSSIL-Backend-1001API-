#!/bin/sh

flask db upgrade
echo "Database upgraded"
exec "$@"