### Docker Commands

**Build**
```shell
docker build --platform linux/amd64 . -t ghcr.io/raymond-devries/qupath_tool:latest
```

**Push**
```shell
docker push ghcr.io/raymond-devries/qupath_tool:latest
```

**Run example**
```shell
docker run -v "$(pwd):/data" -d ghcr.io/raymond-devries/qupath_tool image.vsi
```

### Apptainer commands
**Build**
```shell
apptainer build qupath_base.sif qupath_base.def  
apptainer build qupath_tool.sif qupath_tool.def  
```

**Pull**
```shell
apptainer pull oras://ghcr.io/raymond-devries/qupath_tool:apptainer-latest
```

**Push**
```shell
apptainer push qupath_tool.sif oras://ghcr.io/raymond-devries/qupath_tool:apptainer-latest
```

**Run examples**

Get help
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif --help
```

**Built in segment script**

Get sbatch segment
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif sbatch-segment 10 0.5
```

Get sbatch segment for a specific series within each VSI file
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif sbatch-segment 10 0.5 --series-index 1
```

Run segment on single image
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif segment image.vsi 10 0.5
```

Run segment on single image, selecting a specific series (image) within the VSI file (0-indexed, defaults to 0)
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif segment image.vsi 10 0.5 --series-index 1
```

**Custom script**

All custom script must accept one argument: the file path of the image the script will be run on. 

Get sbatch custom script
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif sbatch-script custom_script.groovy vsi
```

Run custom script on a single image
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif script image.vsi
```