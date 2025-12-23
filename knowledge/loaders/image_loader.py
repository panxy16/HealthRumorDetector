from PIL import Image
import pytesseract
from loaders.base import BaseLoader

class ImageLoader(BaseLoader):
    def load(self, path: str) -> str:
        text = pytesseract.image_to_string(
            Image.open(path),
            lang="chi_sim+eng"
        )
        return text.strip()
