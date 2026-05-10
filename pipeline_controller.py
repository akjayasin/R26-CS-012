from pathlib import Path
from typing import Dict

from utils import (
    resolve_path,
    load_json_file,
    write_json_file,
    get_timestamp,
    setup_logger
)

from input_handler import InputHandler
from content_extractor import ContentExtractor
from prompt_normalizer import PromptNormalizer
from clue_extractor import ClueExtractor
from code_context_indexer import CodeContextIndexer
from context_orchestrator import ContextOrchestrator
from evaluation_engine import EvaluationEngine
from schema_builder import SchemaBuilder


class PipelineController:
    """
    Main orchestration layer for the middleware prototype.

    This controller simulates how the component would behave when integrated
    between the Prompt Agent and the Risk Intelligence Framework.
    """

    def __init__(self):
        self.project_root = resolve_path("")
        self.config_path = resolve_path("config/pipeline_config.json")
        self.config = load_json_file(self.config_path)

        timestamp = get_timestamp()
        log_path = resolve_path(f"outputs/logs/middleware_run_{timestamp}.log")
        self.logger = setup_logger(log_path)

        self.input_folder = resolve_path("inputs")
        self.codebase_folder = resolve_path("codebase")

        self.structured_output_folder = resolve_path(
            self.config["output_settings"]["structured_output_folder"]
        )

        self.evaluation_output_folder = resolve_path(
            self.config["output_settings"]["evaluation_output_folder"]
        )

        context_config = self.config.get("context_selection", {})

        self.input_handler = InputHandler(
            input_folder=self.input_folder,
            supported_input_types=self.config.get("supported_input_types", [])
        )

        self.content_extractor = ContentExtractor()
        self.prompt_normalizer = PromptNormalizer()
        self.clue_extractor = ClueExtractor()
        self.code_context_indexer = CodeContextIndexer()

        self.context_orchestrator = ContextOrchestrator(
            max_selected_blocks=context_config.get("max_selected_blocks", 3),
            minimum_relevance_score=context_config.get("minimum_relevance_score", 1)
        )

        self.evaluation_engine = EvaluationEngine()
        self.schema_builder = SchemaBuilder()

    def run(self) -> Dict:
        """
        Runs the middleware pipeline for all supported files in the inputs folder.
        """
        self.logger.info("Middleware pipeline started.")
        self.logger.info(f"Component name: {self.config.get('component_name')}")
        self.logger.info("Running PP1 standalone middleware simulation.")

        input_files = self.input_handler.discover_inputs()

        if not input_files:
            self.logger.warning("No supported input files found.")
            return {
                "pipeline_status": "no_inputs_found",
                "processed_files": 0
            }

        self.logger.info(f"Discovered {len(input_files)} supported input file(s).")

        self.logger.info("Building code context index from codebase folder.")
        code_index = self.code_context_indexer.build_index(self.codebase_folder)

        self.logger.info(
            f"Indexed {code_index.get('total_files_indexed')} file(s), "
            f"{code_index.get('total_code_blocks')} code block(s), "
            f"{code_index.get('total_code_lines')} total code line(s)."
        )

        processed_results = []

        for input_file in input_files:
            try:
                result = self._process_single_input(input_file, code_index)
                processed_results.append(result)

            except Exception as error:
                self.logger.error(f"Failed to process {input_file.name}: {error}")
                processed_results.append({
                    "file_name": input_file.name,
                    "status": "failed",
                    "error": str(error)
                })

        summary = {
            "pipeline_status": "completed",
            "processed_files": len(processed_results),
            "successful_files": len([
                item for item in processed_results
                if item.get("status") == "success"
            ]),
            "failed_files": len([
                item for item in processed_results
                if item.get("status") == "failed"
            ]),
            "results": processed_results
        }

        summary_path = self.evaluation_output_folder / "pipeline_run_summary.json"
        write_json_file(summary_path, summary)

        self.logger.info("Middleware pipeline completed.")
        self.logger.info(f"Pipeline summary written to: {summary_path}")

        return summary

    def _process_single_input(self, input_file: Path, code_index: Dict) -> Dict:
        """
        Runs the complete processing chain for one input file.
        """
        trace_id = f"CPSM-{get_timestamp()}-{input_file.stem}"

        self.logger.info(f"Processing input: {input_file.name}")

        input_metadata = self.input_handler.describe_input(input_file)
        self.logger.info(f"Input detected: {input_metadata}")

        extraction_result = self.content_extractor.extract(input_file)
        self.logger.info(
            f"Content extraction method: {extraction_result.get('extraction_method')}"
        )

        normalization_result = self.prompt_normalizer.normalize(
            extraction_result.get("extracted_text", "")
        )
        self.logger.info("Prompt normalization completed.")

        clue_package = self.clue_extractor.extract(
            normalization_result.get("normalized_prompt", "")
        )
        self.logger.info(f"Extracted clues: {clue_package.get('weighted_clues')}")

        context_selection_result = self.context_orchestrator.select_context(
            clue_package=clue_package,
            code_index=code_index
        )
        self.logger.info(
            f"Selected {len(context_selection_result.get('selected_context_blocks', []))} "
            "relevant code block(s)."
        )

        evaluation_result = self.evaluation_engine.evaluate(
            code_index=code_index,
            context_selection_result=context_selection_result
        )
        self.logger.info(
            f"Context reduction: {evaluation_result.get('context_reduction_percentage')}%"
        )

        structured_schema = self.schema_builder.build_schema(
            trace_id=trace_id,
            input_metadata=input_metadata,
            extraction_result=extraction_result,
            normalization_result=normalization_result,
            clue_package=clue_package,
            context_selection_result=context_selection_result,
            evaluation_result=evaluation_result
        )

        output_file_name = f"structured_output_{input_file.stem}.json"
        output_path = self.structured_output_folder / output_file_name
        write_json_file(output_path, structured_schema)

        status_file_name = f"status_log_{input_file.stem}.txt"
        status_path = self.evaluation_output_folder / status_file_name

        self._write_status_log(
            status_path=status_path,
            trace_id=trace_id,
            input_metadata=input_metadata,
            extraction_result=extraction_result,
            normalization_result=normalization_result,
            clue_package=clue_package,
            context_selection_result=context_selection_result,
            evaluation_result=evaluation_result
        )

        self.logger.info(f"Structured output written to: {output_path}")
        self.logger.info(f"Status log written to: {status_path}")

        return {
            "file_name": input_file.name,
            "status": "success",
            "trace_id": trace_id,
            "structured_output": str(output_path),
            "status_log": str(status_path),
            "context_reduction_percentage": evaluation_result.get(
                "context_reduction_percentage"
            ),
            "selected_context_blocks": evaluation_result.get(
                "selected_context_blocks"
            )
        }

    def _write_status_log(
        self,
        status_path: Path,
        trace_id: str,
        input_metadata: Dict,
        extraction_result: Dict,
        normalization_result: Dict,
        clue_package: Dict,
        context_selection_result: Dict,
        evaluation_result: Dict
    ) -> None:
        """
        Writes detailed processing status into a separate readable log file.
        This keeps the main structured output clean and model/component friendly.
        """
        selected_blocks = context_selection_result.get("selected_context_blocks", [])

        lines = [
            "CPSM Middleware Processing Status Log",
            "====================================",
            f"Trace ID: {trace_id}",
            "",
            "Input Details",
            "-------------",
            f"Input File: {input_metadata.get('file_name')}",
            f"Input Type: {input_metadata.get('file_extension')}",
            f"File Size: {input_metadata.get('file_size_bytes')} bytes",
            f"Extraction Method: {extraction_result.get('extraction_method')}",
            f"Extraction Status: {extraction_result.get('extraction_status')}",
            "",
            "Prompt Analysis",
            "---------------",
            f"Normalized Prompt: {normalization_result.get('normalized_prompt')}",
            f"Detected Intents: {clue_package.get('detected_intents')}",
            f"Domain Clues: {clue_package.get('domain_clues')}",
            f"Technical Keywords: {clue_package.get('keywords')}",
            "",
            "Selected Context",
            "----------------",
            f"Selected Block Count: {len(selected_blocks)}"
        ]

        for block in selected_blocks:
            lines.append(
                f"- {block.get('block_name')} "
                f"({block.get('file_name')} lines "
                f"{block.get('start_line')}-{block.get('end_line')}) "
                f"| Score: {block.get('relevance_score')}"
            )

        lines.extend([
            "",
            "Research Evaluation Snapshot",
            "----------------------------",
            f"Evaluation Status: {evaluation_result.get('evaluation_status')}",
            f"Total Code Lines Available: "
            f"{evaluation_result.get('total_code_lines_available')}",
            f"Total Code Blocks Available: "
            f"{evaluation_result.get('total_code_blocks_available')}",
            f"Selected Context Lines: "
            f"{evaluation_result.get('selected_context_lines')}",
            f"Selected Context Blocks: "
            f"{evaluation_result.get('selected_context_blocks')}",
            f"Context Reduction Percentage: "
            f"{evaluation_result.get('context_reduction_percentage')}%",
            f"Selected Block Ratio Percentage: "
            f"{evaluation_result.get('selected_block_ratio_percentage')}%",
            "",
            "Interpretation",
            "--------------",
            evaluation_result.get("evaluation_interpretation", ""),
            "",
            "Component Boundary",
            "------------------",
            "This component performs prompt structuring and minimal context orchestration only.",
            "Sensitive data detection, risk tagging, masking, and AI response generation are excluded."
        ])

        status_path.parent.mkdir(parents=True, exist_ok=True)

        with status_path.open("w", encoding="utf-8") as file:
            file.write("\n".join(lines))
