"""Module for router stats."""
import csv
import os

from rich.table import Table


def print_router_stats(
    console,
    router_model_path,
    router_train_path,
    router_config_path,
    get_routing_threshold
):
    """Render router statistics."""
    import json

    table = Table(title="Router Stats")
    table.add_column("Item")
    table.add_column("Value")

    table.add_row("router_model", router_model_path)
    table.add_row("router_model_exists", "yes" if os.path.exists(router_model_path) else "no")
    table.add_row("router_train", router_train_path)
    table.add_row("router_train_exists", "yes" if os.path.exists(router_train_path) else "no")
    table.add_row("router_config", router_config_path)
    table.add_row("routing_threshold", f"{get_routing_threshold():.2f}")

    training_rows = []

    if os.path.exists(router_train_path):
        with open(router_train_path, "r", newline="") as file:
            training_rows = list(csv.DictReader(file))

    label_counts = {}

    for row in training_rows:
        skill_name = row.get("skill_name", "")
        label_counts[skill_name] = label_counts.get(skill_name, 0) + 1

    table.add_row("training_examples", str(len(training_rows)))

    if os.path.exists(router_model_path):
        with open(router_model_path, "r") as file:
            model = json.load(file)

        table.add_row("model_labels", str(len(model.get("labels", {}))))
        table.add_row("vocabulary_size", str(len(model.get("vocabulary", []))))
    else:
        table.add_row("model_labels", "0")
        table.add_row("vocabulary_size", "0")

    console.print(table)

    if label_counts:
        label_table = Table(title="Router Label Counts")
        label_table.add_column("Skill")
        label_table.add_column("Examples")

        for skill_name in sorted(label_counts):
            label_table.add_row(skill_name, str(label_counts[skill_name]))

        console.print(label_table)
