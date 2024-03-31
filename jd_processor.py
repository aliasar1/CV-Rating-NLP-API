import os
from read_pdf import read_single_pdf
from parse_jd_to_json import ParseJobDesc

class JobDescriptionProcessor:
    def __init__(self, input_file):
        self.input_file = input_file

    def process(self) -> dict:
        try:
            resume_dict = self._read_job_desc()
            return resume_dict
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {}

    def _read_job_desc(self) -> dict:
        data = read_single_pdf(self.input_file)
        print(data)
        output = ParseJobDesc(data).get_JSON()
        return output