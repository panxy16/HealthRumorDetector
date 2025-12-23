from docx import Document
from loaders.base import BaseLoader

class DocxLoader(BaseLoader):
    def load(self, path: str) -> str:
        doc = Document(path)
        lines = []
        for p in doc.paragraphs:
            if p.text.strip():
                lines.append(p.text.strip())
        return "\n\n".join(lines)
