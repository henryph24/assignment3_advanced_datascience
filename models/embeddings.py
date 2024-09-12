import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

# Set up directory paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')

vocab_path = os.path.join(DATA_DIR, 'vocab.txt')

def load_vocabulary(file_path):
    """Load vocabulary from a file."""
    vocab = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            word, index = line.strip().split(':')
            vocab[word] = int(index)
    return vocab

# Load vocabulary
vocabulary = load_vocabulary(vocab_path)

# Initialize vectorizer with the loaded vocabulary
count_vectorizer = CountVectorizer(vocabulary=vocabulary)

def get_document_embedding(text):
    """
    Get the document embedding using count vectorization.
    This method has competitive performance with TF-IDF and outperforms other embedding methods.
    """
    count_vector = count_vectorizer.transform([text])
    # Convert sparse matrix to dense array
    return count_vector.toarray()[0]


