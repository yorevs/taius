import os

from rich.table import Table


def print_skill_stats(console, skill_name, skills, find_skill_by_name, validate_skill_contract):
    target_skill = find_skill_by_name(skill_name, skills)

    if target_skill is None:
        console.print(f"[red]Unknown loaded skill:[/red] {skill_name}")
        return

    module = target_skill["module"]
    description = target_skill.get("description", {})
    issues = validate_skill_contract(target_skill)
    disabled_path = os.path.join(target_skill["model_dir"], ".disabled")

    table = Table(title=f"Skill Stats: {skill_name}")
    table.add_column("Item")
    table.add_column("Value")

    table.add_row("name", target_skill["name"])
    table.add_row("id", str(description.get("id", "")))
    table.add_row("version", str(description.get("version", "")))
    table.add_row("contract_version", str(description.get("contract_version", "")))
    table.add_row("input_type", str(description.get("input_type", "")))
    table.add_row("output_type", str(description.get("output_type", "")))
    table.add_row("source_dir", target_skill.get("source_dir", ""))
    table.add_row("model_dir", target_skill.get("model_dir", ""))
    table.add_row("disabled", "yes" if os.path.exists(disabled_path) else "no")
    table.add_row("contract_status", "OK" if not issues else "FAIL")
    table.add_row("contract_issues", "\n".join(issues) if issues else "-")

    if hasattr(module, "can_train"):
        try:
            table.add_row("can_train", "yes" if module.can_train() else "no")
        except Exception as error:
            table.add_row("can_train", f"error: {error}")
    else:
        table.add_row("can_train", "unknown")

    if hasattr(module, "needs_training"):
        try:
            table.add_row("needs_training", "yes" if module.needs_training() else "no")
        except Exception as error:
            table.add_row("needs_training", f"error: {error}")
    else:
        table.add_row("needs_training", "unknown")

    if hasattr(module, "training_examples"):
        try:
            examples = module.training_examples()
            table.add_row("training_examples", str(len(examples)))
        except Exception as error:
            table.add_row("training_examples", f"error: {error}")
    else:
        table.add_row("training_examples", "unknown")

    console.print(table)


def print_skill_log(console, skill_name, skills, find_skill_by_name, line_count=20):
    target_skill = find_skill_by_name(skill_name, skills)

    if target_skill is None:
        console.print(f"[red]Unknown loaded skill:[/red] {skill_name}")
        return

    try:
        line_count = int(line_count)
    except ValueError:
        console.print("[red]Line count must be an integer.[/red]")
        return

    if line_count <= 0:
        console.print("[red]Line count must be greater than zero.[/red]")
        return

    log_path = os.path.join(target_skill["model_dir"], "training.log")

    if not os.path.exists(log_path):
        console.print(f"[yellow]No skill log found:[/yellow] {log_path}")
        return

    with open(log_path, "r") as file:
        lines = file.readlines()

    selected_lines = lines[-line_count:]

    table = Table(title=f"Skill Log: {skill_name}")
    table.add_column("Line")
    table.add_column("Message")

    start_line = max(1, len(lines) - len(selected_lines) + 1)

    for index, line in enumerate(selected_lines, start=start_line):
        table.add_row(str(index), line.rstrip())

    console.print(table)
