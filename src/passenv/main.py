import os

import typer
from typer._completion_classes import completion_init
from typer._completion_shared import install as install_completion

from .completion import _detect_shell_and_rc, complete_pass_entries
from .core import PassEnv

app = typer.Typer(
    help="Load environment variables from pass entries",
    add_completion=False,  # Suppress the default --install-completion
)

# Initialize completion classes since we disabled add_completion
# This ensures Typer's custom completion handlers are registered
completion_init()


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
def install(
    shell: str = typer.Option(
        None, "--shell", help="Shell to install completion for (auto-detected if not provided)"
    ),
    skip_completion: bool = typer.Option(
        False, "--skip-completion", help="Skip shell completion installation"
    ),
) -> None:
    """Install shell function to rc file and set up completion"""

    # Detect shell using Typer's detection logic
    detected_shell, rc_file = _detect_shell_and_rc()

    typer.echo(f"🔍 Detected shell: {detected_shell}")

    # Install shell function so we can export env vars
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

    if not rc_file:
        typer.echo(f"⚠️  Unsupported shell: {detected_shell}")
        typer.echo("Add this function to your shell RC file:")
        typer.echo(shell_function)
        if not skip_completion:
            typer.echo("\nFor shell completion, try:")
            typer.echo("passenv install --shell bash  # or zsh, fish, powershell")
        return

    # Check if shell function already exists
    function_exists = False
    if os.path.exists(rc_file):
        with open(rc_file, "r") as f:
            content = f.read()
        if "passenv() {" in content:
            typer.echo(f"✅ passenv function already exists in {rc_file}")
            function_exists = True

    # Add function to rc file if it doesn't exist
    if not function_exists:
        # Ensure directory exists (important for fish config)
        os.makedirs(os.path.dirname(rc_file), exist_ok=True)

        with open(rc_file, "a") as f:
            f.write(f"\n# Added by passenv\n{shell_function}")
        typer.echo(f"✅ Shell function added to {rc_file}")

    # Install shell completion unless skipped
    if not skip_completion:
        try:
            typer.echo("🔧 Installing shell completion...")

            # Use the shell parameter for completion, fall back to detected shell
            completion_shell = shell or detected_shell
            shell_name, completion_path = install_completion(shell=completion_shell)

            typer.secho(
                f"✅ {shell_name} completion installed in {completion_path}", fg=typer.colors.GREEN
            )

        except Exception as e:
            typer.secho(f"⚠️  Could not install completion: {e}", fg=typer.colors.YELLOW)
            typer.echo("You can try installing completion for a specific shell with:")
            typer.echo("passenv install --shell bash  # or zsh, fish, powershell")

    # Final instructions
    if not function_exists or not skip_completion:
        if detected_shell == "fish":
            typer.echo(f"\n💡 Restart your shell or run 'source {rc_file}' to activate")
        else:
            typer.echo(f"\n💡 Run 'source {rc_file}' or restart your shell to activate")

    typer.secho("✨ Installation complete!", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
