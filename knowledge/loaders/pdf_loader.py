import pdfplumber
from loaders.base import BaseLoader

class PDFLoader(BaseLoader):
    def load(self, path: str) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text

