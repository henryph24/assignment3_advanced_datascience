import os
import traceback
from joblib import load
from .preprocessing import preprocess_text
from .embeddings import get_document_embedding

# Set the base directory relative to this file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')  # Add this line

def find_model_file(directories):
    for directory in directories:
        for file in os.listdir(directory):
            if file.startswith('best_model_CatBoostClassifier') and file.endswith('.joblib'):
                return os.path.join(directory, file)
    raise FileNotFoundError(f"No CatBoostClassifier model file found in {directories}")

try:
    model_path = find_model_file([DATA_DIR, MODELS_DIR, BASE_DIR])  # Search in multiple directories
    label_encoder_path = os.path.join(MODELS_DIR, 'label_encoder.joblib')  # Update this line

    print(f"Attempting to load model from: {model_path}")
    print(f"Attempting to load label encoder from: {label_encoder_path}")

    # Load the saved model and label encoder
    model = load(model_path)
    label_encoder = load(label_encoder_path)

    print("Model and label encoder loaded successfully")
except Exception as e:
    print(f"Error loading model or label encoder: {str(e)}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Models directory: {MODELS_DIR}")
    print("Files in data directory:")
    for file in os.listdir(DATA_DIR):
        print(f"  - {file}")
    print("Files in models directory:")
    for file in os.listdir(MODELS_DIR):
        print(f"  - {file}")
    print("Files in base directory:")
    for file in os.listdir(BASE_DIR):
        print(f"  - {file}")
    print(traceback.format_exc())
    model = None
    label_encoder = None

def classify_job(job_description):
    try:
        if model is None or label_encoder is None:
            return "Unable to classify due to missing model or label encoder"
        
        preprocessed_text = preprocess_text(job_description)
        embedding = get_document_embedding(preprocessed_text)
        prediction = model.predict([embedding])[0]
        return label_encoder.inverse_transform([prediction])[0]
    except Exception as e:
        error_msg = f"Error in classify_job: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"Unable to classify: {str(e)}"