# Description: Dockerfile for local development environment
# Build: docker build -f local_deployment/Dockerfile -t local_deployment .
FROM ubuntu:jammy

# Preparation layer
RUN DEBIAN_FRONTEND=noninteractive apt update --fix-missing && \
  ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
  apt install -y software-properties-common

# Build working python layer with all the correct dependencies
RUN apt install -y libffi-dev libssl-dev build-essential zlib1g-dev libpq-dev && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt update && \
  apt install -y python3.12 python3.12-dev python3.12-venv && \
  update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 && \
  update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Bootstrapping the pip installer
RUN python -m ensurepip --upgrade && \
  python -m pip install --upgrade pip && \
  python -m pip install --upgrade setuptools && \
  update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3 1

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  DEBUG=1 \
  DJANGO_ADMIN=1 \
  DJANGO_SETTINGS_MODULE=fbr.settings

# Install nodejs
RUN apt install -y curl && \
  curl -sL https://deb.nodesource.com/setup_20.x | bash - && \
  apt install -y nodejs

RUN apt install -y openssl

WORKDIR /app

# Install Django Extensions
RUN pip install django-extensions

RUN pip install poetry

# Copy only the requirements.txt into the container
COPY requirements.txt /app/

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

COPY . /app

COPY entry.sh /entry.sh
RUN chmod +x /entry.sh
ENTRYPOINT ["/entry.sh"]
