# flake8: noqa

import time

from celery import shared_task

from app.cache.legislation import Legislation
from app.cache.public_gateway import PublicGateway
from app.search.config import SearchDocumentConfig
from app.search.utils.documents import clear_all_documents


@shared_task(name="celery_worker.tasks.rebuild_cache")
def rebuild_cache():
    """
    Rebuilds the cache for search documents across various components by
    clearing all existing documents. The process is timed, and the
    duration is included in the success response. If an exception occurs,
    an error message is returned.

    Returns:
        dict: A dictionary containing either a success message with the
        duration of the cache rebuilding process or an error message
        detailing the exception that was raised.
    """
    try:
        start = time.time()
        clear_all_documents()
        config = SearchDocumentConfig(search_query="", timeout=2)
        PublicGateway().build_cache(config)
        Legislation().build_cache(config)
        end = time.time()
        print(
            {
                "message": "rebuilt cache",
                "duration": round(end - start, 2),
            }
        )
    except Exception as e:
        message = {"message": f"error building cache data: {e}"}
        print(message)
