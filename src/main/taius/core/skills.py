import importlib.util
import os

from rich.table import Table

from taius.core.paths import SKILLS_MODEL_DIR, SKILLS_SOURCE_DIR, ensure_layout


def discover_skill_sources():
    ensure_layout()

    skills = []

    for entry in sorted(os.listdir(SKILLS_SOURCE_DIR)):
        skill_dir = os.path.join(SKILLS_SOURCE_DIR, entry)
        skill_file = os.path.join(skill_dir, "skill.py")

        if not os.path.isdir(skill_dir):
            continue

        if not os.path.exists(skill_file):
            continue

        skills.append(
            {
                "name": entry,
                "source_dir": skill_dir,
                "skill_file": skill_file,
                "model_dir": os.path.join(SKILLS_MODEL_DIR, entry)
            }
        )

    return skills


def is_skill_disabled(skill):
    if isinstance(skill, dict):
        skill_name = skill.get("name", "")
    else:
        skill_name = str(skill)

    disabled_path = os.path.join(SKILLS_MODEL_DIR, skill_name, ".disabled")
    return os.path.exists(disabled_path)




def load_skill_module(skill):
    module_name = f"taius_skill_{skill['name']}"
    spec = importlib.util.spec_from_file_location(module_name, skill["skill_file"])

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load skill: {skill['name']}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_skills(console, show_disabled=True):
    loaded = []

    for skill in discover_skill_sources():
        if isinstance(skill, dict) and skill.get("name", "").startswith("_"):
            continue

        if is_skill_disabled(skill):
            if show_disabled:
              skill_name = skill.get("name", str(skill)) if isinstance(skill, dict) else str(skill)
              console.print(f"[yellow]Skipping disabled skill:[/yellow] {skill_name}")
            continue

        module = load_skill_module(skill)

        if hasattr(module, "configure"):
            os.makedirs(skill["model_dir"], exist_ok=True)
            module.configure(
                {
                    "name": skill["name"],
                    "source_dir": skill["source_dir"],
                    "model_dir": skill["model_dir"]
                }
            )

        if not hasattr(module, "describe"):
            console.print(f"[yellow]Skipping skill without describe():[/yellow] {skill['name']}")
            continue

        description = module.describe()

        loaded.append(
            {
                "name": skill["name"],
                "source_dir": skill["source_dir"],
                "model_dir": skill["model_dir"],
                "module": module,
                "description": description
            }
        )

    return loaded


def print_skills_table(console, skills, title):
    table = Table(title=title)
    table.add_column("Skill")
    table.add_column("ID")
    table.add_column("Version")
    table.add_column("Input")
    table.add_column("Output")
    table.add_column("Model Dir")

    for skill in skills:
        description = skill["description"]

        table.add_row(
            skill["name"],
            str(description.get("id", "")),
            str(description.get("version", "")),
            str(description.get("input_type", "")),
            str(description.get("output_type", "")),
            skill["model_dir"]
        )

    console.print(table)
