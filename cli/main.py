import inspect
import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


@app.command()
def segment(
    file: str,
    min_nuclei_area: int,
    threshold: float,
    test: bool = False,
    series_index: int = typer.Option(
        2,
        help="Index of the image series to use within the VSI file (0-indexed). Typically 2 for the full-resolution image.",
    ),
):
    os.system("/QuPath/bin/QuPath script /scripts/prefs.groovy")

    args = (
        file,
        "test" if test else "not_test",
        min_nuclei_area,
        threshold,
        series_index,
    )
    arg_str = " --args ".join(str(a) for a in args)
    print(arg_str)
    os.system(f"/QuPath/bin/QuPath script /scripts/segment.groovy --args {arg_str}")


@app.command()
def script(script_path: str, image_path: str):
    os.system("/QuPath/bin/QuPath script /scripts/prefs.groovy")
    os.system(f"/QuPath/bin/QuPath script /data/{script_path} --args {image_path}")


def _sbatch(command: str, file_type: str):
    sbatch_script_content = inspect.cleandoc(f"""
        #!/bin/bash
        ml Apptainer
        {command}
    """)

    data_files = Path("/data")
    vsi_files = list(data_files.glob(f"*.{file_type}"))
    files_arg = " ".join(file.name for file in vsi_files if file.is_file())
    all_files_script = inspect.cleandoc(f"""
        #!/bin/bash
        files="{files_arg}"

        for file in $files; do
            echo "Batching $file"
            sbatch -c 8 process.sh $file
        done
    """)

    with open("/data/process.sh", "w") as f:
        f.write(sbatch_script_content + "\n")

    with open("/data/all_files.sh", "w") as f:
        f.write(all_files_script + "\n")

    # Display table of files to be processed
    console.print(f"\n[bold]Total files:[/bold] {len(vsi_files)}")

    table = Table(title="Files to be Processed")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Filename", style="magenta")

    for idx, vsi_file in enumerate(vsi_files, 1):
        table.add_row(str(idx), vsi_file.name)

    console.print(table)

    # Display instructions
    console.print("\n[bold yellow]Next steps:[/bold yellow]")
    console.print("  1. Make all_files.sh executable:")
    console.print("     [cyan]chmod +x all_files.sh[/cyan]")
    console.print("  2. Run the batch script:")
    console.print("     [cyan]./all_files.sh[/cyan]")


@app.command()
def sbatch_segment(
    min_nuclei_area: int,
    threshold: float,
    test: bool = False,
    series_index: int = typer.Option(
        2,
        help="Index of the image series to use within the VSI file (0-indexed). Typically 2 for the full-resolution image.",
    ),
):
    console.print("[bold green]Generating scripts for sbatch[/bold green]")

    cmd_args = ["$1", str(min_nuclei_area), str(threshold)]
    if test:
        cmd_args.append("--test")
    cmd_args.extend(["--series-index", str(series_index)])

    cmd_line = " ".join(cmd_args)

    _sbatch(
        f'apptainer run --fakeroot --bind "$(pwd):/data" '
        f"qupath_tool_apptainer-latest.sif segment {cmd_line}",
        "vsi",
    )

    console.print(f"Min nuclei area: {min_nuclei_area}")
    console.print(f"Threshold: {threshold}")


@app.command()
def sbatch_script(script_path: str, file_type: str):
    _sbatch(
        f'apptainer run --fakeroot --bind "$(pwd):/data" '
        f"qupath_tool_apptainer-latest.sif script {script_path} $1",
        file_type,
    )


if __name__ == "__main__":
    app()
