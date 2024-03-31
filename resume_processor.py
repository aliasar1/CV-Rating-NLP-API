from parse_resume_to_json import ParseResume
from read_pdf import read_single_pdf

class ResumeProcessor:
    def __init__(self, input_file):
        self.input_file = input_file

    def process(self) -> dict:
        try:
            resume_dict = self._read_resumes()
            return resume_dict
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {}

    def _read_resumes(self) -> dict:
        data = read_single_pdf(self.input_file)
        output = ParseResume(data).get_JSON()
        return output
