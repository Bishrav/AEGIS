# AEGIS RAG foundation

This package provides deterministic document chunking, citation-preserving evidence IDs, and a local hybrid retriever. `HashingEmbedder` is intentionally an offline test substitute; the retrieval interface can later be backed by pgvector and a production embedding model without changing evidence contracts.
