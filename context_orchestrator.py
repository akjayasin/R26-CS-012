from typing import Dict, List


class ContextOrchestrator:
    """
    Selects minimal task-relevant code context from the indexed codebase.

    Research purpose:
    This is the central novelty area of the component. It reduces unnecessary
    context transfer by ranking code blocks against prompt-derived clues and
    selecting only the strongest relevant blocks.
    """

    def __init__(self, max_selected_blocks: int = 3, minimum_relevance_score: int = 1):
        self.max_selected_blocks = max_selected_blocks
        self.minimum_relevance_score = minimum_relevance_score

    def select_context(self, clue_package: Dict, code_index: Dict) -> Dict:
        weighted_clues = clue_package.get("weighted_clues", {})
        ranked_blocks = []

        for indexed_file in code_index.get("indexed_files", []):
            for block in indexed_file.get("code_blocks", []):
                scoring_result = self._score_block(block, weighted_clues)
                ranked_blocks.append({
                    "block_id": block["block_id"],
                    "file_name": block["file_name"],
                    "block_name": block["block_name"],
                    "start_line": block["start_line"],
                    "end_line": block["end_line"],
                    "line_count": block["line_count"],
                    "content": block["content"],
                    "relevance_score": scoring_result["score"],
                    "matched_clues": scoring_result["matched_clues"],
                    "called_functions": block.get("called_functions", [])
                })

        ranked_blocks.sort(key=lambda item: item["relevance_score"], reverse=True)

        directly_selected = [
            block for block in ranked_blocks
            if block["relevance_score"] >= self.minimum_relevance_score
        ][:self.max_selected_blocks]

        dependency_expanded = self._expand_with_dependencies(
            selected_blocks=directly_selected,
            ranked_blocks=ranked_blocks
        )

        final_selected = self._limit_and_deduplicate(dependency_expanded)

        return {
            "context_selection_status": "success",
            "selection_strategy": "weighted_clue_matching_with_dependency_awareness",
            "selected_context_blocks": final_selected,
            "ranking_details": ranked_blocks
        }

    def _score_block(self, block: Dict, weighted_clues: Dict[str, int]) -> Dict:
        block_text = (
            block.get("content", "") + " " +
            block.get("block_name", "") + " " +
            " ".join(block.get("tokens", []))
        ).lower()

        score = 0
        matched_clues = []

        for clue, weight in weighted_clues.items():
            clue_lower = clue.lower()

            if clue_lower in block_text:
                score += weight
                matched_clues.append(clue)

        # Extra structural score for action handlers
        block_name = block.get("block_name", "").lower()

        if any(term in weighted_clues for term in ["ui_interaction", "submit", "click", "save"]):
            if any(handler_word in block_name for handler_word in ["handle", "submit", "save"]):
                score += 3
                matched_clues.append("handler_pattern")

        if "debugging" in weighted_clues:
            if any(error_word in block_text for error_word in ["error", "failed", "catch", "console.error"]):
                score += 2
                matched_clues.append("error_handling_pattern")

        if "data_loading" in weighted_clues:
            if any(data_word in block_text for data_word in ["fetch", "load", "response", "api"]):
                score += 2
                matched_clues.append("data_loading_pattern")

        return {
            "score": score,
            "matched_clues": list(dict.fromkeys(matched_clues))
        }

    def _expand_with_dependencies(self, selected_blocks: List[Dict], ranked_blocks: List[Dict]) -> List[Dict]:
        """
        Adds directly related dependency blocks where possible.

        Example:
        If submitLoginForm is selected and it calls sendLoginRequest,
        the sendLoginRequest block can also be included if space is available.
        """
        expanded = selected_blocks.copy()
        selected_called_functions = set()

        for block in selected_blocks:
            for called_function in block.get("called_functions", []):
                selected_called_functions.add(called_function.lower())

        for block in ranked_blocks:
            if block["block_name"].lower() in selected_called_functions:
                expanded.append(block)

        return expanded

    def _limit_and_deduplicate(self, blocks: List[Dict]) -> List[Dict]:
        unique_blocks = []
        seen_ids = set()

        for block in blocks:
            if block["block_id"] not in seen_ids:
                unique_blocks.append(block)
                seen_ids.add(block["block_id"])

            if len(unique_blocks) >= self.max_selected_blocks:
                break

        return unique_blocks