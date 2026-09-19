import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

# Ensure project root is in python path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def run_sync() -> dict:
    """Attempt API sync first (if uvicorn server is running), fallback to local module sync."""
    api_url = "http://127.0.0.1:8000/api/knowledge/sync"
    try:
        req = urllib.request.Request(api_url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, ConnectionRefusedError, OSError):
        # Server is not running; sync directly using internal modules
        from backend.app.api.knowledge import sync_knowledge_base
        return sync_knowledge_base()

if __name__ == "__main__":
    print("==================================================")
    print("  CAMPUSIQ — KNOWLEDGE BASE INDEXER")
    print("  Prathyusha Engineering College (PEC)")
    print("==================================================")
    print("Building Qdrant vector database (4096 dimensions)...\n")

    result = run_sync()

    if result.get("success"):
        print("\n[SUCCESS] Knowledge base built successfully!")
        print(f"Raw items processed: {result.get('raw_items_processed')}")
        print(f"Knowledge chunks indexed: {result.get('chunks_indexed')}")
        print(f"Total points in Qdrant: {result.get('total_vectors')}")
        print("Collection: campusiq_college_knowledge")
        print("Vector dimension: 4096")

        validation = result.get("mess_menu_validation", {})
        print("\nMess Menu Validation:")
        for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            status = validation.get(day, "missing")
            print(f"{day}: {status}")
    else:
        print(f"\n[ERROR] Ingestion failed: {result.get('message')}")
        validation = result.get("mess_menu_validation", {})
        if validation:
            print("\nMess Menu Validation:")
            for day, status in validation.items():
                print(f"{day}: {status}")