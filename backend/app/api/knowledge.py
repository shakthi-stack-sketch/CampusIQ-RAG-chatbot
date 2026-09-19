from fastapi import APIRouter
from backend.app.config import OFFICIAL_SOURCES, DOCUMENTS_DIR, SOCIAL_MEDIA_DIR
from backend.app.rag.vectorstore import vectorstore_manager
from backend.app.ingestion.doc_parser import parse_all_documents
from backend.app.ingestion.social_loader import load_official_social_media
from backend.app.ingestion.chunker import process_and_chunk_all
from backend.app.rag.embeddings import embedding_service

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Ingestion"])

@router.get("/status")
def get_knowledge_status():
    """Return status of knowledge base, document counts, verified sources, and mess menu validation."""
    vector_count = vectorstore_manager.get_collection_count()
    doc_files = [f.name for f in DOCUMENTS_DIR.iterdir() if f.is_file()] if DOCUMENTS_DIR.exists() else []
    validation = vectorstore_manager.validate_mess_menu_indexing()

    return {
        "status": "operational",
        "collection": vectorstore_manager.collection_name,
        "embedding_dimension": vectorstore_manager.dimension,
        "embedding_model": embedding_service.model_name,
        "total_vectors_indexed": vector_count,
        "documents_available": doc_files,
        "official_sources": OFFICIAL_SOURCES,
        "mess_menu_validation": validation["days_validation"],
        "all_days_indexed": validation["all_days_indexed"]
    }

@router.post("/sync")
def sync_knowledge_base():
    """Re-index all official college documents and verified social media into Qdrant with index validation."""
    raw_docs = parse_all_documents()
    raw_social = load_official_social_media()
    all_raw = raw_docs + raw_social

    chunks = process_and_chunk_all(all_raw)
    if not chunks:
        return {"success": False, "message": "No documents or social content found to index."}

    # Generate 4096-dimensional vectors
    texts = [c["content"] for c in chunks]
    vectors = embedding_service.embed_documents(texts)

    points = []
    for idx, chunk in enumerate(chunks):
        payload = dict(chunk["metadata"])
        payload["content"] = chunk["content"]
        points.append({
            "vector": vectors[idx],
            "payload": payload
        })

    # Clear old collection and upsert fresh points
    vectorstore_manager.clear_collection()
    vectorstore_manager.upsert_points(points)

    # Actual index validation derived from indexed Qdrant data
    validation = vectorstore_manager.validate_mess_menu_indexing()
    total_vectors = vectorstore_manager.get_collection_count()

    if not validation["all_days_indexed"]:
        return {
            "success": False,
            "message": "Index validation failed: One or more days are missing from Qdrant.",
            "raw_items_processed": len(all_raw),
            "chunks_indexed": len(points),
            "total_vectors": total_vectors,
            "mess_menu_validation": validation["days_validation"]
        }

    return {
        "success": True,
        "raw_items_processed": len(all_raw),
        "chunks_indexed": len(points),
        "total_vectors": total_vectors,
        "mess_menu_validation": validation["days_validation"],
        "all_days_indexed": True
    }
