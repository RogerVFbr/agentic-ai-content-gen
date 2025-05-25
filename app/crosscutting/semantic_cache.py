import os
import pickle
from datetime import datetime, timedelta, timezone
from typing import List, Any

from sentence_transformers import SentenceTransformer
import faiss

from dataclasses import dataclass
from datetime import datetime
import numpy as np

@dataclass
class CacheEntry:
    query: str
    result: Any
    embedding: np.ndarray
    timestamp: datetime


class SemanticCache:
    def __init__(self, cache_file: str, threshold=0.85, ttl_minutes=60):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache_file = cache_file
        self.threshold = threshold
        self.ttl = timedelta(minutes=ttl_minutes)
        self.index = faiss.IndexFlatIP(384)
        self.entries: List[CacheEntry] = []

        if os.path.exists(cache_file):
            self._load()

    def _embed(self, text: str) -> np.ndarray:
        vec = self.model.encode([text])[0]
        return vec.astype("float32")

    def _is_expired(self, timestamp: datetime) -> bool:
        return datetime.now(timezone.utc) - timestamp > self.ttl

    def _prune(self):
        """Remove expired entries."""
        now = datetime.now(timezone.utc)
        self.entries = [e for e in self.entries if now - e.timestamp <= self.ttl]
        self._rebuild_index()

    def _rebuild_index(self):
        self.index = faiss.IndexFlatIP(384)
        if self.entries:
            embeddings = np.stack([e.embedding for e in self.entries]).astype("float32")
            self.index.add(embeddings)

    def search(self, query: str):
        self._prune()
        if not self.entries:
            return None

        query_vec = self._embed(query).reshape(1, -1)
        scores, indices = self.index.search(query_vec, 1)

        score = scores[0][0]
        match_idx = indices[0][0]

        if score >= self.threshold:
            entry = self.entries[match_idx]
            return {
                "match_query": entry.query,
                "result": entry.result,
                "score": float(score),
                "timestamp": entry.timestamp.isoformat()
            }

        return None

    def store(self, query: str, result):
        embedding = self._embed(query)
        entry = CacheEntry(
            query=query,
            result=result,
            embedding=embedding,
            timestamp=datetime.now(timezone.utc)
        )
        self.entries.append(entry)
        self.index.add(np.array([embedding]))

    def save(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.entries, f)

    def _load(self):
        if os.path.getsize(self.cache_file) == 0:
            self.entries = []
            return

        with open(self.cache_file, "rb") as f:
            self.entries = pickle.load(f)
            # Compatibility: convert old dicts to CacheEntry if needed
            for i, entry in enumerate(self.entries):
                if isinstance(entry, dict):
                    self.entries[i] = CacheEntry(**entry)
            self._rebuild_index()


if __name__ == "__main__":
    cache = SemanticCache(cache_file="../infrastructure/test_cache.json", threshold=0.85)
    cache.store("Who is the CEO of OpenAI?", "Sam Altman is the CEO of OpenAI.")
    cache.store("Capital of France", "The capital of France is Paris.")
    queries = [
        "Who runs OpenAI?",
        "What's France's capital?",
        "Tell me the leader of OpenAI",
        "Where's the HQ of OpenAI?"
    ]

    for q in queries:
        hit = cache.search(q)
        if hit:
            result = hit["result"]
            original_query = hit["match_query"]
            score = hit["score"]
            print(f"\n✅ Cache HIT for: \"{q}\"")
            print(f"  ↳ Matched: \"{original_query}\" (Score: {score:.2f})")
            print(f"  ↳ Result: {result}")
        else:
            print(f"\n❌ Cache MISS for: \"{q}\"")
            print("→ Would call web search and store result.")
            # Simulate web result
            fake_result = f"Simulated result for: {q}"
            cache.store(q, fake_result)

    cache.save()