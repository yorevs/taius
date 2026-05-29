import os

from taius.core.training_monitor import TrainingLogMonitor


def run_taius_loop(
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
):
    skills = load_skills()
    train_router_if_needed(skills)

    while True:
        try:
            input_data = input("Taius> ").strip()
        except KeyboardInterrupt:
            console.print("")
            console.print("[yellow]Interrupted. Exiting Taius.[/yellow]")
            break
        except EOFError:
            console.print("")
            console.print("[yellow]EOF received. Exiting Taius.[/yellow]")
            break

        if not input_data:
            continue

        if is_command(input_data):
            command_context = build_command_context(skills)
            status, skills = handle_command(input_data, command_context)

            if status == "quit":
                break

            continue

        skill, route_source, confidence = route_to_skill(input_data, skills)

        if skill is None:
            if route_source == "below-threshold":
                console.print(
                    "[red]No skill reached routing threshold.[/red] "
                    f"(confidence={confidence:.2f}, threshold={get_routing_threshold():.2f})"
                )
            else:
                console.print("[red]No skill can handle this input.[/red]")
            continue

        console.print(
            f"[bold]Selected skill:[/bold] {skill['name']} "
            f"({route_source}, confidence={confidence:.2f})"
        )

        if route_source == "router":
            selected_ok = input("Correct skill [y/n] ? ").strip().lower()

            if selected_ok != "y":
                expected_skill = input("Expected skill name? ").strip()

                if expected_skill in {"", "none", "no-skill"}:
                    try:
                        forget_router(input_data)
                        console.print("[green]Router example forgotten.[/green]")
                    except Exception as error:
                        console.print(f"[red]Router forget failed:[/red] {error}")

                    continue

                try:
                    teach_router(input_data, expected_skill, skills)
                    console.print("[green]Router updated.[/green]")
                except Exception as error:
                    console.print(f"[red]Router teach failed:[/red] {error}")

                continue

        module = skill["module"]

        if not hasattr(module, "predict"):
            console.print(f"[red]Skill has no predict():[/red] {skill['name']}")
            continue

        result = module.predict(input_data)

        console.print(f"[bold]Skill:[/bold] {skill['description'].get('id', skill['name'])}")
        console.print(f"[bold]Response:[/bold] {result}")

        if not hasattr(module, "teach"):
            continue

        correct = input("Correct [y/n] ? ").strip().lower()

        if correct == "y":
            continue

        expected_output = input("Expected output? ").strip()

        try:
            log_path = os.path.join(skill["model_dir"], "training.log")
            monitor = TrainingLogMonitor(
                console=console,
                log_path=log_path,
                title=f"Training skill: {skill['name']}"
            )

            monitor.start()

            try:
                module.teach(input_data, expected_output)
            finally:
                monitor.stop()

            console.print("[green]Skill updated.[/green]")
        except Exception as error:
            console.print(f"[red]Teach failed:[/red] {error}")
