import csv
import json
import os
import re


CONFIG = {}
MODEL = {}


SKILL_ID = 'math.divide'
SKILL_VERSION = "0.1.0"
CONTRACT_VERSION = "1.0"
VERBS = ['divide']
SYMBOL = '/'
EXAMPLES = ['divide 10 2', '10 / 2', 'divide 9 3']


def describe() -> dict:
    return {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "input_type": "text",
        "output_type": "number",
        "examples": EXAMPLES
    }


def configure(config: dict):
    global CONFIG
    CONFIG = dict(config)
    os.makedirs(CONFIG["model_dir"], exist_ok=True)
    load_model()


def model_path():
    return os.path.join(CONFIG["model_dir"], "model.json")


def train_path():
    return os.path.join(CONFIG["model_dir"], "train.csv")


def parse_numbers(input_data):
    text = str(input_data).strip().lower()
    escaped_symbol = re.escape(SYMBOL)

    symbol_match = re.match(
        rf"^\s*(-?\d+(?:\.\d+)?)\s*{escaped_symbol}\s*(-?\d+(?:\.\d+)?)\s*$",
        text
    )

    if symbol_match:
        return float(symbol_match.group(1)), float(symbol_match.group(2))

    verb_pattern = "|".join(re.escape(verb) for verb in VERBS)

    verb_match = re.match(
        rf"^\s*(?:{verb_pattern})\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*$",
        text
    )

    if verb_match:
        return float(verb_match.group(1)), float(verb_match.group(2))

    raise ValueError(f"Invalid input for {SKILL_ID}: {input_data}")


def calculate(a, b):
    if SYMBOL == "/" and b == 0:
        raise ZeroDivisionError("division by zero")

    return a / b


def normalize_number(value):
    value = float(value)

    if value.is_integer():
        return int(value)

    return value


def can_handle(input_data):
    try:
        parse_numbers(input_data)
        return True
    except Exception:
        return False


def can_train() -> bool:
    return True


def needs_training() -> bool:
    return not os.path.exists(model_path())


def seed_rows():
    rows = []

    for example in EXAMPLES:
        try:
            a, b = parse_numbers(example)
            rows.append({
                "input": example,
                "output": str(normalize_number(calculate(a, b)))
            })
        except Exception:
            continue

    return rows


def ensure_train_file():
    if os.path.exists(train_path()):
        return

    with open(train_path(), "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["input", "output"])
        writer.writeheader()
        writer.writerows(seed_rows())


def train():
    ensure_train_file()

    rows = training_examples()
    model = {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "examples": rows
    }

    with open(model_path(), "w") as file:
        json.dump(model, file, indent=2, sort_keys=True)

    load_model()


def load_model():
    global MODEL

    if not CONFIG:
        MODEL = {}
        return

    if not os.path.exists(model_path()):
        MODEL = {}
        return

    with open(model_path(), "r") as file:
        MODEL = json.load(file)


def predict(input_data):
    text = str(input_data).strip()

    for row in training_examples():
        if row["input"].strip().lower() == text.lower():
            return normalize_number(float(row["output"]))

    a, b = parse_numbers(input_data)
    return normalize_number(calculate(a, b))


def teach(input_data, expected_output):
    ensure_train_file()

    rows = training_examples()
    normalized_input = str(input_data).strip()
    normalized_output = str(expected_output).strip()

    kept_rows = [
        row
        for row in rows
        if row["input"].strip().lower() != normalized_input.lower()
    ]

    kept_rows.append({
        "input": normalized_input,
        "output": normalized_output
    })

    with open(train_path(), "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["input", "output"])
        writer.writeheader()
        writer.writerows(kept_rows)

    train()
    return True


def forget(input_data, expected_output=None):
    if not os.path.exists(train_path()):
        return False

    normalized_input = str(input_data).strip().lower()
    rows = training_examples()

    kept_rows = [
        row
        for row in rows
        if row["input"].strip().lower() != normalized_input
    ]

    with open(train_path(), "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["input", "output"])
        writer.writeheader()
        writer.writerows(kept_rows)

    train()
    return len(kept_rows) != len(rows)


def training_examples():
    ensure_train_file()

    with open(train_path(), "r", newline="") as file:
        return list(csv.DictReader(file))


def export_data():
    return {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "examples": training_examples()
    }


def import_data(data):
    rows = data.get("examples", [])

    os.makedirs(CONFIG["model_dir"], exist_ok=True)

    with open(train_path(), "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["input", "output"])
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "input": row["input"],
                "output": row["output"]
            })

    train()
