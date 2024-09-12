from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from markupsafe import escape
from models import classify_job, preprocess_text
import os
import json

app = Flask(__name__)

# Set up directory paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'assess3_data', 'assess3_data')

# Define paths for data files
preprocessed_file = os.path.join(DATA_DIR, 'preprocessed_jobs.txt')
saved_jobs_file = os.path.join(DATA_DIR, 'saved_jobs.json')

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
        description = []
        for line in f:
            line = line.strip()
            if line.startswith('Category:'):
                if job:
                    if description:
                        job['description'] = ' '.join(description)
                    jobs.append(job)
                    job = {}
                    description = []
                job['category'] = line.split(':', 1)[1].strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                job[key] = value
            elif line:
                description.append(line)
            elif not line and job:
                if description:
                    job['description'] = ' '.join(description)
                jobs.append(job)
                job = {}
                description = []
    if job:
        if description:
            job['description'] = ' '.join(description)
        jobs.append(job)
    return jobs

def save_jobs_to_file(jobs, file_path):
    """Save the jobs list to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

def load_jobs_from_file(file_path):
    """Load jobs from a JSON file."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Load job data on startup
jobs = load_preprocessed_data(preprocessed_file)
saved_jobs = load_jobs_from_file(saved_jobs_file)
jobs.extend(saved_jobs)  # Combine preprocessed and saved jobs

@app.route('/')
def index():
    """Render the home page with all job listings and categories."""
    categories = list(set(job['category'] for job in jobs))
    return render_template('index.html', jobs=jobs, categories=categories)

@app.route('/job/<int:job_id>')
def job_listing(job_id):
    """Render the page for a specific job listing."""
    job = next((job for job in jobs if int(job.get('webindex', 0)) == job_id), None)
    if job is None:
        return "Job not found", 404

    # Ensure all required fields are present with default values
    default_fields = {
        'title': 'No Title',
        'company': 'No Company',
        'category': 'Uncategorized',
        'description': 'No description available.'
    }

    # Use the actual job data, falling back to defaults if necessary
    job_data = {
        'title': job.get('title', default_fields['title']),
        'company': job.get('company', default_fields['company']),
        'category': job.get('category', default_fields['category']),
        'description': job.get('description') or job.get('processed_description', default_fields['description'])
    }

    return render_template('job_listing.html', job=job_data)

@app.route('/category/<category>')
def category_jobs(category):
    """Render the page with job listings for a specific category."""
    category = escape(category)
    category_jobs = [job for job in jobs if job['category'] == category]
    categories = list(set(job['category'] for job in jobs))
    return render_template('index.html', jobs=category_jobs, category=category, categories=categories)

@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    """Handle job posting (both form display and submission)."""
    if request.method == 'POST':
        new_job = {
            'title': request.form['title'],
            'company': request.form['company'],
            'webindex': str(len(jobs) + 1),
            'description': request.form['description'],
            'processed_description': preprocess_text(request.form['description'])
        }

        suggested_category = classify_job(new_job['processed_description'])
        if suggested_category.startswith("Unable to classify"):
            flash(f"Error: {suggested_category}", 'error')
            categories = list(set(job['category'] for job in jobs))
            return render_template('post_job.html', categories=categories, job=new_job)

        new_job['category'] = request.form.get('category', suggested_category)

        jobs.append(new_job)
        save_jobs_to_file(saved_jobs + [new_job], saved_jobs_file)
    
        return redirect(url_for('job_listing', job_id=int(new_job['webindex'])))

    categories = list(set(job['category'] for job in jobs))
    return render_template('post_job.html', categories=categories)

@app.route('/classify', methods=['POST'])
def classify():
    description = request.form['description']
    processed_description = preprocess_text(description)
    category = classify_job(processed_description)
    print(f"Classification result: {category}")  # Add this line for debugging
    if category.startswith("Unable to classify"):
        return jsonify({"error": category}), 400
    return jsonify({"category": category})

@app.route('/search')
def search():
    """Handle job search functionality."""
    query = request.args.get('q', '').lower()
    search_results = [
        job for job in jobs
        if query in job.get('title', '').lower()
        or query in job.get('company', '').lower()
        or query in job.get('description', '').lower()
        or query in job.get('category', '').lower()
    ]
    return render_template('search_results.html', jobs=search_results, query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


