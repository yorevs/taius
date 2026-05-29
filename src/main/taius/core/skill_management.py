import os
import shutil
import time


def find_skill_by_name(skill_name, skills):
    for skill in skills:
        if skill["name"] == skill_name:
            return skill

    return None


def create_new_skill(skill_name, skills_source_dir):
    safe_name = skill_name.strip()

    if not safe_name:
        raise ValueError("skill name is required")

    if safe_name.startswith("_"):
        raise ValueError("skill name cannot start with '_'")

    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
    invalid = sorted({character for character in safe_name if character not in allowed})

    if invalid:
        raise ValueError(f"skill name has invalid character(s): {''.join(invalid)}")

    target_dir = os.path.join(skills_source_dir, safe_name)
    target_path = os.path.join(target_dir, "skill.py")
    template_path = os.path.join(skills_source_dir, "_template", "skill.py")

    if os.path.exists(target_path):
        raise FileExistsError(target_path)

    if not os.path.exists(template_path):
        raise FileNotFoundError(template_path)

    os.makedirs(target_dir, exist_ok=True)

    with open(template_path, "r") as file:
        content = file.read()

    skill_id = safe_name.replace("_", ".")
    content = content.replace('"template.skill"', f'"{skill_id}"', 1)

    with open(target_path, "w") as file:
        file.write(content)

    return target_path


def delete_skill(skill_name, skills_source_dir, skills_model_dir, validate_skill_name):
    safe_name = skill_name.strip()

    if not safe_name:
        raise ValueError("skill name is required")

    if safe_name.startswith("_"):
        raise ValueError("refusing to delete reserved skill directory")

    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
    invalid = sorted({character for character in safe_name if character not in allowed})

    if invalid:
        raise ValueError(f"skill name has invalid character(s): {''.join(invalid)}")

    source_dir = os.path.join(skills_source_dir, safe_name)
    model_dir = os.path.join(skills_model_dir, safe_name)

    if not os.path.exists(source_dir):
        raise FileNotFoundError(source_dir)

    removed = []

    if os.path.exists(source_dir):
        shutil.rmtree(source_dir)
        removed.append(source_dir)

    if os.path.exists(model_dir):
        shutil.rmtree(model_dir)
        removed.append(model_dir)

    return removed


def rename_skill(old_name, new_name, skills_source_dir, skills_model_dir, validate_skill_name):
    old_safe_name = validate_skill_name(old_name)
    new_safe_name = validate_skill_name(new_name)

    old_source_dir = os.path.join(skills_source_dir, old_safe_name)
    new_source_dir = os.path.join(skills_source_dir, new_safe_name)
    old_model_dir = os.path.join(skills_model_dir, old_safe_name)
    new_model_dir = os.path.join(skills_model_dir, new_safe_name)

    if not os.path.exists(old_source_dir):
        raise FileNotFoundError(old_source_dir)

    if os.path.exists(new_source_dir):
        raise FileExistsError(new_source_dir)

    if os.path.exists(new_model_dir):
        raise FileExistsError(new_model_dir)

    os.rename(old_source_dir, new_source_dir)

    if os.path.exists(old_model_dir):
        os.rename(old_model_dir, new_model_dir)

    skill_path = os.path.join(new_source_dir, "skill.py")

    if os.path.exists(skill_path):
        with open(skill_path, "r") as file:
            content = file.read()

        old_id = old_safe_name.replace("_", ".")
        new_id = new_safe_name.replace("_", ".")
        content = content.replace(f'"{old_id}"', f'"{new_id}"', 1)

        with open(skill_path, "w") as file:
            file.write(content)

    return {
        "source_dir": new_source_dir,
        "model_dir": new_model_dir
    }


def disable_skill(skill_name, skills):
    target_skill = find_skill_by_name(skill_name, skills)

    if target_skill is None:
        raise ValueError(f"Unknown loaded skill: {skill_name}")

    disabled_path = os.path.join(target_skill["model_dir"], ".disabled")
    os.makedirs(target_skill["model_dir"], exist_ok=True)

    with open(disabled_path, "w") as file:
        file.write("disabled\n")

    return disabled_path


def enable_skill(skill_name, skills_model_dir):
    disabled_path = os.path.join(skills_model_dir, skill_name, ".disabled")

    if not os.path.exists(disabled_path):
        return disabled_path

    os.remove(disabled_path)
    return disabled_path


def log_skill_event(skill, message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(skill["model_dir"], "training.log")

    os.makedirs(skill["model_dir"], exist_ok=True)

    with open(log_path, "a") as file:
        file.write(f"[{timestamp}] {message}\n")

    return log_path
