import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')

# count_vectors_path = os.path.join(DATA_DIR, 'count_vectors.txt')
vocab_path = os.path.join(DATA_DIR, 'vocab.txt')

# Load vocabulary
def load_vocabulary(file_path):
    vocab = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            word, index = line.strip().split(':')
            vocab[word] = int(index)
    return vocab

vocabulary = load_vocabulary(vocab_path)

# Initialize vectorizer
count_vectorizer = CountVectorizer(vocabulary=vocabulary)

def get_document_embedding(text):
    # Use count vectorizer
    count_vector = count_vectorizer.transform([text])
    # Convert sparse matrix to dense array
    return count_vector.toarray()[0]