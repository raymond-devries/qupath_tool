import os
from pathlib import Path
from textwrap import dedent

import typer

app = typer.Typer()


@app.command()
def segment(file: str, min_nuclei_area: int, threshold: float, test: bool = False):
    os.system("/QuPath/bin/QuPath script /scripts/prefs.groovy")

    args = (file, "test" if test else "not_test", min_nuclei_area, threshold)
    arg_str = " --args ".join(str(a) for a in args)
    print(arg_str)
    os.system(f"/QuPath/bin/QuPath script /scripts/segment.groovy --args {arg_str}")


@app.command()
def sbatch_script(min_nuclei_area: int, threshold: float, test: bool = False):
    print("Generating scripts for sbatch")
    test_arg = " --test" if test else ""
    sbatch_script = f"""#!/bin/bash
    ml Apptainer
    apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif segment $1 {min_nuclei_area} {threshold}{test_arg}
    """

    data_files = Path("/data")
    vsi_files = list(data_files.glob("*.vsi"))
    files_arg = " ".join(file.name for file in vsi_files if file.is_file())
    all_files_script = f"""#!/bin/bash
    files="{files_arg}"
    
    for file in $files; do
        echo "Batching $file"
        sbatch process.sh $file
    done
    """

    with open("/data/process.sh", "w") as f:
        f.write(dedent(sbatch_script))

    with open("/data/all_files.sh", "w") as f:
        f.write(dedent(all_files_script))


if __name__ == "__main__":
    app()
