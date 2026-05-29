import os
import re
import threading
import time

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn
)


class TrainingLogMonitor:

    def __init__(self, console, log_path, title):
        self.console = console
        self.log_path = log_path
        self.title = title
        self.stop_event = threading.Event()
        self.thread = None
        self.progress = None
        self.task_id = None
        self.started_at = None

    def start(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        if not os.path.exists(self.log_path):
            open(self.log_path, "a").close()

        self.started_at = time.monotonic()

        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            console=self.console
        )

        self.progress.start()
        self.task_id = self.progress.add_task(self.title, total=100)

        self.thread = threading.Thread(target=self._watch, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()

        if self.thread is not None:
            self.thread.join(timeout=1.0)

        if self.progress is not None:
            self.progress.update(self.task_id, completed=100)
            self.progress.stop()

    def _watch(self):
        position = 0

        while not self.stop_event.is_set():
            try:
                with open(self.log_path, "r") as file:
                    file.seek(position)
                    lines = file.readlines()
                    position = file.tell()

                for line in lines:
                    self._handle_line(line.strip())
            except FileNotFoundError:
                pass

            time.sleep(0.2)

    def _handle_line(self, line):
        if not line or self.progress is None:
            return

        parsed = self._parse_epoch_line(line)

        if parsed is None:
            self.progress.update(
                self.task_id,
                description=f"{self.title} - {line[-80:]}"
            )
            return

        current, total, message = parsed

        if total <= 0:
            return

        percent = current / total
        completed = int(percent * 100)

        spent_seconds = 0.0

        if self.started_at is not None:
            spent_seconds = max(0.0, time.monotonic() - self.started_at)

        eta_seconds = 0.0

        if current > 0 and total > current:
            eta_seconds = (spent_seconds / current) * (total - current)

        message = (
            f"{message}, spent={self._format_duration(spent_seconds)}, "
            f"eta={self._format_duration(eta_seconds)}"
        )

        self.progress.update(
            self.task_id,
            completed=max(0, min(100, completed)),
            description=f"{self.title} - {message}"
        )

    def _format_duration(self, seconds):
        seconds = int(max(0, seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"


    def _parse_epoch_line(self, line):
        epoch_token = None
        loss_token = None
        examples_token = None
        batch_token = None

        for token in line.split():
            if token.startswith("epoch="):
                epoch_token = token[len("epoch="):]
            elif token.startswith("loss="):
                loss_token = token[len("loss="):]
            elif token.startswith("examples="):
                examples_token = token[len("examples="):]
            elif token.startswith("batch_size="):
                batch_token = token[len("batch_size="):]

        if not epoch_token or "/" not in epoch_token:
            return None

        current_text, total_text = epoch_token.split("/", 1)

        try:
            current = int(current_text)
            total = int(total_text)
        except ValueError:
            return None

        parts = [f"epoch={current}/{total}"]

        if loss_token:
            parts.append(f"loss={loss_token}")

        if examples_token:
            parts.append(f"examples={examples_token}")

        if batch_token:
            parts.append(f"batch_size={batch_token}")

        return current, total, ", ".join(parts)
