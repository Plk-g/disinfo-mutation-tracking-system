"""
Embedding generation using Sentence-BERT models.
This module provides functions to generate embeddings for text using pre-trained models.
"""

from typing import List, Union
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    _SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    _SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")


def generate_embeddings_batch(texts: List[str], model_name: str = 'all-MiniLM-L6-v2') -> np.ndarray:
    """
    Generate embeddings for a batch of texts using Sentence-BERT.
    
    Args:
        texts: List of text strings to embed
        model_name: Name of the Sentence-BERT model to use
        
    Returns:
        numpy array of shape (n_texts, embedding_dim)
    """
    if not _SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError("sentence-transformers is required. Install with: pip install sentence-transformers")
    
    if not texts:
        return np.array([])
    
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings


def generate_embedding_single(text: str, model_name: str = 'all-MiniLM-L6-v2') -> np.ndarray:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text string to embed
        model_name: Name of the Sentence-BERT model to use
        
    Returns:
        numpy array of shape (embedding_dim,)
    """
    return generate_embeddings_batch([text], model_name)[0]

