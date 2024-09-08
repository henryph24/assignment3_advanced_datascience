import pytest
from app import app, jobs, load_preprocessed_data, preprocess_text, classify_job
from flask import url_for

@pytest.fixture
def client():
    # Create a test client for the Flask app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    # Test the main page route
    response = client.get('/')
    assert response.status_code == 200
    assert b'Job Listings' in response.data

def test_job_listing_route(client):
    # Test individual job listing route
    if jobs:
        first_job_id = jobs[0]['webindex']
        response = client.get(f'/job/{first_job_id}')
        assert response.status_code == 200
        assert b'Description' in response.data
    else:
        pytest.skip("No jobs available to test")

def test_category_jobs_route(client):
    # Test category-specific job listings route
    response = client.get('/category/Engineering')
    assert response.status_code == 200
    assert b'Engineering' in response.data

def test_post_job_get(client):
    # Test GET request to post job page
    response = client.get('/post_job')
    assert response.status_code == 200
    assert b'Post a New Job' in response.data

def test_post_job_post(client):
    # Test POST request to create a new job
    data = {
        'title': 'Test Job',
        'company': 'Test Company',
        'description': 'This is a test job description',
        'category': 'Engineering'
    }
    response = client.post('/post_job', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Job' in response.data

def test_classify_route(client):
    # Test job classification route
    data = {'description': 'This is a test job description for a software developer'}
    response = client.post('/classify', data=data)
    assert response.status_code == 200
    assert response.data.decode('utf-8') in [job['category'] for job in jobs]

def test_load_preprocessed_data():
    # Test loading preprocessed job data
    loaded_jobs = load_preprocessed_data('assess3_data/assess3_data/preprocessed_jobs.txt')
    assert len(loaded_jobs) > 0
    assert 'category' in loaded_jobs[0]
    assert 'webindex' in loaded_jobs[0]

def test_preprocess_text():
    # Test text preprocessing function
    text = "This is a TEST job description!"
    processed = preprocess_text(text)
    assert processed == "test job description"

def test_classify_job():
    # Test job classification function
    description = "This is a job for a software developer with experience in Python and Flask"
    category = classify_job(description)
    assert category in [job['category'] for job in jobs]