#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied
export BUILD_STEP='True'
export COPILOT_ENVIRONMENT_NAME='build'
export DJANGO_SETTINGS_MODULE="fbr.settings"

# Set NODE_ENV to production
export NODE_ENV=production

python manage.py collectstatic --noinput
