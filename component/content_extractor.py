import json
from pathlib import Path
from typing import Dict

from utils import read_text_file


class ContentExtractor:
    """
    Converts different prompt-bearing input formats into plain text.

    PP1 Scope:
    - Real extraction is implemented for .txt, .md, .json, and image files.
    - Image files use OCR through pytesseract.
    - PDF, Word, and PowerPoint are still marked as future parser integrations.
    """

    def extract(self, file_path: Path) -> Dict:
        extension = file_path.suffix.lower()

        if extension in [".txt", ".md"]:
            return self._extract_text_file(file_path)

        if extension == ".json":
            return self._extract_json_file(file_path)

        if extension in [".png", ".jpg", ".jpeg"]:
            return self._extract_image_ocr(file_path)

        if extension in [".pdf", ".docx", ".pptx"]:
            return self._extract_document_placeholder(file_path)

        raise ValueError(f"Unsupported extraction format: {extension}")

    def _extract_text_file(self, file_path: Path) -> Dict:
        content = read_text_file(file_path)

        return {
            "extraction_method": "direct_text_read",
            "extracted_text": content,
            "extraction_status": "success"
        }

    def _extract_json_file(self, file_path: Path) -> Dict:
        raw_content = read_text_file(file_path)

        try:
            parsed_json = json.loads(raw_content)
        except json.JSONDecodeError:
            return {
                "extraction_method": "json_read_failed_fallback_to_text",
                "extracted_text": raw_content,
                "extraction_status": "partial_success"
            }

        prompt_text = (
            parsed_json.get("prompt")
            or parsed_json.get("message")
            or parsed_json.get("text")
            or raw_content
        )

        return {
            "extraction_method": "json_field_extraction",
            "extracted_text": prompt_text,
            "original_json_keys": list(parsed_json.keys()),
            "extraction_status": "success"
        }

    def _extract_image_ocr(self, file_path: Path) -> Dict:
        """
        Extracts readable text from image prompts using OCR.

        Supported use cases:
        - screenshots of error messages
        - screenshots of code
        - screenshots of console logs
        - screenshots of issue tickets
        """
        try:
            from PIL import Image
            import pytesseract

            # Windows default Tesseract installation path.
            # If Tesseract is installed somewhere else, update this line.
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

            if Path(tesseract_path).exists():
                pytesseract.pytesseract.tesseract_cmd = tesseract_path

            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image)

            if not extracted_text.strip():
                return {
                    "extraction_method": "image_ocr",
                    "extracted_text": "",
                    "extraction_status": "failed",
                    "implementation_note": "OCR ran but no readable text was detected."
                }

            return {
                "extraction_method": "image_ocr",
                "extracted_text": extracted_text,
                "extraction_status": "success"
            }

        except ImportError as error:
            return {
                "extraction_method": "image_ocr",
                "extracted_text": "",
                "extraction_status": "failed",
                "error": str(error),
                "implementation_note": (
                    "Install required packages using: pip install pillow pytesseract"
                )
            }

        except Exception as error:
            return {
                "extraction_method": "image_ocr",
                "extracted_text": "",
                "extraction_status": "failed",
                "error": str(error),
                "implementation_note": (
                    "Check whether Tesseract OCR is installed and available at "
                    "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                )
            }

    def _extract_document_placeholder(self, file_path: Path) -> Dict:
        """
        Placeholder for future PDF, Word, and PowerPoint parsing.

        Full version can integrate:
        - PyPDF2 / pymupdf for PDF
        - python-docx for Word
        - python-pptx for PowerPoint
        """
        return {
            "extraction_method": "document_parser_placeholder",
            "extracted_text": "",
            "extraction_status": "not_enabled_in_pp1",
            "implementation_note": (
                "PDF, Word, and PowerPoint extraction can be integrated in the next phase."
            )
        }