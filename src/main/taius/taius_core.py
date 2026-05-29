import csv
import hashlib
import os
import re

from rich.console import Console
from rich.table import Table

from taius.core.commands import handle_command, is_command
from taius.core.log_views import print_tail_log as print_taius_tail_log
from taius.core.paths import APP_NAME, CORE_DIR, CORE_LOG_PATH, ROUTER_MODEL_PATH, ROUTER_TRAIN_PATH, SKILLS_HASH_PATH, \
    SKILLS_MODEL_DIR, SKILLS_SOURCE_DIR, SNAPSHOT_BACKUP_DIR, ensure_layout as ensure_taius_layout
from taius.core.router_runtime import get_routing_threshold as taius_get_routing_threshold, \
    load_router_config as taius_load_router_config, load_router_model as taius_load_router_model, \
    predict_skill_with_router as taius_predict_skill_with_router, route_to_skill as taius_route_to_skill, \
    save_router_config as taius_save_router_config
from taius.core.router_stats import print_router_stats as print_taius_router_stats
from taius.core.runtime import run_taius_loop as run_taius_runtime_loop
from taius.core.skill_management import create_new_skill as taius_create_new_skill, delete_skill as taius_delete_skill, \
    disable_skill as taius_disable_skill, enable_skill as taius_enable_skill, \
    find_skill_by_name as taius_find_skill_by_name, log_skill_event as taius_log_skill_event, \
    rename_skill as taius_rename_skill
from taius.core.skill_views import print_skill_log as print_taius_skill_log, \
    print_skill_stats as print_taius_skill_stats
from taius.core.skills import load_skills as load_taius_skills, print_skills_table
from taius.core.snapshots import backup_all_snapshot as taius_backup_all_snapshot, \
    print_snapshot_list as print_taius_snapshot_list, restore_all_snapshot as taius_restore_all_snapshot
from taius.core.status import print_status as print_taius_status
from taius.core.training_monitor import TrainingLogMonitor
from taius.core.validation import validate_skill_contract, validate_skill_name

console = Console()


ROUTER_CONFIG_PATH = os.path.join(CORE_DIR, "router.config.json")
DEFAULT_ROUTING_THRESHOLD = 0.60


def load_skills(show_disabled=True):
    return load_taius_skills(console, show_disabled=show_disabled)


def print_discovered_skills():
    skills = load_skills()
    print_skills_table(console, skills, "Discovered Taius Skills")


def tokenize_router_text(text):
    return re.findall(r"[a-zA-Z0-9_+\-*/']+", str(text).lower())


def build_router_training_file(skills):
    os.makedirs(CORE_DIR, exist_ok=True)

    with open(ROUTER_TRAIN_PATH, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["input", "skill_name"])

        for skill in skills:
            description = skill["description"]
            examples = description.get("examples", [])

            for example in examples:
                writer.writerow([example, skill["name"]])


def train_router(skills):
    build_router_training_file(skills)

    label_counts = {}
    word_counts = {}
    vocabulary = set()

    with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            label = row["skill_name"]
            tokens = tokenize_router_text(row["input"])

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
        import json
        json.dump(model, file, indent=2, sort_keys=True)

    console.print(f"[green]Router trained:[/green] {ROUTER_MODEL_PATH}")


def router_needs_training():
    return not os.path.exists(ROUTER_MODEL_PATH) or skills_changed()


def load_router_config():
    return taius_load_router_config(ROUTER_CONFIG_PATH, CORE_DIR)


def save_router_config(config):
    return taius_save_router_config(config, ROUTER_CONFIG_PATH, CORE_DIR)


def get_routing_threshold():
    return taius_get_routing_threshold(ROUTER_CONFIG_PATH, CORE_DIR)


def load_router_model():
    return taius_load_router_model(ROUTER_MODEL_PATH)


def predict_skill_with_router(input_data: str, skills):
    return taius_predict_skill_with_router(
        input_data,
        skills,
        ROUTER_MODEL_PATH,
        tokenize_router_text
    )


def route_to_skill(input_data: str, skills):
    return taius_route_to_skill(
        input_data,
        skills,
        ROUTER_MODEL_PATH,
        tokenize_router_text,
        get_routing_threshold
    )


def teach_router(input_data: str, skill_name: str, skills):
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


def train_router_from_existing_file():
    label_counts = {}
    word_counts = {}
    vocabulary = set()

    with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            label = row["skill_name"]
            tokens = tokenize_router_text(row["input"])

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
        import json
        json.dump(model, file, indent=2, sort_keys=True)

    console.print(f"[green]Router updated:[/green] {ROUTER_MODEL_PATH}")


def forget_router(input_data: str):
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


def train_skill_with_monitor(skill):
    module = skill["module"]
    log_path = os.path.join(skill["model_dir"], "training.log")

    monitor = TrainingLogMonitor(
        console=console,
        log_path=log_path,
        title=f"Training skill: {skill['name']}"
    )

    monitor.start()

    try:
        module.train()
    finally:
        monitor.stop()


def train_router_if_needed(skills):
    if not router_needs_training():
        return

    console.rule("[bold yellow]Training core router")
    train_router(skills)
    update_skills_hash()


def calculate_skills_hash():
    digest = hashlib.sha256()

    for skill in load_skills(show_disabled=False):
        description = skill["description"]

        digest.update(str(skill["name"]).encode())
        digest.update(str(description.get("id", "")).encode())
        digest.update(str(description.get("version", "")).encode())
        digest.update(str(description.get("input_type", "")).encode())
        digest.update(str(description.get("output_type", "")).encode())

    return digest.hexdigest()


def read_saved_skills_hash():
    if not os.path.exists(SKILLS_HASH_PATH):
        return ""

    with open(SKILLS_HASH_PATH, "r") as file:
        return file.read().strip()


def save_skills_hash(skills_hash):
    os.makedirs(CORE_DIR, exist_ok=True)

    with open(SKILLS_HASH_PATH, "w") as file:
        file.write(skills_hash)


def skills_changed():
    current_hash = calculate_skills_hash()
    saved_hash = read_saved_skills_hash()

    return current_hash != saved_hash


def update_skills_hash():
    save_skills_hash(calculate_skills_hash())


def detect_skill_changes():
    if not skills_changed():
        return False

    console.print("[yellow]Skill registry changed.[/yellow]")
    update_skills_hash()

    return True


def configure_skill(skill):
    module = skill["module"]

    os.makedirs(skill["model_dir"], exist_ok=True)

    if hasattr(module, "configure"):
        module.configure(
            {
                "name": skill["name"],
                "source_dir": skill["source_dir"],
                "model_dir": skill["model_dir"]
            }
        )


def train_skills_if_needed():
    skills = load_skills()

    for skill in skills:
        module = skill["module"]
        configure_skill(skill)

        if not hasattr(module, "can_train"):
            continue

        if not module.can_train():
            continue

        if not hasattr(module, "needs_training"):
            console.print(f"[yellow]Skipping trainable skill without needs_training():[/yellow] {skill['name']}")
            continue

        if not module.needs_training():
            continue

        if not hasattr(module, "train"):
            console.print(f"[yellow]Skipping trainable skill without train():[/yellow] {skill['name']}")
            continue

        console.rule(f"[bold yellow]Training skill: {skill['name']}")
        log_skill_event(skill, "auto-training started")
        train_skill_with_monitor(skill)
        log_skill_event(skill, "auto-training finished")

def print_router_examples():
    if not os.path.exists(ROUTER_TRAIN_PATH):
        console.print("[yellow]No router examples found.[/yellow]")
        return

    table = Table(title="Router Training Examples")
    table.add_column("Input")
    table.add_column("Skill")

    with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            table.add_row(row["input"], row["skill_name"])

    console.print(table)


def print_skill_examples(skill_name: str, skills):
    target_skill = None

    for skill in skills:
        if skill["name"] == skill_name:
            target_skill = skill
            break

    if target_skill is None:
        console.print(f"[red]Unknown skill:[/red] {skill_name}")
        return

    module = target_skill["module"]

    if not hasattr(module, "training_examples"):
        console.print(f"[yellow]Skill has no training_examples():[/yellow] {skill_name}")
        return

    rows = module.training_examples()

    table = Table(title=f"Training Examples: {skill_name}")

    if not rows:
        console.print("[yellow]No examples found.[/yellow]")
        return

    for column in rows[0].keys():
        table.add_column(str(column))

    for row in rows:
        table.add_row(*(str(value) for value in row.values()))

    console.print(table)


def export_skill(skill_name: str, skills):
    target_skill = None

    for skill in skills:
        if skill["name"] == skill_name:
            target_skill = skill
            break

    if target_skill is None:
        raise ValueError(f"Unknown skill: {skill_name}")

    module = target_skill["module"]

    if not hasattr(module, "export_data"):
        raise ValueError(f"Skill has no export_data(): {skill_name}")

    export_path = os.path.join(target_skill["model_dir"], "export.json")
    data = module.export_data()

    with open(export_path, "w") as file:
        import json
        json.dump(data, file, indent=2, sort_keys=True)

    return export_path


def import_skill(skill_name: str, skills):
    target_skill = None

    for skill in skills:
        if skill["name"] == skill_name:
            target_skill = skill
            break

    if target_skill is None:
        raise ValueError(f"Unknown skill: {skill_name}")

    module = target_skill["module"]

    if not hasattr(module, "import_data"):
        raise ValueError(f"Skill has no import_data(): {skill_name}")

    import_path = os.path.join(target_skill["model_dir"], "export.json")

    if not os.path.exists(import_path):
        raise FileNotFoundError(import_path)

    with open(import_path, "r") as file:
        import json
        data = json.load(file)

    module.import_data(data)

    return import_path


def print_snapshot_list():
    print_taius_snapshot_list(
        console,
        SNAPSHOT_BACKUP_DIR
    )


def backup_all_snapshot(skills):
    return taius_backup_all_snapshot(
        skills,
        SNAPSHOT_BACKUP_DIR,
        CORE_DIR,
        export_router,
        export_skill
    )


def restore_all_snapshot(snapshot_name, skills):
    return taius_restore_all_snapshot(
        snapshot_name,
        skills,
        SNAPSHOT_BACKUP_DIR,
        CORE_DIR,
        SKILLS_MODEL_DIR,
        import_router,
        import_skill,
        find_skill_by_name
    )


def restore_all(skills):
    imported = []

    router_import = import_router()
    imported.append(router_import)

    for skill in skills:
        module = skill["module"]

        if not hasattr(module, "import_data"):
            continue

        imported.append(import_skill(skill["name"], skills))

    return imported


def backup_all(skills):
    exported = []

    router_export = export_router()
    exported.append(router_export)

    for skill in skills:
        module = skill["module"]

        if not hasattr(module, "export_data"):
            continue

        exported.append(export_skill(skill["name"], skills))

    return exported


def export_router():
    export_path = os.path.join(CORE_DIR, "router.export.json")

    examples = []

    if os.path.exists(ROUTER_TRAIN_PATH):
        with open(ROUTER_TRAIN_PATH, "r", newline="") as file:
            examples = list(csv.DictReader(file))

    data = {
        "router_train_path": ROUTER_TRAIN_PATH,
        "router_model_path": ROUTER_MODEL_PATH,
        "training_examples": examples
    }

    with open(export_path, "w") as file:
        import json
        json.dump(data, file, indent=2, sort_keys=True)

    return export_path


def import_router():
    import_path = os.path.join(CORE_DIR, "router.export.json")

    if not os.path.exists(import_path):
        raise FileNotFoundError(import_path)

    with open(import_path, "r") as file:
        import json
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


def print_version_info(skills):
    version_path = os.path.join(CORE_DIR, "version.txt")

    runtime_version = "unknown"

    if os.path.exists(version_path):
        with open(version_path, "r") as file:
            runtime_version = file.read().strip()

    table = Table(title="Taius Version")
    table.add_column("Component")
    table.add_column("ID")
    table.add_column("Version")

    table.add_row("runtime", "taius", runtime_version)

    for skill in skills:
        description = skill["description"]

        table.add_row(
            skill["name"],
            str(description.get("id", "")),
            str(description.get("version", ""))
        )

    console.print(table)


def print_help():
    console.print("[bold]Taius commands[/bold]")
    console.print("/help")
    console.print("/version")
    console.print("/status")
    console.print("/doctor")
    console.print("/skills")
    console.print("/reload")
    console.print("/router-examples")
    console.print("/router-stats")
    console.print("/get-routing-threshold")
    console.print("/set-routing-threshold <value>")
    console.print("/export-router")
    console.print("/import-router")
    console.print("/backup-all")
    console.print("/backup-all --snapshot")
    console.print("/list-snapshots")
    console.print("/restore-all")
    console.print("/restore-all <snapshot>")
    console.print("/skill-examples <skill_name>")
    console.print("/skill-stats <skill_name>")
    console.print("/skill-log <skill_name> \\[lines]")
    console.print("/tail-log \\[lines]")
    console.print("/validate-skill <skill_name>")
    console.print("/disable-skill <skill_name>")
    console.print("/enable-skill <skill_name>")
    console.print("/new-skill <skill_name>")
    console.print("/delete-skill <skill_name>")
    console.print("/rename-skill <old_name> <new_name>")
    console.print("/export-skill <skill_name>")
    console.print("/import-skill <skill_name>")
    console.print("/teach-router <skill_name> :: <input text>")
    console.print("/forget-router <input text>")
    console.print("/teach-skill <skill_name> :: <input text> => <expected output>")
    console.print("/forget-skill <skill_name> :: <input text>")
    console.print("/quit")
    console.print("/exit")
    console.print("")
    console.print("[bold]Examples[/bold]")
    console.print("echo hello")
    console.print("sentiment I love this")
    console.print("/set-routing-threshold 0.68")
    console.print("/skill-stats sentiment_skill")
    console.print("/skill-log sentiment_skill 20")
    console.print("/tail-log 20")
    console.print("/backup-all --snapshot")
    console.print("/list-snapshots")
    console.print("/restore-all 20260528-221904")
    console.print("/new-skill demo_skill")
    console.print("/delete-skill demo_skill")
    console.print("/rename-skill demo_skill renamed_skill")
    console.print("/validate-skill echo_skill")
    console.print("/teach-router sentiment_skill :: this movie rocks")
    console.print("/teach-skill sentiment_skill :: this is sick => positive")
    console.print("/forget-skill sentiment_skill :: this is sick")


def print_loaded_skills(skills):
    print_skills_table(console, skills, "Loaded Taius Skills")


def print_validate_skill(skill_name, skills):
    target_skill = None

    for skill in skills:
        if skill["name"] == skill_name:
            target_skill = skill
            break

    if target_skill is None:
        console.print(f"[red]Unknown skill:[/red] {skill_name}")
        return

    issues = validate_skill_contract(target_skill)

    table = Table(title=f"Skill Validation: {skill_name}")
    table.add_column("Item")
    table.add_column("Value")

    table.add_row("skill", target_skill["name"])
    table.add_row("source_dir", target_skill.get("source_dir", ""))
    table.add_row("model_dir", target_skill.get("model_dir", ""))

    description = target_skill.get("description", {})
    table.add_row("id", str(description.get("id", "")))
    table.add_row("version", str(description.get("version", "")))
    table.add_row("contract_version", str(description.get("contract_version", "")))
    table.add_row("input_type", str(description.get("input_type", "")))
    table.add_row("output_type", str(description.get("output_type", "")))
    table.add_row("status", "OK" if not issues else "FAIL")
    table.add_row("issues", "\n".join(issues) if issues else "-")

    console.print(table)

    if issues:
        console.print(f"[red]Skill has {len(issues)} issue(s).[/red]")
        return

    console.print("[green]Skill contract is valid.[/green]")


def print_doctor(skills):
    table = Table(title="Taius Doctor")
    table.add_column("Skill")
    table.add_column("Status")
    table.add_column("Issues")

    total_issues = 0

    for skill in skills:
        issues = validate_skill_contract(skill)
        total_issues += len(issues)

        table.add_row(
            skill["name"],
            "OK" if not issues else "FAIL",
            "\n".join(issues) if issues else "-"
        )

    console.print(table)

    if total_issues:
        console.print(f"[red]Doctor found {total_issues} issue(s).[/red]")
        return

    console.print("[green]Doctor passed. No skill contract issues found.[/green]")


def set_routing_threshold(value):
    threshold = float(value)

    if threshold < 0.0 or threshold > 1.0:
        raise ValueError("routing threshold must be between 0.0 and 1.0")

    config = load_router_config()
    config["routing_threshold"] = threshold
    save_router_config(config)

    return threshold


def print_routing_threshold():
    console.print(f"[cyan]Routing threshold:[/cyan] {get_routing_threshold():.2f}")


def find_skill_by_name(skill_name, skills):
    return taius_find_skill_by_name(skill_name, skills)


def create_new_skill(skill_name):
    return taius_create_new_skill(skill_name, SKILLS_SOURCE_DIR)


def delete_skill(skill_name):
    return taius_delete_skill(
        skill_name,
        SKILLS_SOURCE_DIR,
        SKILLS_MODEL_DIR,
        validate_skill_name
    )


def rename_skill(old_name, new_name):
    return taius_rename_skill(
        old_name,
        new_name,
        SKILLS_SOURCE_DIR,
        SKILLS_MODEL_DIR,
        validate_skill_name
    )


def disable_skill(skill_name, skills):
    return taius_disable_skill(skill_name, skills)


def enable_skill(skill_name):
    return taius_enable_skill(skill_name, SKILLS_MODEL_DIR)


def log_skill_event(skill, message):
    return taius_log_skill_event(skill, message)


def print_tail_log(skills, line_count=20):
    print_taius_tail_log(
        console,
        skills,
        CORE_LOG_PATH,
        line_count
    )


def print_skill_stats(skill_name, skills):
    print_taius_skill_stats(
        console,
        skill_name,
        skills,
        find_skill_by_name,
        validate_skill_contract
    )


def print_skill_log(skill_name, skills, line_count=20):
    print_taius_skill_log(
        console,
        skill_name,
        skills,
        find_skill_by_name,
        line_count
    )


def print_router_stats():
    print_taius_router_stats(
        console,
        ROUTER_MODEL_PATH,
        ROUTER_TRAIN_PATH,
        ROUTER_CONFIG_PATH,
        get_routing_threshold
    )


def print_status(skills):
    print_taius_status(
        console,
        skills,
        APP_NAME,
        CORE_DIR,
        ROUTER_MODEL_PATH,
        ROUTER_TRAIN_PATH,
        SKILLS_MODEL_DIR,
        SKILLS_SOURCE_DIR,
        ROUTER_CONFIG_PATH,
        get_routing_threshold,
        skills_changed
    )


def build_command_context(skills):
    return {
        "console": console,
        "skills": skills,
        "print_help": print_help,
        "print_version_info": print_version_info,
        "print_status": print_status,
        "print_routing_threshold": print_routing_threshold,
        "set_routing_threshold": set_routing_threshold,
        "print_router_stats": print_router_stats,
        "print_skill_stats": print_skill_stats,
        "print_skill_log": print_skill_log,
        "print_tail_log": print_tail_log,
        "print_doctor": print_doctor,
        "print_validate_skill": print_validate_skill,
        "disable_skill": disable_skill,
        "enable_skill": enable_skill,
        "create_new_skill": create_new_skill,
        "delete_skill": delete_skill,
        "rename_skill": rename_skill,
        "print_snapshot_list": print_snapshot_list,
        "print_loaded_skills": print_loaded_skills,
        "reload_skills": reload_skills,
        "print_router_examples": print_router_examples,
        "print_skill_examples": print_skill_examples,
        "export_router": export_router,
        "import_router": import_router,
        "backup_all": backup_all,
        "backup_all_snapshot": backup_all_snapshot,
        "restore_all": restore_all,
        "restore_all_snapshot": restore_all_snapshot,
        "export_skill": export_skill,
        "import_skill": import_skill,
        "log_skill_event": log_skill_event,
        "teach_router": teach_router,
        "forget_router": forget_router
    }


def reload_skills():
    skills = load_skills()
    print_loaded_skills(skills)
    detect_skill_changes()
    train_skills_if_needed()
    train_router_if_needed(skills)

    return skills


def run_taius_loop():
    run_taius_runtime_loop(
        console,
        load_skills,
        train_router_if_needed,
        is_command,
        handle_command,
        route_to_skill,
        get_routing_threshold,
        teach_router,
        forget_router,
        build_command_context
    )


def setup():
    ensure_taius_layout()
    print_discovered_skills()
    detect_skill_changes()
    train_skills_if_needed()
    run_taius_loop()
