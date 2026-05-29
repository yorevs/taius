"""Module for router."""
import csv
import json
import math
import os

from taius.core.paths import (
    CORE_DIR,
    ROUTER_MODEL_PATH,
    ROUTER_TRAIN_PATH,
    SKILLS_HASH_PATH,
)
from taius.core.text import tokenize


def calculate_skills_hash(skills):
  """Compute a hash for the loaded skills."""
  import hashlib

  digest = hashlib.sha256()

  for skill in skills:
    description = skill["description"]

    digest.update(str(skill["name"]).encode())
    digest.update(str(description.get("id", "")).encode())
    digest.update(str(description.get("version", "")).encode())
    digest.update(str(description.get("input_type", "")).encode())
    digest.update(str(description.get("output_type", "")).encode())

  return digest.hexdigest()


def read_saved_skills_hash():
  """Read the persisted skills hash."""
  if not os.path.exists(SKILLS_HASH_PATH):
    return ""

  with open(SKILLS_HASH_PATH, "r") as file:
    return file.read().strip()


def save_skills_hash(skills_hash):
  """Persist the skills hash to disk."""
  os.makedirs(CORE_DIR, exist_ok=True)

  with open(SKILLS_HASH_PATH, "w") as file:
    file.write(skills_hash)


def skills_changed(skills):
  """Return whether the loaded skills changed."""
  return calculate_skills_hash(skills) != read_saved_skills_hash()


def update_skills_hash(skills):
  """Update the persisted skills hash."""
  save_skills_hash(calculate_skills_hash(skills))


def build_router_training_file(skills):
  """Write router training examples to CSV."""
  os.makedirs(CORE_DIR, exist_ok=True)

  with open(ROUTER_TRAIN_PATH, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["input", "skill_name"])

    for skill in skills:
      description = skill["description"]
      examples = description.get("examples", [])

      for example in examples:
        writer.writerow([example, skill["name"]])


def train_router_from_existing_file():
  """Train the router model from the existing CSV file."""
  label_counts = {}
  word_counts = {}
  vocabulary = set()

  with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
      label = row["skill_name"]
      tokens = tokenize(row["input"])

      label_counts[label] = label_counts.get(label, 0) + 1
      word_counts.setdefault(label, {})

      for token in tokens:
        vocabulary.add(token)
        word_counts[label][token] = word_counts[label].get(token, 0) + 1

  model = {
    "labels": label_counts,
    "vocabulary": sorted(vocabulary),
    "word_counts": word_counts
  }

  with open(ROUTER_MODEL_PATH, "w") as file:
    json.dump(model, file, indent=2, sort_keys=True)


def train_router(skills):
  """Build the router training data and retrain the model."""
  build_router_training_file(skills)
  train_router_from_existing_file()


def router_needs_training(skills):
  """Return whether the router model needs retraining."""
  return not os.path.exists(ROUTER_MODEL_PATH) or skills_changed(skills)


def load_router_model():
  """Load the persisted router model."""
  with open(ROUTER_MODEL_PATH, "r") as file:
    return json.load(file)


def predict_skill(input_data, skills):
  """Execute predict skill."""
  if not os.path.exists(ROUTER_MODEL_PATH):
    return None

  model = load_router_model()
  tokens = tokenize(input_data)

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

  if not scores:
    return None

  selected_name = max(scores, key=scores.get)

  for skill in skills:
    if skill["name"] == selected_name:
      return skill

  return None


def teach_router(input_data, skill_name, skills):
  """Teach the router with a new labeled example."""
  valid_names = {skill["name"] for skill in skills}

  if skill_name not in valid_names:
    raise ValueError(f"Unknown skill: {skill_name}")

  file_exists = os.path.exists(ROUTER_TRAIN_PATH)

  with open(ROUTER_TRAIN_PATH, "a", newline="") as file:
    writer = csv.writer(file)

    if not file_exists:
      writer.writerow(["input", "skill_name"])

    writer.writerow([input_data, skill_name])

  train_router_from_existing_file()


def forget_router(input_data):
  """Remove a router training example."""
  if not os.path.exists(ROUTER_TRAIN_PATH):
    return

  kept_rows = []

  with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
      if row["input"].strip() == input_data.strip():
        continue

      kept_rows.append(row)

  with open(ROUTER_TRAIN_PATH, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["input", "skill_name"])
    writer.writeheader()
    writer.writerows(kept_rows)

  train_router_from_existing_file()


def router_examples():
  """Return the stored router training examples."""
  if not os.path.exists(ROUTER_TRAIN_PATH):
    return []

  with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
    return list(csv.DictReader(file))


def export_router():
  """Export router data to a snapshot file."""
  export_path = os.path.join(CORE_DIR, "router.export.json")

  data = {
    "router_train_path": ROUTER_TRAIN_PATH,
    "router_model_path": ROUTER_MODEL_PATH,
    "training_examples": router_examples()
  }

  with open(export_path, "w") as file:
    json.dump(data, file, indent=2, sort_keys=True)

  return export_path


def import_router():
  """Import router data from a snapshot file."""
  import_path = os.path.join(CORE_DIR, "router.export.json")

  if not os.path.exists(import_path):
    raise FileNotFoundError(import_path)

  with open(import_path, "r") as file:
    data = json.load(file)

  examples = data.get("training_examples", [])

  with open(ROUTER_TRAIN_PATH, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["input", "skill_name"])
    writer.writeheader()

    for row in examples:
      writer.writerow(
        {
          "input": row["input"],
          "skill_name": row["skill_name"]
        }
      )

  train_router_from_existing_file()

  return import_path
