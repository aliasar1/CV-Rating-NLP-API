import os
import boto3
from flask import Flask, request, jsonify
import json
from jd_processor import JobDescriptionProcessor

# AWS S3 configurations
S3_BUCKET_NAME = 'skillsift'
S3_PROCESSED_PREFIX = 'processed'

app = Flask(__name__)

@app.route('/', methods=['GET'])
def data():
    return jsonify({'message': 'Hello WORLD'}) 

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    pdf_url = request.json.get('pdf_url')
    print(pdf_url)

    fname = f"{pdf_url.split('/')[-2]}"
    print(fname)
    path = f"{pdf_url.split('/')[-1].split('.')[0]}.pdf"
    print(path)
    
    s3 = boto3.client('s3', 
        aws_access_key_id = 'AKIA6GBMFP2FOFM3OEFD',
        aws_secret_access_key = '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'
    )

    current_directory = os.getcwd()
    local_pdf_path = os.path.join(current_directory, 'downloads', path)
    print(local_pdf_path)
    print(f"jobs/{fname}/{path}")
    s3.download_file(
        Bucket=S3_BUCKET_NAME,
        Key=f"jobs/{fname}/{path}",
        Filename=local_pdf_path,
    )

    try:

        jd_processor = JobDescriptionProcessor(local_pdf_path)
        jd_data = jd_processor.process()    

        # Delete the temporary file
        os.remove(local_pdf_path)

        # Dump JSON to S3 bucket
        json_data = json.dumps(jd_data)
        destination_key = f"{S3_PROCESSED_PREFIX}/{path.split('.')[0]}.json"
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=destination_key, Body=json_data)

        return jsonify({'message': 'Processing completed successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
