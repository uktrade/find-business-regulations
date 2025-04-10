# flake8: noqa

import time

from celery import shared_task

from app.cache.public_gateway import PublicGateway
from app.search.config import SearchDocumentConfig
from app.search.utils.documents import clear_all_documents


@shared_task(name="celery_worker.tasks.rebuild_cache")
def rebuild_cache():
    try:
        start = time.time()
        clear_all_documents()
        config = SearchDocumentConfig(search_query="", timeout=120)
        config.print_to_log("celery task")

        public_gateway_start = time.time()
        PublicGateway().build_cache(config)
        public_gateway_end = time.time()
        public_gateway_total = public_gateway_end - public_gateway_start

        end = time.time()
        print(
            {
                "message": "rebuilt cache",
                "total duration": round(end - start, 2),
                "details": {
                    "legislation": round(legislation_total, 2),
                    "public_gateway": round(public_gateway_total, 2),
                },
            }
        )
    except Exception as e:
        print({"message": f"cache rebuild failed: {e}"})
