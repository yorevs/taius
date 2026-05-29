"""Skill implementation module."""
import csv
import json
import os
import random
import re


CONFIG = {}
MODEL = {}

SKILL_ID = "math.approx"
SKILL_VERSION = "0.2.0"
CONTRACT_VERSION = "1.0"

TRAIN_EPOCHS = 5000
LEARNING_RATE = 0.0003
SCALE = 400.0

OPERATORS = ["+", "-", "*", "/"]

EXAMPLES = [
    "approx 2 + 3",
    "approx 10 - 4",
    "approx 3 * 7",
    "approx 10 / 2",
    "estimate 8 + 9",
    "estimate 12 / 3",
    "predict 4 * 6"
]


def describe() -> dict:
    """Return the module metadata contract."""
    return {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "input_type": "text",
        "output_type": "number",
        "examples": EXAMPLES
    }


def configure(config: dict):
    """Configure the module with the provided runtime settings."""
    global CONFIG
    CONFIG = dict(config)
    os.makedirs(CONFIG["model_dir"], exist_ok=True)
    load_model()


def model_path():
    """Execute model path."""
    return os.path.join(CONFIG["model_dir"], "model.json")


def train_path():
    """Execute train path."""
    return os.path.join(CONFIG["model_dir"], "train.csv")


def training_log_path():
    """Execute training log path."""
    return os.path.join(CONFIG["model_dir"], "training.log")


def write_training_log(message):
    """Execute write training log."""
    os.makedirs(CONFIG["model_dir"], exist_ok=True)

    with open(training_log_path(), "a") as file:
        file.write(message + "\n")


def parse_expression(input_data):
    """Execute parse expression."""
    text = str(input_data).strip().lower()

    for prefix in ["approx", "estimate", "predict"]:
        if text.startswith(prefix + " "):
            text = text[len(prefix):].strip()
            break

    match = re.match(
        r"^\s*(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)\s*$",
        text
    )

    if not match:
        raise ValueError(f"Invalid math approximation input: {input_data}")

    return float(match.group(1)), match.group(2), float(match.group(3))


def exact_result(a, op, b):
    """Execute exact result."""
    if op == "+":
        return a + b

    if op == "-":
        return a - b

    if op == "*":
        return a * b

    if op == "/":
        if b == 0:
            raise ZeroDivisionError("division by zero")

        return a / b

    raise ValueError(f"Unknown operator: {op}")


def normalize_number(value):
    """Execute normalize number."""
    value = float(value)

    if value.is_integer():
        return int(value)

    return round(value, 6)


def features(a, op, b):
    """Execute features."""
    safe_division = 0.0 if b == 0 else a / b

    return [
        1.0,
        a / SCALE,
        b / SCALE,
        (a + b) / SCALE,
        (a - b) / SCALE,
        (a * b) / SCALE,
        safe_division / SCALE,
    ]


def can_handle(input_data):
    """Return whether the input matches this handler."""
    text = str(input_data).strip().lower()

    if not text.startswith(("approx ", "estimate ", "predict ")):
        return False

    try:
        parse_expression(input_data)
        return True
    except Exception:
        return False


def can_train() -> bool:
    """Return whether the module supports training."""
    return True


def needs_training() -> bool:
    """Return whether the module needs training."""
    return not os.path.exists(model_path())


def seed_rows():
    """Execute seed rows."""
    rows = []

    for a in range(-20, 21):
        for b in range(-20, 21):
            for op in OPERATORS:
                if op == "/" and b == 0:
                    continue

                expression = f"approx {a} {op} {b}"
                rows.append({
                    "input": expression,
                    "output": str(exact_result(a, op, b))
                })

    return rows


def ensure_train_file():
    """Execute ensure train file."""
    if os.path.exists(train_path()):
        return

    with open(train_path(), "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["input", "output"])
        writer.writeheader()
        writer.writerows(seed_rows())


def training_examples():
    """Return the stored training examples."""
    ensure_train_file()

    with open(train_path(), "r", newline="") as file:
        return list(csv.DictReader(file))


def initial_weights(size):
    """Execute initial weights."""
    random.seed(42)
    return [random.uniform(-0.01, 0.01) for _ in range(size)]


def dot(left, right):
    """Execute dot."""
    return sum(a * b for a, b in zip(left, right))


def train_one_operator(op, parsed_rows):
    """Execute train one operator."""
    operator_rows = [
        (row_features, target)
        for row_op, row_features, target in parsed_rows
        if row_op == op
    ]

    if not operator_rows:
        return []

    weight_count = len(operator_rows[0][0])
    weights = initial_weights(weight_count)

    for _ in range(TRAIN_EPOCHS):
        random.shuffle(operator_rows)

        for row_features, target in operator_rows:
            prediction = dot(weights, row_features)
            error = prediction - target

            if error != error:
                raise ValueError("training diverged: nan error")

            for index, value in enumerate(row_features):
                weights[index] -= LEARNING_RATE * error * value

    return weights


def train():
    """Train the module and persist its model."""
    ensure_train_file()

    rows = training_examples()
    parsed_rows = []

    for row in rows:
        try:
            a, op, b = parse_expression(row["input"])
            target = float(row["output"]) / SCALE
            parsed_rows.append((op, features(a, op, b), target))
        except Exception:
            continue

    if not parsed_rows:
        raise ValueError("No valid training rows found.")

    report_every = max(1, TRAIN_EPOCHS // 100)
    weights_by_operator = {}

    write_training_log(
        f"epoch=0/{TRAIN_EPOCHS * len(OPERATORS)} loss=unknown "
        f"examples={len(parsed_rows)} batch_size=1"
    )

    global_epoch = 0

    for op in OPERATORS:
        operator_rows = [
            (row_features, target)
            for row_op, row_features, target in parsed_rows
            if row_op == op
        ]

        if not operator_rows:
            continue

        weight_count = len(operator_rows[0][0])
        weights = initial_weights(weight_count)

        for epoch in range(1, TRAIN_EPOCHS + 1):
            global_epoch += 1
            random.shuffle(operator_rows)
            total_loss = 0.0

            for row_features, target in operator_rows:
                prediction = dot(weights, row_features)
                error = prediction - target
                total_loss += error * error

                if error != error:
                    raise ValueError("training diverged: nan error")

                for index, value in enumerate(row_features):
                    weights[index] -= LEARNING_RATE * error * value

            if epoch == 1 or epoch == TRAIN_EPOCHS or epoch % report_every == 0:
                loss = total_loss / len(operator_rows)
                write_training_log(
                    f"epoch={global_epoch}/{TRAIN_EPOCHS * len(OPERATORS)} "
                    f"loss={loss:.8f} examples={len(operator_rows)} batch_size=1"
                )

        weights_by_operator[op] = weights

    model = {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "weights_by_operator": weights_by_operator,
        "feature_count": len(parsed_rows[0][1]),
        "epochs": TRAIN_EPOCHS,
        "learning_rate": LEARNING_RATE,
        "scale": SCALE,
        "examples": rows
    }

    with open(model_path(), "w") as file:
        json.dump(model, file, indent=2, sort_keys=True)

    load_model()


def load_model():
    """Load persisted model state from disk."""
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
    """Return the module prediction for the input."""
    if not MODEL:
        train()

    a, op, b = parse_expression(input_data)
    weights_by_operator = MODEL.get("weights_by_operator", {})
    weights = weights_by_operator.get(op)

    if not weights:
        raise ValueError(f"Model has no weights for operator: {op}")

    prediction = dot(weights, features(a, op, b)) * SCALE

    if prediction != prediction:
        raise ValueError("prediction is nan; retrain math_approx_skill")

    return normalize_number(prediction)


def teach(input_data, expected_output):
    """Teach the module from a labeled example."""
    ensure_train_file()

    normalized_input = str(input_data).strip()
    normalized_output = str(expected_output).strip()

    rows = training_examples()
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
    """Forget a previously learned example."""
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


def export_data():
    """Export the module state as a serializable payload."""
    return {
        "id": SKILL_ID,
        "version": SKILL_VERSION,
        "contract_version": CONTRACT_VERSION,
        "model": MODEL,
        "examples": training_examples()
    }


def import_data(data):
    """Import the module state from a payload."""
    rows = data.get("examples", [])
    model = data.get("model", {})

    os.makedirs(CONFIG["model_dir"], exist_ok=True)

    with open(train_path(), "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["input", "output"])
        writer.writeheader()

        for row in rows:
            writer.writerow({
                "input": row["input"],
                "output": row["output"]
            })

    if model:
        with open(model_path(), "w") as file:
            json.dump(model, file, indent=2, sort_keys=True)
        load_model()
    else:
        train()
