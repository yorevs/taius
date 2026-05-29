"""Module for text."""
import re


def tokenize(text):
    """Split text into normalized tokens."""
    return re.findall(r"[a-zA-Z0-9_+\-*/']+", str(text).lower())
