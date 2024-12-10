# flake8: noqa
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fbr.settings")

# Initialize Django setup
django.setup()

import time

from app.cache.legislation import Legislation
from app.cache.public_gateway import PublicGateway
from app.search.config import SearchDocumentConfig
from app.search.utils.documents import clear_all_documents


def rebuild_cache():
    try:
        start = time.time()
        clear_all_documents()
        config = SearchDocumentConfig(search_query="", timeout=1)
        Legislation().build_cache(config)
        PublicGateway().build_cache(config)
        end = time.time()
        return {"message": "rebuilt cache", "duration": round(end - start, 2)}
    except Exception as e:
        return {"message": f"error clearing documents: {e}"}
