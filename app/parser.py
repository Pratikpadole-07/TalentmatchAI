from pypdf import PdfReader


def extract_text(pdf_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): Path to PDF

    Returns:
        str: Extracted text
    """

    text = ""

    reader = PdfReader(pdf_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()