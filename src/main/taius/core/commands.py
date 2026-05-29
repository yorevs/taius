"""Module for commands."""
def find_skill(skill_name, skills):
  """Return the matching skill from the provided list."""
  for skill in skills:
    if skill["name"] == skill_name:
      return skill

  return None


def is_command(input_data):
  """Return whether the input is a command."""
  return input_data.startswith("/")


def handle_command(input_data, context):
  """Handle a slash command and return the next state."""
  console = context["console"]
  skills = context["skills"]

  if input_data in {"/quit", "/exit"}:
    return "quit", skills

  if input_data == "/help":
    context["print_help"]()
    return "handled", skills

  if input_data == "/version":
    context["print_version_info"](skills)
    return "handled", skills

  if input_data == "/status":
    context["print_status"](skills)
    return "handled", skills

  if input_data == "/get-routing-threshold":
    context["print_routing_threshold"]()
    return "handled", skills

  if input_data == "/set-routing-threshold":
    console.print("[red]Usage:[/red] /set-routing-threshold <value>")
    return "handled", skills

  if input_data.startswith("/set-routing-threshold "):
    value = input_data[len("/set-routing-threshold "):].strip()

    if not value:
      console.print("[red]Usage:[/red] /set-routing-threshold <value>")
      return "handled", skills

    try:
      threshold = context["set_routing_threshold"](value)
      console.print(f"[green]Routing threshold updated:[/green] {threshold:.2f}")
    except Exception as error:
      console.print(f"[red]Set routing threshold failed:[/red] {error}")

    return "handled", skills

  if input_data == "/doctor":
    context["print_doctor"](skills)
    return "handled", skills

  if input_data == "/rename-skill":
    console.print("[red]Usage:[/red] /rename-skill <old_name> <new_name>")
    return "handled", skills

  if input_data.startswith("/rename-skill "):
    payload = input_data[len("/rename-skill "):].strip()
    parts = payload.split()

    if len(parts) != 2:
      console.print("[red]Usage:[/red] /rename-skill <old_name> <new_name>")
      return "handled", skills

    try:
      result = context["rename_skill"](parts[0], parts[1])
      console.print(f"[green]Skill renamed:[/green] {parts[0]} -> {parts[1]}")
      console.print(f"[cyan]Source:[/cyan] {result['source_dir']}")
      console.print(f"[cyan]Model:[/cyan] {result['model_dir']}")
      skills = context["reload_skills"]()
    except Exception as error:
      console.print(f"[red]Rename skill failed:[/red] {error}")

    return "handled", skills

  if input_data == "/delete-skill":
    console.print("[red]Usage:[/red] /delete-skill <skill_name>")
    return "handled", skills

  if input_data.startswith("/delete-skill "):
    skill_name = input_data[len("/delete-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /delete-skill <skill_name>")
      return "handled", skills

    try:
      removed_paths = context["delete_skill"](skill_name)

      for removed_path in removed_paths:
        console.print(f"[green]Removed:[/green] {removed_path}")

      skills = context["reload_skills"]()
    except Exception as error:
      console.print(f"[red]Delete skill failed:[/red] {error}")

    return "handled", skills

  if input_data == "/new-skill":
    console.print("[red]Usage:[/red] /new-skill <skill_name>")
    return "handled", skills

  if input_data.startswith("/new-skill "):
    skill_name = input_data[len("/new-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /new-skill <skill_name>")
      return "handled", skills

    try:
      skill_path = context["create_new_skill"](skill_name)
      console.print(f"[green]Skill created:[/green] {skill_path}")
      skills = context["reload_skills"]()
    except Exception as error:
      console.print(f"[red]New skill failed:[/red] {error}")

    return "handled", skills

  if input_data == "/disable-skill":
    console.print("[red]Usage:[/red] /disable-skill <skill_name>")
    return "handled", skills

  if input_data.startswith("/disable-skill "):
    skill_name = input_data[len("/disable-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /disable-skill <skill_name>")
      return "handled", skills

    try:
      disabled_path = context["disable_skill"](skill_name, skills)
      console.print(f"[green]Skill disabled:[/green] {skill_name}")
      console.print(f"[cyan]Marker:[/cyan] {disabled_path}")
      skills = context["reload_skills"]()
    except Exception as error:
      console.print(f"[red]Disable skill failed:[/red] {error}")

    return "handled", skills

  if input_data == "/enable-skill":
    console.print("[red]Usage:[/red] /enable-skill <skill_name>")
    return "handled", skills

  if input_data.startswith("/enable-skill "):
    skill_name = input_data[len("/enable-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /enable-skill <skill_name>")
      return "handled", skills

    try:
      disabled_path = context["enable_skill"](skill_name)
      console.print(f"[green]Skill enabled:[/green] {skill_name}")
      console.print(f"[cyan]Marker removed:[/cyan] {disabled_path}")
      skills = context["reload_skills"]()
    except Exception as error:
      console.print(f"[red]Enable skill failed:[/red] {error}")

    return "handled", skills

  if input_data == "/validate-skill":
    console.print("[red]Usage:[/red] /validate-skill <skill_name>")
    return "handled", skills

  if input_data.startswith("/validate-skill "):
    skill_name = input_data[len("/validate-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /validate-skill <skill_name>")
      return "handled", skills

    context["print_validate_skill"](skill_name, skills)
    return "handled", skills

  if input_data == "/skills":
    context["print_loaded_skills"](skills)
    return "handled", skills

  if input_data == "/reload":
    skills = context["reload_skills"]()
    return "handled", skills

  if input_data == "/router-examples":
    context["print_router_examples"]()
    return "handled", skills

  if input_data == "/router-stats":
    context["print_router_stats"]()
    return "handled", skills

  if input_data == "/export-router":
    try:
      export_path = context["export_router"]()
      console.print(f"[green]Router exported:[/green] {export_path}")
    except Exception as error:
      console.print(f"[red]Router export failed:[/red] {error}")
    return "handled", skills

  if input_data == "/import-router":
    try:
      import_path = context["import_router"]()
      console.print(f"[green]Router imported:[/green] {import_path}")
    except Exception as error:
      console.print(f"[red]Router import failed:[/red] {error}")
    return "handled", skills

  if input_data == "/backup-all --snapshot":
    try:
      snapshot_dir, exported = context["backup_all_snapshot"](skills)
      console.print(f"[green]Snapshot created:[/green] {snapshot_dir}")

      for path in exported:
        console.print(f"[green]Exported:[/green] {path}")
    except Exception as error:
      console.print(f"[red]Snapshot backup failed:[/red] {error}")
    return "handled", skills

  if input_data == "/backup-all":
    try:
      exported = context["backup_all"](skills)

      for path in exported:
        console.print(f"[green]Exported:[/green] {path}")
    except Exception as error:
      console.print(f"[red]Backup failed:[/red] {error}")
    return "handled", skills

  if input_data.startswith("/restore-all "):
    snapshot_name = input_data[len("/restore-all "):].strip()

    if not snapshot_name:
      console.print("[red]Usage:[/red] /restore-all <snapshot>")
      return "handled", skills

    try:
      snapshot_dir, restored = context["restore_all_snapshot"](snapshot_name, skills)
      console.print(f"[green]Snapshot restored:[/green] {snapshot_dir}")

      for path in restored:
        console.print(f"[green]Restored:[/green] {path}")

      skills = context["reload_skills"]()
    except Exception as error:
      console.print(f"[red]Snapshot restore failed:[/red] {error}")

    return "handled", skills

  if input_data == "/list-snapshots":
    context["print_snapshot_list"]()
    return "handled", skills

  if input_data == "/restore-all":
    try:
      imported = context["restore_all"](skills)

      for path in imported:
        console.print(f"[green]Imported:[/green] {path}")
    except Exception as error:
      console.print(f"[red]Restore failed:[/red] {error}")
    return "handled", skills

  if input_data == "/tail-log":
    context["print_tail_log"](skills)
    return "handled", skills

  if input_data.startswith("/tail-log "):
    line_count = input_data[len("/tail-log "):].strip()

    if not line_count:
      line_count = 20

    context["print_tail_log"](skills, line_count)
    return "handled", skills

  if input_data == "/skill-log":
    console.print("[red]Usage:[/red] /skill-log <skill_name> [lines]")
    return "handled", skills

  if input_data.startswith("/skill-log "):
    payload = input_data[len("/skill-log "):].strip()
    parts = payload.split()

    if not parts:
      console.print("[red]Usage:[/red] /skill-log <skill_name> [lines]")
      return "handled", skills

    skill_name = parts[0]
    line_count = parts[1] if len(parts) > 1 else 20

    context["print_skill_log"](skill_name, skills, line_count)
    return "handled", skills

  if input_data == "/skill-stats":
    console.print("[red]Usage:[/red] /skill-stats <skill_name>")
    return "handled", skills

  if input_data.startswith("/skill-stats "):
    skill_name = input_data[len("/skill-stats "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /skill-stats <skill_name>")
      return "handled", skills

    context["print_skill_stats"](skill_name, skills)
    return "handled", skills

  if input_data == "/skill-examples":
    console.print("[red]Usage:[/red] /skill-examples <skill_name>")
    return "handled", skills

  if input_data.startswith("/skill-examples "):
    skill_name = input_data[len("/skill-examples "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /skill-examples <skill_name>")
      return "handled", skills

    context["print_skill_examples"](skill_name, skills)
    return "handled", skills

  if input_data.startswith("/export-skill "):
    skill_name = input_data[len("/export-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /export-skill <skill_name>")
      return "handled", skills

    try:
      export_path = context["export_skill"](skill_name, skills)
      console.print(f"[green]Skill exported:[/green] {export_path}")
    except Exception as error:
      console.print(f"[red]Skill export failed:[/red] {error}")

    return "handled", skills

  if input_data.startswith("/import-skill "):
    skill_name = input_data[len("/import-skill "):].strip()

    if not skill_name:
      console.print("[red]Usage:[/red] /import-skill <skill_name>")
      return "handled", skills

    try:
      import_path = context["import_skill"](skill_name, skills)
      console.print(f"[green]Skill imported:[/green] {import_path}")
    except Exception as error:
      console.print(f"[red]Skill import failed:[/red] {error}")

    return "handled", skills

  if input_data.startswith("/teach-router "):
    payload = input_data[len("/teach-router "):].strip()

    if " :: " not in payload:
      console.print("[red]Usage:[/red] /teach-router <skill_name> :: <input text>")
      return "handled", skills

    expected_skill, router_input = payload.split(" :: ", 1)

    try:
      context["teach_router"](router_input.strip(), expected_skill.strip(), skills)
      console.print("[green]Router updated.[/green]")
    except Exception as error:
      console.print(f"[red]Router teach failed:[/red] {error}")

    return "handled", skills

  if input_data.startswith("/forget-router "):
    router_input = input_data[len("/forget-router "):].strip()

    if not router_input:
      console.print("[red]Usage:[/red] /forget-router <input text>")
      return "handled", skills

    try:
      context["forget_router"](router_input)
      console.print("[green]Router example forgotten.[/green]")
    except Exception as error:
      console.print(f"[red]Router forget failed:[/red] {error}")

    return "handled", skills

  if input_data.startswith("/teach-skill "):
    payload = input_data[len("/teach-skill "):].strip()

    if " :: " not in payload or " => " not in payload:
      console.print("[red]Usage:[/red] /teach-skill <skill_name> :: <input text> => <expected output>")
      return "handled", skills

    skill_name, rest = payload.split(" :: ", 1)
    skill_input, expected_output = rest.split(" => ", 1)

    target_skill = find_skill(skill_name.strip(), skills)

    if target_skill is None:
      console.print(f"[red]Unknown skill:[/red] {skill_name.strip()}")
      return "handled", skills

    module = target_skill["module"]

    if not hasattr(module, "teach"):
      console.print(f"[red]Skill has no teach():[/red] {skill_name.strip()}")
      return "handled", skills

    try:
      module.teach(skill_input.strip(), expected_output.strip())

      if "log_skill_event" in context:
        context["log_skill_event"](
          target_skill,
          f"command teach input={skill_input.strip()!r} expected={expected_output.strip()!r}"
        )

      console.print("[green]Skill updated.[/green]")
    except Exception as error:
      console.print(f"[red]Skill teach failed:[/red] {error}")

    return "handled", skills

  if input_data.startswith("/forget-skill "):
    payload = input_data[len("/forget-skill "):].strip()

    if " :: " not in payload:
      console.print("[red]Usage:[/red] /forget-skill <skill_name> :: <input text>")
      return "handled", skills

    skill_name, skill_input = payload.split(" :: ", 1)
    target_skill = find_skill(skill_name.strip(), skills)

    if target_skill is None:
      console.print(f"[red]Unknown skill:[/red] {skill_name.strip()}")
      return "handled", skills

    module = target_skill["module"]

    if not hasattr(module, "forget"):
      console.print(f"[red]Skill has no forget():[/red] {skill_name.strip()}")
      return "handled", skills

    try:
      module.forget(skill_input.strip())

      if "log_skill_event" in context:
        context["log_skill_event"](
          target_skill,
          f"command forget input={skill_input.strip()!r}"
        )

      console.print("[green]Skill example forgotten.[/green]")
    except Exception as error:
      console.print(f"[red]Skill forget failed:[/red] {error}")

    return "handled", skills

  console.print(f"[red]Unknown command:[/red] {input_data}")
  return "handled", skills
