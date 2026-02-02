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
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif sbatch-script 10 0.5
```

Run segment on single image
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif segment image.vsi 10 0.5
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