import os
import traceback
from joblib import load
from .preprocessing import preprocess_text
from .embeddings import get_document_embedding

# Set up directory paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def find_model_file(directories):
    """Find the model file in the given directories."""
    for directory in directories:
        model_path = os.path.join(directory, 'models/best_model_CatBoostClassifier_Description_Only_-_Count_Vectors.joblib')
        if os.path.exists(model_path):
            return model_path
    raise FileNotFoundError(f"Model file not found in {directories}")

try:
    # Load the model and label encoder
    model_path = find_model_file([DATA_DIR, MODELS_DIR, BASE_DIR])
    label_encoder_path = os.path.join(MODELS_DIR, 'label_encoder.joblib')

    model = load(model_path)
    label_encoder = load(label_encoder_path)

    print("Model and label encoder loaded successfully")
except Exception as e:
    print(f"Error loading model or label encoder: {str(e)}")
    print(traceback.format_exc())
    model = None
    label_encoder = None

def classify_job(job_description):
    """
    Classify a job based on its description.
    
    Args:
        job_description (str): The job description to classify.
    
    Returns:
        str: The predicted job category or an error message.
    """
    try:
        if model is None or label_encoder is None:
            return "Unable to classify due to missing model or label encoder"
        
        preprocessed_text = preprocess_text(job_description)
        embedding = get_document_embedding(preprocessed_text)
        # Reshape the embedding to ensure it's a 2D array
        embedding = embedding.reshape(1, -1)
        prediction = model.predict(embedding).ravel()[0]  # Use ravel() to flatten the array
        return label_encoder.inverse_transform([prediction])[0]
    except Exception as e:
        error_msg = f"Error in classify_job: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"Unable to classify: {str(e)}"

