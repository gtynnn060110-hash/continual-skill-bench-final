from importlib.metadata import version
from typing import Optional

import typer
from typer import Typer

from harbor.cli.jobs import jobs_app, start
from harbor.cli.tasks import tasks_app
from harbor.cli.trials import trials_app


def version_callback(value: bool) -> None:
    if value:
        print(version("harbor"))
        raise typer.Exit()


app = Typer(no_args_is_help=True)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True
    ),
) -> None:
    pass


app.add_typer(tasks_app, name="tasks", help="Manage tasks.")
app.add_typer(jobs_app, name="jobs", help="Manage jobs.")
app.add_typer(trials_app, name="trials", help="Manage trials.")

app.command(name="run", help="Start a job. Alias for `harbor jobs start`.")(start)

if __name__ == "__main__":
    app()
