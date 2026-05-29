import csv
import json
import math
import os
import re
from collections import defaultdict

SKILL_ID = "text.sentiment"
SKILL_VERSION = "0.1.0"

CONFIG = {}
MODEL_PATH = None
TRAIN_PATH = None
VERSION_PATH = None


def configure(config):
    global CONFIG, MODEL_PATH, TRAIN_PATH, VERSION_PATH

    CONFIG = config

    model_dir = CONFIG["model_dir"]
    os.makedirs(model_dir, exist_ok=True)

    MODEL_PATH = os.path.join(model_dir, "model.json")
    TRAIN_PATH = os.path.join(model_dir, "train.csv")
    VERSION_PATH = os.path.join(model_dir, ".skill-version")


def describe():
    return {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": "1.0",
        "input_type": "text",
        "output_type": "label",
        "examples": [
            "sentiment I love this",
            "sentiment this is terrible",
            "is this positive: amazing work"
        ]
    }


def can_handle(input_data):
    text = str(input_data).strip().lower()

    return (
        text.startswith("sentiment ")
        or text.startswith("is this positive:")
        or text.startswith("is this negative:")
    )


def can_train():
    return True


def needs_training():
    if MODEL_PATH is None:
        return True

    if not os.path.exists(MODEL_PATH):
        return True

    if not os.path.exists(VERSION_PATH):
        return True

    with open(VERSION_PATH, "r") as file:
        return file.read().strip() != SKILL_VERSION


def tokenize(text):
    return re.findall(r"[a-zA-Z']+", text.lower())


def normalize_input(input_data):
    text = str(input_data).strip()

    prefixes = [
        "sentiment ",
        "is this positive:",
        "is this negative:"
    ]

    lowered = text.lower()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix):].strip()

    return text


def generate_training_file():
    rows = [
        ("I love this", "positive"),
        ("this is great", "positive"),
        ("amazing work", "positive"),
        ("excellent result", "positive"),
        ("very good", "positive"),
        ("I like this", "positive"),
        ("this makes me happy", "positive"),
        ("perfect job", "positive"),
        ("beautiful output", "positive"),
        ("that is awesome", "positive"),

        ("I hate this", "negative"),
        ("this is terrible", "negative"),
        ("awful work", "negative"),
        ("bad result", "negative"),
        ("very poor", "negative"),
        ("I dislike this", "negative"),
        ("this makes me angry", "negative"),
        ("horrible job", "negative"),
        ("ugly output", "negative"),
        ("that is awful", "negative")
    ]

    with open(TRAIN_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "label"])
        writer.writerows(rows)


def train():
    generate_training_file()

    label_counts = defaultdict(int)
    word_counts = defaultdict(lambda: defaultdict(int))
    vocabulary = set()

    with open(TRAIN_PATH, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            label = row["label"]
            tokens = tokenize(row["text"])

            label_counts[label] += 1

            for token in tokens:
                vocabulary.add(token)
                word_counts[label][token] += 1

    model = {
        "version": SKILL_VERSION,
        "labels": dict(label_counts),
        "vocabulary": sorted(vocabulary),
        "word_counts": {
            label: dict(counts)
            for label, counts in word_counts.items()
        }
    }

    with open(MODEL_PATH, "w") as file:
        json.dump(model, file, indent=2, sort_keys=True)

    with open(VERSION_PATH, "w") as file:
        file.write(SKILL_VERSION)

    print(f"Trained {SKILL_ID}: {MODEL_PATH}")


def load_model():
    with open(MODEL_PATH, "r") as file:
        return json.load(file)


def predict(input_data):
    text = normalize_input(input_data)
    tokens = tokenize(text)
    model = load_model()

    labels = model["labels"]
    vocabulary = model["vocabulary"]
    word_counts = model["word_counts"]

    total_docs = sum(labels.values())
    vocab_size = max(1, len(vocabulary))

    scores = {}

    for label, label_count in labels.items():
        score = math.log(label_count / total_docs)
        total_words = sum(word_counts[label].values())

        for token in tokens:
            token_count = word_counts[label].get(token, 0)
            score += math.log((token_count + 1) / (total_words + vocab_size))

        scores[label] = score

    return max(scores, key=scores.get)


def teach(input_data, expected_output):
    text = normalize_input(input_data)
    label = str(expected_output).strip().lower()

    if label not in {"positive", "negative"}:
        raise ValueError("expected_output must be positive or negative")

    file_exists = os.path.exists(TRAIN_PATH)

    with open(TRAIN_PATH, "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["text", "label"])

        writer.writerow([text, label])

    train()


def forget(input_data, expected_output=None):
    text = normalize_input(input_data)

    if not os.path.exists(TRAIN_PATH):
        return

    kept_rows = []

    with open(TRAIN_PATH, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["text"].strip() == text:
                continue

            kept_rows.append(row)

    with open(TRAIN_PATH, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "label"])
        writer.writeheader()
        writer.writerows(kept_rows)

    train()


def training_examples():
    if not os.path.exists(TRAIN_PATH):
        return []

    with open(TRAIN_PATH, "r", newline="") as file:
        return list(csv.DictReader(file))



def export_data():
    return {
        "skill_id": SKILL_ID,
        "skill_version": SKILL_VERSION,
        "training_examples": training_examples(),
        "model_path": MODEL_PATH,
        "train_path": TRAIN_PATH
    }



def import_data(data):
    examples = data.get("training_examples", [])

    with open(TRAIN_PATH, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "label"])
        writer.writeheader()

        for row in examples:
            writer.writerow(
                {
                    "text": row["text"],
                    "label": row["label"]
                }
            )

    train()
