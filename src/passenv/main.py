import os

import typer

from .completion import complete_pass_entries
from .core import PassEnv

app = typer.Typer(help="Load environment variables from pass entries")


@app.command()
def load(
    pass_path: str = typer.Argument(
        ..., help="Pass entry path to load", autocompletion=complete_pass_entries
    )
) -> None:
    """Load secrets to the environment"""
    try:
        passenv = PassEnv()
        output = passenv.load(pass_path)
        print(output)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def unload() -> None:
    """Unload all secrets"""
    try:
        passenv = PassEnv()
        output = passenv.unload()
        print(output)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def status() -> None:
    """Show status of loaded secrets"""
    try:
        passenv = PassEnv()
        status_msg = passenv.status()
        typer.echo(status_msg)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def list() -> None:
    """List all secrets"""
    try:
        passenv = PassEnv()
        entries = passenv.list_entries()
        if entries:
            for entry in entries:
                typer.echo(entry)
        else:
            typer.echo("No pass entries found")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def install() -> None:
    """Install shell function to rc file"""
    shell_function = """
passenv() {
    case "$1" in
        load|unload)
            eval $(command passenv "$@")
            ;;
        *)
            command passenv "$@"
            ;;
    esac
}
"""

    # Detect shell
    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell == "bash":
        rc_file = os.path.expanduser("~/.bashrc")
        shell_function = shell_function.replace("zsh_source", "bash_source")
    elif shell == "zsh":
        rc_file = os.path.expanduser("~/.zshrc")
    else:
        typer.echo("Add this function to your shell RC file:")
        typer.echo(shell_function)
        return

    # Check if already exists
    if os.path.exists(rc_file):
        with open(rc_file, "r") as f:
            content = f.read()
        if "passenv() {" in content:
            typer.echo(f"passenv function already exists in {rc_file}")
            return

    # Add function to rc file
    with open(rc_file, "a") as f:
        f.write(f"\n# Added by passenv\n{shell_function}")

    typer.echo(f"Shell function added to {rc_file}")
    typer.echo(f"Run 'source {rc_file}' or restart your shell to activate")


if __name__ == "__main__":
    app()
