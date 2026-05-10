import re
from typing import Dict


class PromptNormalizer:
    """
    Cleans and standardises extracted prompt content.

    This stage prepares messy input text for clue extraction and JSON structuring.
    It does not import or call the pipeline controller. It only performs
    prompt-level normalisation.
    """

    def normalize(self, extracted_text: str) -> Dict:
        """
        Receives extracted text and returns a cleaned prompt object.
        """
        if extracted_text is None:
            extracted_text = ""

        original_length = len(extracted_text)

        cleaned_text = self._clean_whitespace(extracted_text)
        cleaned_text = self._remove_extraction_labels(cleaned_text)
        cleaned_text = self._standardise_quotes(cleaned_text)

        return {
            "normalized_prompt": cleaned_text,
            "normalization_status": "success",
            "original_character_length": original_length,
            "normalized_character_length": len(cleaned_text)
        }

    def _clean_whitespace(self, text: str) -> str:
        """
        Removes unnecessary line breaks and repeated spaces.
        """
        text = text.replace("\r", " ").replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _remove_extraction_labels(self, text: str) -> str:
        """
        Removes labels used in simulated document/image extracted inputs.
        """
        labels = [
            "Document extracted prompt:",
            "Image/OCR extracted prompt:"
        ]

        for label in labels:
            text = text.replace(label, "")

        return text.strip()

    def _standardise_quotes(self, text: str) -> str:
        """
        Converts smart quotes into normal quotes for consistent processing.
        """
        text = text.replace("“", "\"").replace("”", "\"")
        text = text.replace("‘", "'").replace("’", "'")
        return text
