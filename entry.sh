#!/bin/sh -e

# Set NODE_ENV to production
export NODE_ENV=production

# Set NODE_ENV to production only in staging and prod environments
# if [ "$COPILOT_ENVIRONMENT_NAME" = "staging" ] || [ "$COPILOT_ENVIRONMENT_NAME" = "prod" ]; then
#   export NODE_ENV=production
# else
#   export NODE_ENV=development
# fi

# Install Node.js dependencies
echo "Installing node modules..."
npm install

# Build the frontend assets with Webpack
echo "Bundling WebPack..."
npm run build

# Collect Django static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Set paths for the certificate and key
CERT_FILE=/app/ssl/certificate.crt
KEY_FILE=/app/ssl/private_key.key

# Ensure the SSL directory exists
mkdir -p /app/ssl

# Check if certificate and key already exist, generate them if not
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
  echo "Generating self-signed certificate..."
  openssl req -x509 -newkey rsa:4096 -keyout "$KEY_FILE" -out "$CERT_FILE" \
      -days 365 -nodes -subj "/CN=localhost"
else
  echo "Using existing SSL certificate and key."
fi

# Run Django server with SSL support
echo "Starting server with HTTPS..."
exec python manage.py runserver_plus 0.0.0.0:8080 --cert-file "$CERT_FILE" --key-file "$KEY_FILE"
