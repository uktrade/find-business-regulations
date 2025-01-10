# Cache rebuild

## Introduction
There are a few ways to rebuild the cache. The cache is a collection of data from legislation and data workspace.
The cache data is stored in a postgres database that is used to store the data that is used to build the search index.

This document outlies the steps to rebuild the cache using three different methods.

## Rebuild the cache locally using the `make` command
The `make setup_local_force_rebuild` command is a simple way to rebuild the cache locally including the entire service.
The `make` command is a build automation tool that automatically builds executable programs and libraries from source
code by reading files called `Makefiles` which specify how to derive the target program.

However, to rebuild the cache onlly, you can use the `make rebuild_cache` command.

## Rebuild the cache on environment using the automated celery task
The cache can be rebuilt on the environment using the automated celery task.
The task is scheduled to run every 24 hours as a cron job. The task is defined in the `tasks.py` file in the
`celery_worker` directory. However, the actual task is defined in the `celery_app.py` file in the `fbr` directory.

At present is set to run at 10:00 PM every day. To edit the time then change the following code:
```python
celery_app.conf.beat_schedule = {
    "schedule-fbr-cache-task": {
        "task": "celery_worker.tasks.rebuild_cache",
        "schedule": crontab(hour="22", minute="00"),  # Runs daily at 10:00 PM
    },
}
```

## Rebuild the cache on environment using the django management command
The cache can be rebuilt on the environment using the django management command.
The command is defined in the `management/commands` directory in the `fbr` directory.

To run the command, use the following command:
```bash
$ poetry run python manage.py rebuild_cache
```

## Conclusion
The cache is a collection of data from legislation and data workspace. The cache data is stored in a postgres database
that is used to store the data that is used to build the search index. The cache can be rebuilt using the `make`
command, the automated celery task, or the django management command. The automated celery task is scheduled to run
every 24 hours as a cron job. The cache can be rebuilt on the environment using the automated celery task or the django
management command. The cache is an important part of the application and should be rebuilt regularly to ensure that the
data is up to date.
