import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

_REBUILD_INTERVAL = 300  # 5 min — same as pricing cache TTL


class RAGPriceService:
    """BM25-based retrieval over PriceHistory for price estimation.

    Builds a per-device-type BM25 index from completed repairs with final_price set.
    Rebuilds automatically every 5 minutes. Returns None gracefully when < 3 records
    exist or langchain-community is not installed.
    """

    # device_type -> (BM25Retriever, built_at_timestamp)
    _cache: dict = {}

    @classmethod
    def _build(cls, device_type: str):
        try:
            from langchain_community.retrievers import BM25Retriever
            from langchain_core.documents import Document
        except ImportError:
            logger.warning("RAG: langchain-community not installed — skipping RAG layer")
            return None

        try:
            from back.models.repair_requests_models import PriceHistory

            records = list(
                PriceHistory.objects.filter(
                    final_price__isnull=False,
                    device_type=device_type,
                ).values("problem_description", "final_price")
            )
        except Exception as exc:
            logger.warning("RAG: DB query failed: %s", exc)
            return None

        if len(records) < 3:
            logger.debug("RAG: not enough records for %s (%d)", device_type, len(records))
            return None

        docs = [
            Document(
                page_content=r["problem_description"],
                metadata={"final_price": float(r["final_price"])},
            )
            for r in records
        ]

        retriever = BM25Retriever.from_documents(docs, k=min(5, len(docs)))
        logger.info("RAG: built index for %s (%d records)", device_type, len(docs))
        return retriever

    @classmethod
    def _get_retriever(cls, device_type: str):
        now = time.monotonic()
        entry = cls._cache.get(device_type)
        if entry is not None:
            retriever, built_at = entry
            if now - built_at < _REBUILD_INTERVAL:
                return retriever

        retriever = cls._build(device_type)
        cls._cache[device_type] = (retriever, now)
        return retriever

    @classmethod
    def estimate(cls, device_type: str, description: str) -> Optional[dict]:
        retriever = cls._get_retriever(device_type)
        if retriever is None:
            return None

        try:
            similar = retriever.invoke(description)
        except Exception as exc:
            logger.warning("RAG: retrieval failed: %s", exc)
            return None

        if not similar:
            return None

        prices = [doc.metadata["final_price"] for doc in similar]
        avg_price = sum(prices) / len(prices)
        # Confidence scales with number of retrieved cases: 3 cases → 0.45, 5 → 0.55
        confidence = min(0.35 + len(prices) * 0.04, 0.60)

        return {
            "predicted_price": round(avg_price, -2),
            "confidence": round(confidence, 2),
            "source": "rag",
            "similar_cases_count": len(prices),
        }

    @classmethod
    def invalidate(cls, device_type: str | None = None) -> None:
        if device_type:
            cls._cache.pop(device_type, None)
        else:
            cls._cache.clear()
