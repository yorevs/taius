[x] 1. Add /status
Show core/router state, skill count, model paths, routing threshold, router config.

[x] 2. Add /doctor
Validate all loaded skill contracts and report missing functions/issues.

[x] 3. Add /validate-skill <skill_name>
Validate one skill only.

[x] 4. Add skill contract versioning
Require describe()["contract_version"] and validate supported versions.

[x] 5. Add skill enable/disable
Use resources/model/skills/<skill>/.disabled.

[x] 6. Add /disable-skill <skill_name>
Stop loading a skill.

[x] 7. Add /enable-skill <skill_name>
Re-enable a skill.

[x] 8. Add /remove-skill <skill_name>
Implemented as /delete-skill <skill_name>.
Safely removes skill source and model folder.

[x] 9. Add router confidence score
Show router confidence before asking confirmation.

[x] 10. Add routing threshold
If confidence is below threshold, reject routing instead of guessing.

[x] 11. Add /router-stats
Show examples per skill, vocabulary size, model state, threshold.

[x] 12. Add /skill-stats <skill_name>
Show metadata, examples, contract state, training state.

[x] 13. Add /tail-log
Partial: /skill-log <skill_name> [lines] exists.
Still missing generic /tail-log for core + skill logs.

[x] 14. Add generic skill logger
resources/model/skills/<skill>/training.log.

[x] 15. Add skill training progress monitor
    Implemented TrainingLogMonitor.
    Log-based watcher tails training.log only during training.
    math_approx_skill writes epoch/loss/examples/batch_size lines.

[x] 16. Add trainable math skills
    math_sum_skill
    math_subtract_skill
    math_multiply_skill
    math_divide_skill
    math_approx_skill

[~] 17. Migrate legacy mather logic into math skills
Legacy SelfUpdatingMathModel removed from taius.py.
Math skills still need to be implemented.

[x] 18. Add skill templates
skills/_template/skill.py.

[x] 19. Add /new-skill <name>
Generate a skeleton skill folder from template.

[x] 20. Add tests
    Smoke, skill management, router teach/forget, import/export, and command dispatch tests added.

[x] 21. Add patch validation
Dry-run patches before applying.

[ ] 22. Add launcher support for resources/launcher.bash patches safely
Optional; currently intentionally blocked.

[x] 23. Add backup snapshots
resources/model/backups/<timestamp>/.

[x] 24. Add /backup-all --snapshot
Export into timestamped snapshot folder.

[x] 25. Add /restore-all <snapshot>
Restore a specific snapshot.

[x] 26. Add README.md
Document runtime, skill contract, commands, layout, patch workflow.

[x] 27. Clean taius.py
    Legacy math removed.
    Unused import cleanup done.
    Remaining large-file cleanup belongs to item 28: split taius.py into modules.

[x] 28. Split taius.py into modules
    validation.py
    status.py
    snapshots.py
    router_runtime.py
    router_stats.py
    skill_views.py
    log_views.py
    skill_management.py
    runtime.py

[x] 29. Add /get-routing-threshold
Show current routing threshold.

[x] 30. Add /set-routing-threshold <value>
Update routing threshold in resources/model/core/router.config.json.

[x] 31. Add /skill-log <skill_name> [lines]
Show recent lines from a skill training log.

[x] 32. Add /delete-skill <skill_name>
Remove skill source and model directory.

[x] 33. Add /rename-skill <old_name> <new_name>
Rename skill source/model directories and update generated skill id.

[x] 34. Handle Ctrl+C cleanly
Exit without traceback.

[x] 35. Update /help
Include all implemented commands.

[x] 36. Improve math_approx_skill quality
    One model per operation.

[x] 37. Add README update for math skills and TrainingLogMonitor
