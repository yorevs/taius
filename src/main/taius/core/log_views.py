import os

from rich.table import Table


def print_tail_log(console, skills, core_log_path, line_count=20):
    try:
        line_count = int(line_count)
    except ValueError:
        console.print("[red]Line count must be an integer.[/red]")
        return

    if line_count <= 0:
        console.print("[red]Line count must be greater than zero.[/red]")
        return

    log_paths = []

    if os.path.exists(core_log_path):
        log_paths.append(("core", core_log_path))

    for skill in skills:
        log_path = os.path.join(skill["model_dir"], "training.log")

        if os.path.exists(log_path):
            log_paths.append((skill["name"], log_path))

    if not log_paths:
        console.print("[yellow]No logs found.[/yellow]")
        return

    for name, log_path in log_paths:
        with open(log_path, "r") as file:
            lines = file.readlines()

        selected_lines = lines[-line_count:]

        table = Table(title=f"Tail Log: {name}")
        table.add_column("Line")
        table.add_column("Message")

        start_line = max(1, len(lines) - len(selected_lines) + 1)

        for index, line in enumerate(selected_lines, start=start_line):
            table.add_row(str(index), line.rstrip())

        console.print(table)
