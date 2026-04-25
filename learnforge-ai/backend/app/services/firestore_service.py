"""Local JSON database service replacing Firestore for LearnForge AI."""

import json
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import structlog

logger = structlog.get_logger(__name__)

DB_PATH = Path("data/learnforge_db.json")

class LocalDBService:
    """Local JSON file-based CRUD operations matching Firestore API."""

    def __init__(self) -> None:
        self.db_path = DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.db_path.exists():
            return {"collections": {}, "users": {}, "top_level": {}}
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"collections": {}, "users": {}, "top_level": {}}

    def _save(self) -> None:
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    def _get_collection(self, collection: str) -> dict[str, Any]:
        if collection not in self._data["collections"]:
            self._data["collections"][collection] = {}
        return self._data["collections"][collection]

    # ── Generic helpers ────────────────────────────────────────────────────────

    def _now(self) -> datetime:
        return datetime.now(tz=timezone.utc)

    def set_document(self, collection: str, document_id: str, data: dict[str, Any], merge: bool = False) -> None:
        col = self._get_collection(collection)
        if merge and document_id in col:
            col[document_id].update(data)
        else:
            col[document_id] = data
        self._save()

    def get_document(self, collection: str, document_id: str) -> dict[str, Any] | None:
        col = self._get_collection(collection)
        if document_id in col:
            return {"id": document_id, **col[document_id]}
        return None

    def update_document(self, collection: str, document_id: str, data: dict[str, Any]) -> None:
        col = self._get_collection(collection)
        if document_id in col:
            col[document_id].update(data)
            self._save()

    def delete_document(self, collection: str, document_id: str) -> bool:
        col = self._get_collection(collection)
        if document_id in col:
            del col[document_id]
            self._save()
            return True
        return False

    def list_documents(
        self, collection: str, filters: list[tuple[str, str, Any]] | None = None,
        order_by: str | None = None, limit: int | None = None, descending: bool = True
    ) -> list[dict[str, Any]]:
        col = self._get_collection(collection)
        docs = [{"id": k, **v} for k, v in col.items()]

        if filters:
            for field, op, value in filters:
                if op == "==":
                    docs = [d for d in docs if d.get(field) == value]
                elif op == ">":
                    docs = [d for d in docs if d.get(field) is not None and d.get(field) > value]
                elif op == "<":
                    docs = [d for d in docs if d.get(field) is not None and d.get(field) < value]
                elif op == "in":
                    docs = [d for d in docs if d.get(field) in value]

        if order_by:
            docs.sort(key=lambda x: x.get(order_by, ""), reverse=descending)

        if limit:
            docs = docs[:limit]
        return docs

    # ── User-scoped sub-collection helpers ─────────────────────────────────────

    def _get_user_collection(self, user_id: str, collection: str) -> dict[str, Any]:
        if user_id not in self._data["users"]:
            self._data["users"][user_id] = {}
        if collection not in self._data["users"][user_id]:
            self._data["users"][user_id][collection] = {}
        return self._data["users"][user_id][collection]

    def set_user_doc(self, user_id: str, collection: str, document_id: str, data: dict[str, Any], merge: bool = False) -> None:
        col = self._get_user_collection(user_id, collection)
        if merge and document_id in col:
            col[document_id].update(data)
        else:
            col[document_id] = data
        self._save()

    def get_user_doc(self, user_id: str, collection: str, document_id: str) -> dict[str, Any] | None:
        col = self._get_user_collection(user_id, collection)
        if document_id in col:
            return {"id": document_id, **col[document_id]}
        return None

    def list_user_docs(self, user_id: str, collection: str, order_by: str | None = "created_at", descending: bool = True, limit: int | None = None) -> list[dict[str, Any]]:
        col = self._get_user_collection(user_id, collection)
        docs = [{"id": k, **v} for k, v in col.items()]
        if order_by:
            docs.sort(key=lambda x: x.get(order_by, ""), reverse=descending)
        if limit:
            docs = docs[:limit]
        return docs

    def delete_user_doc(self, user_id: str, collection: str, document_id: str) -> bool:
        col = self._get_user_collection(user_id, collection)
        if document_id in col:
            del col[document_id]
            self._save()
            return True
        return False

    def update_user_doc(self, user_id: str, collection: str, document_id: str, data: dict[str, Any]) -> None:
        col = self._get_user_collection(user_id, collection)
        if document_id in col:
            col[document_id].update(data)
            self._save()

    # ── Top-level collection helpers ───────────────────────────────────────────

    def _get_top_level_collection(self, top_collection: str, user_id: str) -> dict[str, Any]:
        if top_collection not in self._data["top_level"]:
            self._data["top_level"][top_collection] = {}
        if user_id not in self._data["top_level"][top_collection]:
            self._data["top_level"][top_collection][user_id] = {"items": {}}
        return self._data["top_level"][top_collection][user_id]["items"]

    def set_top_level_user_doc(self, top_collection: str, user_id: str, document_id: str, data: dict[str, Any], merge: bool = False) -> None:
        col = self._get_top_level_collection(top_collection, user_id)
        if merge and document_id in col:
            col[document_id].update(data)
        else:
            col[document_id] = data
        self._save()

    def list_top_level_user_docs(self, top_collection: str, user_id: str, order_by: str | None = "created_at", descending: bool = True, limit: int | None = None) -> list[dict[str, Any]]:
        col = self._get_top_level_collection(top_collection, user_id)
        docs = [{"id": k, **v} for k, v in col.items()]
        if order_by:
            docs.sort(key=lambda x: x.get(order_by, ""), reverse=descending)
        if limit:
            docs = docs[:limit]
        return docs

    def get_top_level_user_doc(self, top_collection: str, user_id: str, document_id: str) -> dict[str, Any] | None:
        col = self._get_top_level_collection(top_collection, user_id)
        if document_id in col:
            return {"id": document_id, **col[document_id]}
        return None

    def delete_top_level_user_doc(self, top_collection: str, user_id: str, document_id: str) -> bool:
        col = self._get_top_level_collection(top_collection, user_id)
        if document_id in col:
            del col[document_id]
            self._save()
            return True
        return False

    def update_top_level_user_doc(self, top_collection: str, user_id: str, document_id: str, data: dict[str, Any]) -> None:
        col = self._get_top_level_collection(top_collection, user_id)
        if document_id in col:
            col[document_id].update(data)
            self._save()

# Keep the same singleton instance name so imports don't break
firestore_service = LocalDBService()
