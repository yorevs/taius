"""Module for validation."""
import os


SUPPORTED_SKILL_CONTRACT_VERSION = "1.0"

REQUIRED_SKILL_FUNCTIONS = [
    "describe",
    "configure",
    "can_handle",
    "can_train",
    "needs_training",
    "train",
    "predict",
    "teach",
    "forget",
    "training_examples",
    "export_data",
    "import_data"
]


def validate_skill_contract(skill):
    """Validate a loaded skill module against the contract."""
    issues = []
    module = skill["module"]

    for function_name in REQUIRED_SKILL_FUNCTIONS:
        if not hasattr(module, function_name):
            issues.append(f"missing function: {function_name}")
            continue

        if not callable(getattr(module, function_name)):
            issues.append(f"not callable: {function_name}")

    if hasattr(module, "describe"):
        try:
            description = module.describe()

            if not isinstance(description, dict):
                issues.append("describe() must return dict")
            else:
                for field in ["id", "version", "contract_version", "input_type", "output_type"]:
                    if not description.get(field):
                        issues.append(f"describe() missing field: {field}")

                contract_version = description.get("contract_version")

                if contract_version and contract_version != SUPPORTED_SKILL_CONTRACT_VERSION:
                    issues.append(
                        "unsupported contract_version: "
                        f"{contract_version} "
                        f"(supported: {SUPPORTED_SKILL_CONTRACT_VERSION})"
                    )
        except Exception as error:
            issues.append(f"describe() failed: {error}")

    for path_key in ["source_dir", "model_dir"]:
        path_value = skill.get(path_key)

        if not path_value:
            issues.append(f"missing skill metadata: {path_key}")
            continue

        if not os.path.exists(path_value):
            issues.append(f"path does not exist: {path_key}={path_value}")

    if hasattr(module, "can_train"):
        try:
            can_train = module.can_train()

            if can_train:
                for function_name in ["needs_training", "train"]:
                    if not hasattr(module, function_name):
                        issues.append(f"trainable skill missing: {function_name}")
        except Exception as error:
            issues.append(f"can_train() failed: {error}")

    return issues


def validate_skill_name(skill_name):
    """Validate and normalize a skill name."""
    safe_name = skill_name.strip()

    if not safe_name:
        raise ValueError("skill name is required")

    if safe_name.startswith("_"):
        raise ValueError("skill name cannot start with '_'")

    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
    invalid = sorted({character for character in safe_name if character not in allowed})

    if invalid:
        raise ValueError(f"skill name has invalid character(s): {''.join(invalid)}")

    return safe_name
