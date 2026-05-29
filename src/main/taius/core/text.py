import re


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9_+\-*/']+", str(text).lower())
