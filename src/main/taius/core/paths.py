import os

from __classpath__ import classpath  # noqa: E402

APP_NAME = "taius"

RESOURCE_DIR = classpath.resource_dir
MODEL_DIR = os.path.join(RESOURCE_DIR, "model")
CORE_DIR = os.path.join(MODEL_DIR, "core")
SKILLS_MODEL_DIR = os.path.join(MODEL_DIR, "skills")
SNAPSHOT_BACKUP_DIR = os.path.join(MODEL_DIR, "backups")
SKILLS_SOURCE_DIR = os.path.join(classpath.source_path, "taius", "skills")

CORE_LOG_PATH = os.path.join(CORE_DIR, "training.log")
SKILLS_HASH_PATH = os.path.join(CORE_DIR, "skills.hash")

ROUTER_MODEL_PATH = os.path.join(CORE_DIR, "router.json")
ROUTER_TRAIN_PATH = os.path.join(CORE_DIR, "router.csv")


def ensure_layout():
    os.makedirs(CORE_DIR, exist_ok=True)
    os.makedirs(SKILLS_MODEL_DIR, exist_ok=True)
    os.makedirs(SNAPSHOT_BACKUP_DIR, exist_ok=True)
    os.makedirs(SKILLS_SOURCE_DIR, exist_ok=True)
