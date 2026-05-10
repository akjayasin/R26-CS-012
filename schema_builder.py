from typing import Dict, List


class SchemaBuilder:
    """
    Builds a compact downstream JSON package.

    The detailed processing metadata is not placed inside the main JSON output.
    It is written separately into status logs by the pipeline controller.
    """

    def build_schema(
        self,
        trace_id: str,
        input_metadata: Dict,
        extraction_result: Dict,
        normalization_result: Dict,
        clue_package: Dict,
        context_selection_result: Dict,
        evaluation_result: Dict
    ) -> Dict:

        selected_blocks = context_selection_result.get("selected_context_blocks", [])

        return {
            "package_type": "minimal_context_prompt_package",
            "trace_id": trace_id,
            "source": "Prompt Agent",
            "destination": "Risk Intelligence Framework",

            "user_request": normalization_result.get("normalized_prompt"),

            "request_analysis": {
                "detected_intents": clue_package.get("detected_intents"),
                "domain_clues": clue_package.get("domain_clues"),
                "technical_keywords": clue_package.get("keywords")
            },

            "selected_code_context": self._format_selected_blocks(selected_blocks),

            "handoff_status": "ready_for_next_component"
        }

    def _format_selected_blocks(self, selected_blocks: List[Dict]) -> List[Dict]:
        formatted = []

        for block in selected_blocks:
            formatted.append({
                "file": block.get("file_name"),
                "function": block.get("block_name"),
                "lines": f"{block.get('start_line')}-{block.get('end_line')}",
                "relevance_score": block.get("relevance_score"),
                "matched_clues": block.get("matched_clues"),
                "code": block.get("content")
            })

        return formatted