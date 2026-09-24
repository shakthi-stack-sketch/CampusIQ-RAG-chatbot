import uuid
from typing import List, Dict, Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from backend.app.config import (
    VECTORSTORE_DIR,
    QDRANT_COLLECTION,
    QDRANT_URL,
    QDRANT_API_KEY,
    EMBEDDING_DIMENSION,
)


class QdrantVectorStore:
    """Manages 4096-dimensional Qdrant vector database for CampusIQ."""

    def __init__(self):
        self.collection_name = QDRANT_COLLECTION
        self.dimension = EMBEDDING_DIMENSION
        self.client = self._init_client()
        self._ensure_collection()

    def _init_client(self) -> QdrantClient:
        """Initialize Qdrant client (remote if configured, embedded local storage otherwise)."""
        if QDRANT_URL and QDRANT_URL.strip():
            return QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY or None,
                timeout=30.0,
            )
        else:
            VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)
            return QdrantClient(path=str(VECTORSTORE_DIR))

    def _ensure_collection(self):
        """
        Ensure the Qdrant collection exists with:
        - 4096-dimensional vectors
        - Cosine similarity
        - Payload indexes for metadata filtering
        """

        try:
            collections = self.client.get_collections().collections
            names = [c.name for c in collections]

            # ---------------------------------------------------------
            # 1. Create collection if it does not already exist
            # ---------------------------------------------------------
            if self.collection_name not in names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.dimension,
                        distance=Distance.COSINE,
                    ),
                )

                print(
                    f"[Qdrant] Created collection "
                    f"'{self.collection_name}' with {self.dimension} dimensions."
                )

            # ---------------------------------------------------------
            # 2. Create payload indexes used by CampusIQ filters
            # ---------------------------------------------------------
            #
            # These fields are used by:
            # - mess menu filtering
            # - category-based retrieval
            # - day-based retrieval
            # - source filtering
            # - scope filtering
            #
            # Qdrant Cloud requires indexes for reliable filtered queries.
            # ---------------------------------------------------------

            index_fields = [
                "category",
                "day",
                "meal",
                "source_type",
                "scope",
            ]

            for field_name in index_fields:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=models.PayloadSchemaType.KEYWORD,
                    )

                    print(
                        f"[Qdrant] Payload index ready: {field_name}"
                    )

                except Exception as index_error:
                    # The index may already exist.
                    # Do not stop the application because of this.
                    print(
                        f"[Qdrant] Payload index check for "
                        f"'{field_name}': {index_error}"
                    )

        except Exception as e:
            print(f"[Qdrant] Collection check error: {e}")

    def upsert_points(self, points: List[Dict[str, Any]]):
        """
        Upsert a batch of points into Qdrant.

        Each item in points:
        {
            'id': Optional[str],
            'vector': List[float],
            'payload': Dict[str, Any]
        }
        """

        if not points:
            return

        batch = []

        for p in points:
            point_id = p.get("id") or str(uuid.uuid4())

            batch.append(
                PointStruct(
                    id=point_id,
                    vector=p["vector"],
                    payload=p["payload"],
                )
            )

        # Batch upsert in chunks of 50
        chunk_size = 50

        for i in range(0, len(batch), chunk_size):
            chunk = batch[i : i + chunk_size]

            self.client.upsert(
                collection_name=self.collection_name,
                points=chunk,
            )

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        category: Optional[str] = None,
        source_type: Optional[str] = None,
        day: Optional[str] = None,
        meal: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform similarity search with optional metadata filters."""

        conditions = []

        if category:
            conditions.append(
                FieldCondition(
                    key="category",
                    match=MatchValue(value=category),
                )
            )

        if source_type:
            conditions.append(
                FieldCondition(
                    key="source_type",
                    match=MatchValue(value=source_type),
                )
            )

        if day:
            conditions.append(
                FieldCondition(
                    key="day",
                    match=MatchValue(value=day.lower()),
                )
            )

        if meal:
            conditions.append(
                FieldCondition(
                    key="meal",
                    match=MatchValue(value=meal.lower()),
                )
            )

        if scope:
            conditions.append(
                FieldCondition(
                    key="scope",
                    match=MatchValue(value=scope),
                )
            )

        query_filter = Filter(must=conditions) if conditions else None

        try:
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                query_filter=query_filter,
            )

            hits = []

            for res in response.points:
                hits.append(
                    {
                        "id": res.id,
                        "score": res.score,
                        "payload": res.payload,
                    }
                )

            return hits

        except Exception as e:
            print(f"[Qdrant] Search error: {e}")
            return []

    def get_by_filter(
        self,
        conditions_dict: Dict[str, Any],
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieve points strictly matching payload filters."""

        conditions = []

        for key, val in conditions_dict.items():
            if val is not None:
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=val),
                    )
                )

        query_filter = Filter(must=conditions) if conditions else None

        try:
            points, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )

            return [
                {
                    "id": p.id,
                    "payload": p.payload,
                    "score": 1.0,
                }
                for p in points
            ]

        except Exception as e:
            print(f"[Qdrant] Scroll filter error: {e}")
            return []

    def validate_mess_menu_indexing(self) -> Dict[str, Any]:
        """Validate that Qdrant contains indexed points for all 7 days."""

        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]

        validation_results = {}
        all_present = True

        for day in days:
            pts = self.get_by_filter(
                {
                    "category": "mess_menu",
                    "day": day,
                },
                limit=5,
            )

            count = len(pts)

            validation_results[day.capitalize()] = (
                "indexed" if count > 0 else "missing"
            )

            if count == 0:
                all_present = False

        return {
            "all_days_indexed": all_present,
            "days_validation": validation_results,
        }

    def get_collection_count(self) -> int:
        """Return total indexed vectors."""

        try:
            info = self.client.get_collection(
                self.collection_name
            )

            return info.points_count or 0

        except Exception:
            return 0

    def clear_collection(self):
        """Delete and recreate collection for fresh indexing."""

        try:
            self.client.delete_collection(
                self.collection_name
            )

            self._ensure_collection()

            print(
                f"[Qdrant] Cleared and recreated "
                f"'{self.collection_name}'."
            )

        except Exception as e:
            print(
                f"[Qdrant] Failed to clear collection: {e}"
            )


# Global vectorstore singleton
vectorstore_manager = QdrantVectorStore()