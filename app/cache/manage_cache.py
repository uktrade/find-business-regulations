# flake8: noqa
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fbr.settings")

# Initialize Django setup
django.setup()

import time

from app.cache.public_gateway import PublicGateway
from app.search.config import SearchDocumentConfig
from app.search.utils.documents import clear_all_documents


def rebuild_cache():
    try:
        start = time.time()
        clear_all_documents()
        config = SearchDocumentConfig(search_query="", timeout=120)
        config.print_to_log("non-celery task")

        public_gateway_start = time.time()
        PublicGateway().build_cache(config)
        public_gateway_end = time.time()
        public_gateway_total = public_gateway_end - public_gateway_start

        end = time.time()
        return {
            "message": "rebuilt cache",
            "total duration": round(end - start, 2),
            "details": {
                "public_gateway": round(public_gateway_total, 2),
            },
        }
    except Exception as e:
        return {"message": f"cache rebuild failed: {e}"}
