"""Module for status."""
import os

from rich.table import Table


def print_status(
    console,
    skills,
    app_name,
    core_dir,
    router_model_path,
    router_train_path,
    skills_model_dir,
    skills_source_dir,
    router_config_path,
    get_routing_threshold,
    skills_changed
):
    """Render the status output."""
    table = Table(title="Taius Status")
    table.add_column("Item")
    table.add_column("Value")
    
    table.add_row("app", app_name)
    table.add_row("skills_loaded", str(len(skills)))
    table.add_row("core_dir", core_dir)
    table.add_row("router_model", router_model_path)
    table.add_row("router_train", router_train_path)
    table.add_row("skills_model_dir", skills_model_dir)
    table.add_row("skills_source_dir", skills_source_dir)
    table.add_row("routing_threshold", f"{get_routing_threshold():.2f}")
    table.add_row("router_config", router_config_path)
    
    table.add_row(
        "router_model_exists",
        "yes" if os.path.exists(router_model_path) else "no"
    )
    
    table.add_row(
        "router_train_exists",
        "yes" if os.path.exists(router_train_path) else "no"
    )
    
    table.add_row(
        "skills_changed",
        "yes" if skills_changed() else "no"
    )
    
    console.print(table)
