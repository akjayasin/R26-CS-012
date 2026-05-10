from pathlib import Path
from typing import List, Dict


class InputHandler:
    """
    Responsible for discovering input files and identifying their format.
    In the full system, these inputs would arrive from the Prompt Agent.
    In this PP1 prototype, they are simulated through files inside the inputs folder.
    """

    def __init__(self, input_folder: Path, supported_input_types: List[str]):
        self.input_folder = input_folder
        self.supported_input_types = supported_input_types

    def discover_inputs(self) -> List[Path]:
        """
        Finds all supported input files from the inputs folder.
        """
        if not self.input_folder.exists():
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")

        discovered_files = []

        for file_path in self.input_folder.iterdir():
            if file_path.is_file() and self.is_supported(file_path):
                discovered_files.append(file_path)

        return sorted(discovered_files)

    def is_supported(self, file_path: Path) -> bool:
        """
        Checks whether the file extension is supported by the middleware.
        """
        return file_path.suffix.lower() in self.supported_input_types

    def describe_input(self, file_path: Path) -> Dict:
        """
        Creates metadata about the input file for traceability.
        """
        return {
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lower(),
            "file_size_bytes": file_path.stat().st_size,
            "simulated_source_component": "Prompt Agent"
        }