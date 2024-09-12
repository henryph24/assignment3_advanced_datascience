import os
import re
from nltk.tokenize import word_tokenize

# Set up directory paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')
stopwords_path = os.path.join(DATA_DIR, 'stopwords_en.txt')

def load_stopwords(file_path):
    """Load stopwords from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return set(word.strip().lower() for word in file)

# Load stopwords
stop_words = load_stopwords(stopwords_path)

def preprocess_text(text):
    """
    Preprocess the input text by tokenizing, removing short words,
    and filtering out stopwords.
    """
    # Tokenize using the specified regex
    tokens = re.findall(r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?", text.lower())
    # Remove words with length less than 2
    tokens = [token for token in tokens if len(token) >= 2]
    # Remove stopwords
    tokens = [token for token in tokens if token not in stop_words]
    return ' '.join(tokens)