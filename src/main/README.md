# Taius

Taius is a generic dynamic skill runtime.

It loads Python skills from:

    skills/<skill_name>/skill.py

Runtime/model resources live under:

    resources/model/

## Layout

    taius.py
    core/
      paths.py
      skills.py
      commands.py
      router.py
      text.py
    skills/
      _template/
        skill.py
      echo_skill/
        skill.py
      sentiment_skill/
        skill.py
    resources/
      launcher.bash
      core-patcher.bash
      patches/
      backups/
      model/
        core/
        skills/

## Skill Contract

Each skill must expose:

    describe() -> dict
    configure(config: dict)
    can_handle(input_data)
    can_train() -> bool
    needs_training() -> bool
    train()
    predict(input_data)
    teach(input_data, expected_output)
    forget(input_data, expected_output=None)
    training_examples()
    export_data()
    import_data(data)

`describe()` must include:

    id
    version
    contract_version
    input_type
    output_type

Current supported contract version:

    1.0

## Runtime Commands

    /help
    /version
    /status
    /doctor
    /skills
    /reload
    /router-examples
    /router-stats
    /get-routing-threshold
    /set-routing-threshold <value>
    /export-router
    /import-router
    /backup-all
    /backup-all --snapshot
    /restore-all
    /restore-all <snapshot>
    /skill-examples <skill_name>
    /skill-stats <skill_name>
    /skill-log <skill_name> [lines]
    /tail-log [lines]
    /validate-skill <skill_name>
    /disable-skill <skill_name>
    /enable-skill <skill_name>
    /new-skill <skill_name>
    /delete-skill <skill_name>
    /rename-skill <old_name> <new_name>
    /export-skill <skill_name>
    /import-skill <skill_name>
    /teach-router <skill_name> :: <input text>
    /forget-router <input text>
    /teach-skill <skill_name> :: <input text> => <expected output>
    /forget-skill <skill_name> :: <input text>
    /quit
    /exit

## Examples

    echo hello
    sentiment I love this
    this is awesome

## Router

The router learns which skill should handle an input.

Router files:

    resources/model/core/router.csv
    resources/model/core/router.json
    resources/model/core/router.config.json

Routing threshold can be changed with:

    /set-routing-threshold 0.68

## Skill Enable / Disable

Disabled skills use marker files:

    resources/model/skills/<skill_name>/.disabled

## Logs

Skill logs:

    resources/model/skills/<skill_name>/training.log

View logs with:

    /skill-log <skill_name> [lines]
    /tail-log [lines]

## Snapshots

Snapshot backups are stored under:

    resources/model/backups/<timestamp>/

Create a snapshot:

    /backup-all --snapshot

Restore one:

    /restore-all <snapshot>

## Patch Workflow

Write patches into:

    resources/patches/*.patch

Run:

    ./resources/launcher.bash

Supported launcher patch targets:

    taius.py
    core/*.py
    skills/*/skill.py
    resources/core-patcher.bash

`resources/launcher.bash` is intentionally not patched by itself.

## Tests

Run:

    python3 -m unittest discover -s tests -p 'test_*.py'

## Math Skills

Exact deterministic math skills:

    math_sum_skill
    math_subtract_skill
    math_multiply_skill
    math_divide_skill

Approximation skill:

    math_approx_skill

`math_approx_skill` is intentionally trainable and approximate. It uses a pure-Python weighted model with one weight vector per operation. It stores training examples in:

    resources/model/skills/math_approx_skill/train.csv

and model weights in:

    resources/model/skills/math_approx_skill/model.json

## Training Log Monitor

Taius uses `TrainingLogMonitor` for long-running training.

Behavior:

    no training running -> no watcher
    training starts -> watcher tails training.log
    training ends -> watcher stops

Log paths:

    resources/model/core/training.log
    resources/model/skills/<skill_name>/training.log

Supported progress line format:

    epoch=5/200 loss=0.00177957 examples=2000000 batch_size=256

The monitor parses epoch, loss, examples, and batch_size, then updates a Rich progress bar.
