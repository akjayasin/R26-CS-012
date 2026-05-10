import json
import logging
from pathlib import Path
from datetime import datetime


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_path(relative_path: str) -> Path:
    """
    Converts a project-relative path into a full system path.
    This helps the middleware work correctly regardless of where it is executed from.
    """
    return PROJECT_ROOT / relative_path


def ensure_directory(path: Path) -> None:
    """
    Creates a folder if it does not already exist.
    """
    path.mkdir(parents=True, exist_ok=True)


def load_json_file(file_path: Path) -> dict:
    """
    Loads a JSON file and returns it as a Python dictionary.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json_file(file_path: Path, data: dict) -> None:
    """
    Writes a Python dictionary into a formatted JSON file.
    """
    ensure_directory(file_path.parent)

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def read_text_file(file_path: Path) -> str:
    """
    Reads a text-based file and returns its content.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")

    with file_path.open("r", encoding="utf-8", errors="ignore") as file:
        return file.read()


def get_timestamp() -> str:
    """
    Generates a timestamp for traceability.
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def setup_logger(log_file_path: Path) -> logging.Logger:
    """
    Creates a middleware logger that writes both to terminal and log file.
    """
    ensure_directory(log_file_path.parent)

    logger = logging.getLogger("CPSM_Middleware")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger