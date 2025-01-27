# Find business regulations

## Introduction

Find business regulations will provide a searchable and filterable list of UK regulations and legislation.

## Getting Started

The quickest way top get started is to use the `docker-compose` configuration
to run the application and required `PostgreSQL` in a containerised environment.
Most of the actions required to run and manage the application are encapsulated
in the `Makefile`. First, in a working directory run:

    $ git clone git@github.com:uktrade/find-business-regulations.git
    $ cd find-business-regulations

The docker compose configuration requires that a `local.env` file is present.
An example file is provided in the repository. Create one like this:

    $ cp local.env.example local.env

This should work out of the box.

Create the initial database:

    $ make database

> The `make database` command will create a `PostgreSQL` database. If you have
> an existing database and want to start from scratch, use `make drop-database`
> to delete an existing database first.

Prepare the application for first use:

    $ make first-use

Start the services:

    $ make start

> You may see [Sass deprecation warnings](https://frontend.design-system.service.gov.uk/installing-with-npm/#requirements), but these can be ignored.

Navigate a browser to:

    https://localhost:8081

## Local development environment

While the `docker-compose` configuration is the quickest way to get started, it
can also be useful to create a development environment on your local machine.
However, your mileage may vary depending on your operating system. The following
instructions are for OSX.

### Prerequisites

As we are using python package `psycopg-c`, you need the PostgreSQL client
development headers (e.g. the `libpq-dev` package) installed on your system.
On Mac you can run the following command to install `libpq`:

    $ brew install libpq

> Note the dev files are included using this command.

### Requirements

- [`Python 3.12.*`](https://www.python.org/downloads/). Don't be tempted to use
  an earlier or later version of Python. Use Poetry to manage your Python version
  and dependencies.
- [`PostgreSQL`](https://www.postgresql.org/). Optionally you can install and
  configure `PostgreSQL` on your local machine. However, be advised it's much
  easier to use the `db` service provisioned by the `docker-compose`
  configuration which is exposed on `localhost:5432`. Additionally, client
  applications like `psql` and `pg_dump` are installed using the `libpq`
  installation [prerequisite](#prerequisites) step above.
- [`Docker Desktop`](https://docs.docker.com/get-docker/). A recent version
  (e.g. `4.30.0` or above) is recommended, which includes all the key components
  you'll require including `engine`, `build` and `compose`.

### Install Poetry

We use [Poetry](https://python-poetry.org/) to manage dependencies. Follow the
guidance in the [official documentation](https://python-poetry.org/docs/). On
OSX, run the following commands to install Poetry:

    $ brew install pipx
    $ pipx ensurepath
    $ pipx install poetry

Restart your terminal.

### Create a Poetry env and activate it

    $ poetry install
    $ poetry shell

### Installing pre-commit hooks

With your Poetry shell active:

    $ pre-commit install

> This will ensure that your code passes quality checks before you commit it.
> Code quality checks are also performed when pushing your code to origin
> but pre-commit hooks catch issues early and will improve Developer Experience.

### Setup the service, database and cache locally

    $ make setup_local

### Update database tables (manually)...do not use unless you know what you are doing

> To update local database tables, you need to set the `DATABASE_URL` environment variable. You can set it in the terminal or in the `.env` file.

    <!-- pragma: allowlist secret --> $ export DATABASE_URL=postgres://postgres:postgres@localhost:5432/fbr

> If you want to migrate all apps then navigate /find-business-regulations/fbr and use the following command:

    $ poetry run python manage.py migrate

> If you want to migrate a single app then navigate /find-business-regulations/fbr and use the following command:

    $ poetry run python manage.py migrate <app_name>
