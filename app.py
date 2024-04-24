import os
import boto3
from flask import Flask, request, jsonify
import json
from resume_processor import ResumeProcessor
from similarity import match
from jd_processor import JobDescriptionProcessor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS S3 configurations
S3_BUCKET_NAME = 'skillsift'

app = Flask(__name__)

s3 = boto3.client('s3', 
    aws_access_key_id =  os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
)

@app.route('/home', methods=['GET'])
def process_cv_to_rate():
 return jsonify({'success': True, 'message': 'HELLO WORLD!'})

@app.route('/process_cv_to_rate', methods=['GET'])
def process_cv_to_rate():
    cv_url = request.json.get('cv_url')
    jd_json_url = request.json.get('jd_url')

    fname_cv = f"{cv_url.split('/')[-3]}/{cv_url.split('/')[-2]}"
    path_cv = f"{cv_url.split('/')[-1].split('.')[0]}.pdf"

    current_directory = os.getcwd()
    local_cv_path = os.path.join(current_directory, 'cv_downloads', path_cv)
    s3.download_file(
        Bucket=S3_BUCKET_NAME,
        Key=f"jobs/{fname_cv}/{path_cv}",
        Filename=local_cv_path,
    )

    try:
        resume_processor = ResumeProcessor(local_cv_path)
        resume_data = resume_processor.process()

        fname_jd = f"{jd_json_url.split('/')[-2]}"
        path_jd = f"{jd_json_url.split('/')[-1].split('.')[0]}.json"
        local_jd_path = os.path.join(current_directory, 'jd_downloads', path_jd)
        
        s3.download_file(
            Bucket=S3_BUCKET_NAME,
            Key=f"processed/{path_jd}",
            Filename=local_jd_path,
        )

        cv_kw = resume_data['extracted_keywords']
        
        with open(local_jd_path, 'r') as json_file:
            jd_data = json.load(json_file)
        jd_extracted_keywords = jd_data.get('extracted_keywords', [])
        
        resume_string = ' '.join(cv_kw)
        jd_string = ' '.join(jd_extracted_keywords)
        rating = match(resume_string, jd_string)

        # Delete the temporary files
        os.remove(local_cv_path)
        os.remove(local_jd_path)

        return jsonify({'success': True, 'message': 'Processing completed successfully!', 'rating': rating})
    except Exception as e:
        return jsonify({'success': False,  'error': str(e)}), 500

@app.route('/process_jd', methods=['POST'])
def process_pdf():
    pdf_url = request.json.get('pdf_url')

    fname_pdf = f"{pdf_url.split('/')[-2]}"
    path_pdf = f"{pdf_url.split('/')[-1].split('.')[0]}.pdf"
    
    current_directory = os.getcwd()
    local_pdf_path = os.path.join(current_directory, 'jd_downloads', path_pdf)
    s3.download_file(
        Bucket=S3_BUCKET_NAME,
        Key=f"jobs/{fname_pdf}/{path_pdf}",
        Filename=local_pdf_path,
    )

    try:
        jd_processor = JobDescriptionProcessor(local_pdf_path)
        jd_data = jd_processor.process()    

        # Delete the temporary file
        os.remove(local_pdf_path)

        # Dump JSON to S3 bucket
        json_data = json.dumps(jd_data)
        destination_key = f"processed/{path_pdf.split('.')[0]}.json"
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=destination_key, Body=json_data)

        object_url = f"https://{S3_BUCKET_NAME}.s3.eu-north-1.amazonaws.com/{destination_key}"

        return jsonify({'success': True, 'message': 'Processing completed successfully!', 'url': object_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
