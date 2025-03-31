#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fbr.settings")

    is_local_ide_test_server = (
        os.getenv("DJANGO_LOCAL_IDE_TEST_SERVER", "false").lower() == "true"
    )

    args = []

    try:
        from django.core.management import execute_from_command_line

        # If environment variable is set named
        # DJANGO_LOCAL_IDE_TEST_SERVER, use that instead,

        if is_local_ide_test_server:
            # Automatically append runserver_plus args if no
            # command is provided
            extra_args = os.getenv("RUNSERVER_CMD", "").split()
            args = (
                ["runserver_plus"] + extra_args
                if extra_args
                else ["runserver"]
            )

    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if is_local_ide_test_server:
        print(f"Running with args: {args}")
        execute_from_command_line(args)
    else:
        print("Running with default args")
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
