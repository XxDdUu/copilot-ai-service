import fitz

class PdfService:

    def extract_text(self, file_path):

        doc = fitz.open(file_path)

        text = ""

        for page in doc:
            text += page.get_text()

        return text