"""Module for snapshots."""
import os
import time

from rich.table import Table


def print_snapshot_list(console, SNAPSHOT_BACKUP_DIR):
    """Render the snapshot list."""
    if not os.path.isdir(SNAPSHOT_BACKUP_DIR):
        console.print("[yellow]No snapshots found.[/yellow]")
        return

    snapshots = [
        name
        for name in sorted(os.listdir(SNAPSHOT_BACKUP_DIR), reverse=True)
        if os.path.isdir(os.path.join(SNAPSHOT_BACKUP_DIR, name))
    ]

    if not snapshots:
        console.print("[yellow]No snapshots found.[/yellow]")
        return

    table = Table(title="Backup Snapshots")
    table.add_column("Snapshot")
    table.add_column("Path")

    for snapshot in snapshots:
        table.add_row(
            snapshot,
            os.path.join(SNAPSHOT_BACKUP_DIR, snapshot)
        )

    console.print(table)


def backup_all_snapshot(skills, SNAPSHOT_BACKUP_DIR, CORE_DIR, export_router, export_skill):
    """Create a snapshot backup of the router and skills."""
    import json

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    snapshot_dir = os.path.join(SNAPSHOT_BACKUP_DIR, timestamp)
    core_snapshot_dir = os.path.join(snapshot_dir, "core")
    skills_snapshot_dir = os.path.join(snapshot_dir, "skills")

    os.makedirs(core_snapshot_dir, exist_ok=True)
    os.makedirs(skills_snapshot_dir, exist_ok=True)

    exported = []

    router_export = export_router()
    router_target = os.path.join(core_snapshot_dir, "router.export.json")

    with open(router_export, "r") as source:
        router_data = json.load(source)

    with open(router_target, "w") as target:
        json.dump(router_data, target, indent=2, sort_keys=True)

    exported.append(router_target)

    for skill in skills:
        module = skill["module"]

        if not hasattr(module, "export_data"):
            continue

        skill_export = export_skill(skill["name"], skills)
        skill_target_dir = os.path.join(skills_snapshot_dir, skill["name"])
        skill_target = os.path.join(skill_target_dir, "export.json")

        os.makedirs(skill_target_dir, exist_ok=True)

        with open(skill_export, "r") as source:
            skill_data = json.load(source)

        with open(skill_target, "w") as target:
            json.dump(skill_data, target, indent=2, sort_keys=True)

        exported.append(skill_target)

    return snapshot_dir, exported


def restore_all_snapshot(snapshot_name, skills, SNAPSHOT_BACKUP_DIR, CORE_DIR, SKILLS_MODEL_DIR, import_router, import_skill, find_skill_by_name):
    """Restore router and skill data from a snapshot."""
    import json

    safe_name = snapshot_name.strip()

    if not safe_name:
        raise ValueError("snapshot name is required")

    if "/" in safe_name or "\\" in safe_name or safe_name.startswith("."):
        raise ValueError("invalid snapshot name")

    snapshot_dir = os.path.join(SNAPSHOT_BACKUP_DIR, safe_name)
    core_snapshot = os.path.join(snapshot_dir, "core", "router.export.json")
    skills_snapshot_dir = os.path.join(snapshot_dir, "skills")

    if not os.path.isdir(snapshot_dir):
        raise FileNotFoundError(snapshot_dir)

    restored = []

    if os.path.exists(core_snapshot):
        os.makedirs(CORE_DIR, exist_ok=True)

        with open(core_snapshot, "r") as source:
            router_data = json.load(source)

        router_export_path = os.path.join(CORE_DIR, "router.export.json")

        with open(router_export_path, "w") as target:
            json.dump(router_data, target, indent=2, sort_keys=True)

        import_router()
        restored.append(router_export_path)

    if os.path.isdir(skills_snapshot_dir):
        for skill_dir in sorted(os.listdir(skills_snapshot_dir)):
            skill_export = os.path.join(skills_snapshot_dir, skill_dir, "export.json")

            if not os.path.exists(skill_export):
                continue

            target_model_dir = os.path.join(SKILLS_MODEL_DIR, skill_dir)
            target_export = os.path.join(target_model_dir, "export.json")

            os.makedirs(target_model_dir, exist_ok=True)

            with open(skill_export, "r") as source:
                skill_data = json.load(source)

            with open(target_export, "w") as target:
                json.dump(skill_data, target, indent=2, sort_keys=True)

            target_skill = find_skill_by_name(skill_dir, skills)

            if target_skill is not None:
                import_skill(skill_dir, skills)

            restored.append(target_export)

    return snapshot_dir, restored
