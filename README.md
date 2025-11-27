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

**Push**
```shell
apptainer push qupath_tool.sif oras://ghcr.io/raymond-devries/qupath_tool:apptainer-latest
```

**Run examples**
Get help
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif --help
```

Get sbatch scripts
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif sbatch-script 10 0.5
```

Run on single image
```shell
apptainer run --fakeroot --bind "$(pwd):/data" qupath_tool_apptainer-latest.sif image.vsi segment 10 0.5
```