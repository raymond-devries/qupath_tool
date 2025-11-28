import inspect
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def segment(file: str, min_nuclei_area: int, threshold: float, test: bool = False):
    os.system("/QuPath/bin/QuPath script /scripts/prefs.groovy")

    args = (file, "test" if test else "not_test", min_nuclei_area, threshold)
    arg_str = " --args ".join(str(a) for a in args)
    print(arg_str)
    os.system(f"/QuPath/bin/QuPath script /scripts/segment.groovy --args {arg_str}")


@app.command()
def sbatch_script(min_nuclei_area: int, threshold: float, test: bool = False):
    console.print("[bold green]Generating scripts for sbatch[/bold green]")
    test_arg = " --test" if test else ""
    sbatch_script_content = inspect.cleandoc(f"""
        #!/bin/bash
        ml Apptainer
        apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif segment $1 {min_nuclei_area} {threshold}{test_arg}
    """)

    data_files = Path("/data")
    vsi_files = list(data_files.glob("*.vsi"))
    files_arg = " ".join(file.name for file in vsi_files if file.is_file())
    all_files_script = inspect.cleandoc(f"""
        #!/bin/bash
        files="{files_arg}"

        for file in $files; do
            echo "Batching $file"
            sbatch process.sh $file
        done
    """)

    with open("/data/process.sh", "w") as f:
        f.write(sbatch_script_content + "\n")

    with open("/data/all_files.sh", "w") as f:
        f.write(all_files_script + "\n")

    # Display table of files to be processed
    table = Table(title="Files to be Processed")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Filename", style="magenta")

    for idx, vsi_file in enumerate(vsi_files, 1):
        table.add_row(str(idx), vsi_file.name)

    console.print(table)
    console.print(f"\n[bold]Total files:[/bold] {len(vsi_files)}")

    # Display instructions
    console.print("\n[bold yellow]Next steps:[/bold yellow]")
    console.print("  1. Make the script executable:")
    console.print("     [cyan]chmod +x all_files.sh[/cyan]")
    console.print("  2. Run the batch script:")
    console.print("     [cyan]./all_files.sh[/cyan]")


if __name__ == "__main__":
    app()
