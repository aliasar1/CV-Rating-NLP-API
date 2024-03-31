import boto3
import os
import json
from parse_jd_to_json import ParseJobDesc
from read_pdf import read_single_pdf

# AWS S3 configurations
S3_BUCKET_NAME = 'skillsift'
S3_PREFIX = 'jobs'
S3_PROCESSED_PREFIX = 'processed/jobs'

class JobDescriptionProcessor:
    def __init__(self, input_file):
        self.input_file = input_file

    def process(self) -> dict:
        try:
            jd_dict = self._read_job_desc()
            self._write_json_file(jd_dict)
            return jd_dict
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {}

    def _read_job_desc(self) -> dict:
        # Initialize S3 client
        s3 = boto3.client('s3')

        # Read the PDF file from S3
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=self.input_file)
        data = response['Body'].read()

        # Process the PDF data
        output = ParseJobDesc(data).get_JSON()
        return output

    def _write_json_file(self, jd_dict: dict):
        # Extracting the filename without extension from the input file path
        filename_without_extension = os.path.splitext(self.input_file)[0]
        # Construct the S3 key for the JSON file
        json_key = f"{S3_PROCESSED_PREFIX}/{filename_without_extension}.json"

        # Initialize S3 client
        s3 = boto3.client('s3')

        # Writing JSON data to the S3 bucket
        s3.put_object(Bucket=S3_BUCKET_NAME, Key=json_key, Body=json.dumps(jd_dict, indent=4))

if __name__ == "__main__":
    JobDescriptionProcessor().process()