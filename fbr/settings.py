"""Django base settings for Find business regulations project.

Environment:
We use django-environ but do not read a `.env` file. Locally we provide
docker-compose an environment from `local.env` file in the project root,
using `env_file` field in `docker-compose.yml`. There is a `local.env.example`
in this repo. When deployed, the service retrieves these values from the
environment.

NB: Some settings acquired using `env()` deliberately *do not* have defaults
as we want to get an `ImproperlyConfigured` exception. This highlights badly
configured deployments.
"""

import os

from pathlib import Path
from typing import Any

import dj_database_url
import environ

from django_log_formatter_asim import ASIMFormatter

# Define the root directory (i.e. <repo-root>)
root = environ.Path(__file__) - 4  # i.e. Repository root
SITE_ROOT = Path(root())

# Define the project base directory (i.e. <repo-root>/fbr)
BASE_DIR = Path(__file__).resolve().parent.parent


# Get environment variables
env = environ.Env(
    DEBUG=(bool, False),
)

# Must be provided by the environment
SECRET_KEY = env(
    "DJANGO_SECRET_KEY", default="find-business-regulations-secret-key"
)

DEBUG = env("DEBUG", default=False)
DJANGO_ADMIN = env("DJANGO_ADMIN", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost"])
ENVIRONMENT = env(
    "COPILOT_ENVIRONMENT_NAME", default="local"
)  # TODO: Change to APP_ENV, updates required in deploy repo

# Application definition
DJANGO_APPS = [
    "django_celery_beat",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "app",
    "app.core",
    "app.search",
    "app.cache.apps.CacheConfig",
    "celery_worker",
]

THIRD_PARTY_APPS: list = [
    "webpack_loader",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ROOT_URLCONF = "fbr.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "app", "search", "templates"),
            os.path.join(BASE_DIR, "app", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "fbr.context_processors.google_tag_manager",
            ],
        },
    },
]

WSGI_APPLICATION = "fbr.wsgi.application"

DATABASES: dict = {}
if DATABASE_URL := env("DATABASE_URL", default=None):
    DATABASES = {
        "default": {
            **dj_database_url.parse(
                DATABASE_URL,
                engine="postgresql",
            ),
            "ENGINE": "django.db.backends.postgresql",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]

REDIS_ENDPOINT = env("REDIS_ENDPOINT", default="")

# Celery
CELERY_BROKER_URL = env("REDIS_ENDPOINT", default="")
if CELERY_BROKER_URL and CELERY_BROKER_URL.startswith("rediss://"):
    CELERY_BROKER_URL = f"{CELERY_BROKER_URL}?ssl_cert_reqs=CERT_REQUIRED"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
CELERY_RESULT_EXTENDED = True
CELERY_TASK_TIME_LIMIT = (
    900  # Maximum runtime for a task in seconds (e.g., 900/60 = 15 minutes)
)
CELERY_TASK_SOFT_TIME_LIMIT = (
    270  # Optional: Grace period before forced termination
)
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
USE_DEPRECATED_PYTZ = True

# Internationalisation
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# Static files
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "static/"

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Webpack

STATICFILES_DIRS = [
    BASE_DIR / "front_end/",
]

WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        "BUNDLE_DIR_NAME": "webpack_bundles/",  # must end with slash
        "STATS_FILE": os.path.join(BASE_DIR, "webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}


# TODO: Use redis for cache?
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": f"redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         },
#     }
# }

# Logging
LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "asim_formatter": {
            "()": ASIMFormatter,
        },
        "simple": {
            "style": "{",
            "format": "{asctime} {levelname} {message}",
        },
    },
    "handlers": {
        "asim": {
            "class": "logging.StreamHandler",
            "formatter": "asim_formatter",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Django Log Formatter ASIM settings
# See https://github.com/uktrade/django-log-formatter-asim#settings
DLFA_TRACE_HEADERS = ("X-B3-TraceId", "X-B3-SpanId")

# Set the correct handlers when running in DBT Platform
# console handler set as default as it's easier to read
LOGGING["root"]["handlers"] = ["asim"]
LOGGING["loggers"]["django"]["handlers"] = ["asim"]

# ------------------------------------------------------------------------------
# The Find business regulations zone - specific service settings.
# ------------------------------------------------------------------------------

# Service

SERVICE_NAME: str = "Find business regulations"
SERVICE_NAME_SEARCH: str = "Find business regulations"
CONTACT_EMAIL: str = "findbusinessregulations@businessandtrade.gov.uk"

# Cookies
ANALYTICS_CONSENT_NAME: str = "analytics_consent"

# DBT Data API
# DBT_DATA_API_URL = env(
#     "DBT_DATA_API_URL",
#     default="https://data.api.trade.gov.uk/v1/datasets/market-barriers/versions/v1.0.10/data?format=json",  # noqa: E501
# )

# HOSTNAME
HOSTNAME_MAP = {
    "local": "http://localhost:8081",
    "dev": "https://dev.find-business-regulations.uktrade.digital/",
    "staging": "https://staging.find-business-regulations.uktrade.digital/",
    "prod": "https://find-business-regulations.uktrade.digital/",
}

HOSTNAME = HOSTNAME_MAP.get(ENVIRONMENT.lower(), HOSTNAME_MAP["prod"])

# Google Analytics (GA)
# Note: please consult the performance team before changing these settings
COOKIE_PREFERENCES_SET_NAME: str = "cookie_preferences_set"
COOKIE_ACCEPTED_GA_NAME: str = "accepted_ga_cookies"
GOOGLE_ANALYTICS_TAG_MANAGER_ID = env(
    "GOOGLE_ANALYTICS_TAG_MANAGER_ID", default=None
)
