import re
import string

from nltk.corpus import stopwords

STOP_WORDS = set(stopwords.words("english"))


def preprocess_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text (str): Raw extracted text.

    Returns:
        str: Cleaned text.
    """

    # Lowercase
    text = text.lower()

    # Remove email addresses
    text = re.sub(r"\S+@\S+", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Remove phone numbers
    text = re.sub(r"\+?\d[\d\s\-]{8,}\d", " ", text)

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Remove digits
    text = re.sub(r"\d+", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    words = [
        word
        for word in text.split()
        if word not in STOP_WORDS
    ]

    return " ".join(words)