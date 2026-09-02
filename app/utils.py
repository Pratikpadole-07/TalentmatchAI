import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def is_pdf(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


def create_directory(path: str):
    os.makedirs(path, exist_ok=True)


def get_pdf_files(folder: str):
    return [
        file
        for file in os.listdir(folder)
        if file.endswith(".pdf")
    ]