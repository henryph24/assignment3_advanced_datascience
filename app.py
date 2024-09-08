from flask import Flask, render_template, request, redirect, url_for, flash
from markupsafe import escape  # Import escape function for security
from models import classify_job, preprocess_text  # Import custom model functions
import os

app = Flask(__name__)

# Set up directory paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current file
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')  # Path to data directory

# Define paths for data files
base_directory = DATA_DIR
preprocessed_file = os.path.join(DATA_DIR, 'preprocessed_jobs.txt')  # Path to preprocessed job data

def load_preprocessed_data(file_path):
    """
    Load and parse preprocessed job data from a file.
    
    Args:
        file_path (str): Path to the preprocessed data file.
    
    Returns:
        list: A list of dictionaries, each representing a job.
    """
    jobs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        job = {}
        for line in f:
            line = line.strip()
            if line.startswith('Category:'):
                # Start of a new job entry
                if job:
                    jobs.append(job)
                    job = {}
                job['category'] = line.split(':', 1)[1].strip()
            elif ':' in line:
                # Parse key-value pairs
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                job[key] = value
            elif line == '' and job:
                # End of a job entry
                jobs.append(job)
                job = {}
    if job:
        jobs.append(job)  # Add the last job if file doesn't end with a blank line
    return jobs

# Load job data on startup
jobs = load_preprocessed_data(preprocessed_file)

@app.route('/')
def index():
    """Render the home page with all job listings and categories."""
    categories = list(set(job['category'] for job in jobs))  # Get unique categories
    return render_template('index.html', jobs=jobs, categories=categories)

@app.route('/job/<int:job_id>')
def job_listing(job_id):
    """
    Render the page for a specific job listing.
    
    Args:
        job_id (int): The ID of the job to display.
    """
    job = next((job for job in jobs if int(job['webindex']) == job_id), None)
    if job is None:
        return "Job not found", 404
    return render_template('job_listing.html', job=job)

@app.route('/category/<category>')
def category_jobs(category):
    """
    Render the page with job listings for a specific category.
    
    Args:
        category (str): The category to filter jobs by.
    """
    category = escape(category)  # Sanitize input for security
    category_jobs = [job for job in jobs if job['category'] == category]
    categories = list(set(job['category'] for job in jobs))  # Get all categories for sidebar
    return render_template('index.html', jobs=category_jobs, category=category, categories=categories)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    """Handle job posting (both form display and submission)."""
    if request.method == 'POST':
        # Create a new job entry from form data
        new_job = {
            'title': request.form['title'],
            'company': request.form['company'],
            'webindex': str(len(jobs) + 1),
            'processed_description': preprocess_text(request.form['description'])
        }
        print(f"Processed description: {new_job['processed_description']}")

        # Classify the job based on the processed description
        suggested_category = classify_job(new_job['processed_description'])
        print(f"Classification result: {suggested_category}")

        # Handle classification errors
        if suggested_category.startswith("Unable to classify"):
            flash(f"Error: {suggested_category}")
            return render_template('post_job.html', categories=categories)

        # Use selected category if provided, otherwise use suggested category
        selected_category = request.form.get('category')
        new_job['category'] = selected_category if selected_category else suggested_category

        # Add the new job to the jobs list
        jobs.append(new_job)
        return redirect(url_for('job_listing', job_id=new_job['webindex']))

    # For GET requests, render the job posting form
    categories = list(set(job['category'] for job in jobs))
    return render_template('post_job.html', categories=categories)

@app.route('/classify', methods=['POST'])
def classify():
    """
    Classify a job description.
    
    This route is called via AJAX to get a suggested category for a job description.
    """
    description = request.form['description']
    processed_description = preprocess_text(description)
    category = classify_job(processed_description)
    return category

if __name__ == '__main__':
    # Print debug information
    print(f"Current working directory: {os.getcwd()}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Preprocessed file path: {preprocessed_file}")
    print("Files in data directory:")
    for file in os.listdir(DATA_DIR):
        print(f"  - {file}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)