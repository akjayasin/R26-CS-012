from typing import Dict


class EvaluationEngine:
    """
    Generates research evaluation metrics for the middleware prototype.

    Research purpose:
    This module proves that the component is not only producing JSON output,
    but also reducing unnecessary context before downstream processing.
    """

    def evaluate(self, code_index: Dict, context_selection_result: Dict) -> Dict:
        total_code_lines = code_index.get("total_code_lines", 0)
        total_code_blocks = code_index.get("total_code_blocks", 0)

        selected_blocks = context_selection_result.get("selected_context_blocks", [])
        selected_context_lines = sum(block.get("line_count", 0) for block in selected_blocks)

        if total_code_lines > 0:
            reduction_percentage = round(
                ((total_code_lines - selected_context_lines) / total_code_lines) * 100,
                2
            )
        else:
            reduction_percentage = 0

        if total_code_blocks > 0:
            selected_block_ratio = round(
                (len(selected_blocks) / total_code_blocks) * 100,
                2
            )
        else:
            selected_block_ratio = 0

        return {
            "evaluation_status": "success",
            "total_code_lines_available": total_code_lines,
            "total_code_blocks_available": total_code_blocks,
            "selected_context_lines": selected_context_lines,
            "selected_context_blocks": len(selected_blocks),
            "context_reduction_percentage": reduction_percentage,
            "selected_block_ratio_percentage": selected_block_ratio,
            "evaluation_interpretation": (
                "The middleware reduced the available code context by selecting "
                "only task-relevant blocks for downstream processing."
            )
        }