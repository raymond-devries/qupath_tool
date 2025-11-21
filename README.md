### Commands

Build
```shell
docker build --platform linux/amd64 . -t ghcr.io/raymond-devries/qupath_tool:latest
```

Push
```shell
docker push ghcr.io/raymond-devries/qupath_tool:lates
```

Run example:
```shell
docker run -v "$(pwd):/data" -d ghcr.io/raymond-devries/qupath_tool SR25-1525_20251031_01.vsi
```