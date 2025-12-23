from loaders.pdf_loader import PDFLoader
from loaders.docx_loader import DocxLoader
from loaders.pptx_loader import PPTXLoader
from loaders.image_loader import ImageLoader

LOADER_MAP = {
    ".pdf": PDFLoader(),
    ".docx": DocxLoader(),
    ".pptx": PPTXLoader(),
    ".png": ImageLoader(),
    ".jpg": ImageLoader(),
    ".jpeg": ImageLoader(),
}

def get_loader(path: str):
    for ext, loader in LOADER_MAP.items():
        if path.lower().endswith(ext):
            return loader
    raise ValueError(f"Unsupported file type: {path}")
